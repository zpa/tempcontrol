# MQTT client for tempcontrol
#
# the client subscribes to messages on the following topics:
# (1) Shelly H&T's temperature measurement announcements
# (2) tempcontrol's web server incoming command announcements
# the client publishes messages on the topics directing the Shelly1 relays

from enum import Enum
from .database import *
from .statemachine import Event, Temp, transition, BoilerEvent, boiler_transition
import paho.mqtt.client as mqtt
import logging
import sqlite3
from .config import SHELLY_HT_TOPIC, TEMPCONTROL_TOPIC, SHELLY_RELAY_TOPICS, BOILERCONTROL_TOPIC, SHELLY_BOILER_RELAY_TOPIC

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.debug(f'connected with result code {rc}')

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SHELLY_HT_TOPIC, 2)
    logging.debug(f'subscribed to Shelly H&T topic: {SHELLY_HT_TOPIC}')

    client.subscribe(TEMPCONTROL_TOPIC, 2)
    logging.debug(f'subscribed to tempcontrol topic: {TEMPCONTROL_TOPIC}')

    client.subscribe(BOILERCONTROL_TOPIC, 2)
    logging.debug(f'subscribed to tempcontrol topic: {BOILERCONTROL_TOPIC}')

def publish_message(client, msg):
    logging.debug(f'publish_message called with msg: {msg}')
    if msg != None:
        for topic in SHELLY_RELAY_TOPICS:
            client.publish(topic, payload=msg.str, qos=2, retain=True)

def publish_boiler_message(client, msg):
    logging.debug(f'publish_boiler_message called with msg: {msg}')
    if msg != None:
        for topic in SHELLY_BOILER_RELAY_TOPIC:
            client.publish(topic, payload=msg.str, qos=2, retain=True)

def load_temp_info():
    conn = get_connection()
    (current_state, param) = load_current_state(conn)
    most_recent_temp = load_most_recent_temp(conn)
    conn.close()
    return (current_state, param, most_recent_temp)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logging.debug(f'mqtt message received on topic {msg.topic}, payload: {msg.payload}')
    
    if msg.topic == SHELLY_HT_TOPIC:
        (current_state, temp_target, most_recent_temp) = load_temp_info()
        try:
            temp_measured = float(msg.payload)
            temp = Temp.get(temp_measured, temp_target)
            (new_state, message) = transition(Event.TEMP, current_state, temp)
            logging.debug(f'state transition: {(Event.TEMP, current_state, temp)} => {(new_state, message)}')
            publish_message(client, message)
        except ValueError:
            logging.error(f'could not interpret {msg.payload} in msg.payload as a float')
        except KeyError:
            logging.error(f'state transition failed for {(event, current_state, temp)}')
            
    elif msg.topic == TEMPCONTROL_TOPIC:
        (current_state, temp_target, most_recent_temp) = load_temp_info()
        temp_measured = most_recent_temp
        try:
            (event, temp_from_message) = Event.parse_message(msg.payload.decode('utf-8'))
            if temp_from_message != None:
                temp_target = temp_from_message

            temp = Temp.get(temp_measured, temp_target)
            (new_state, message) = transition(event, current_state, temp)
            logging.debug(f'state transition: {(event, current_state, temp)} => {(new_state, message)}')
            publish_message(client, message)                
        except ValueError:
            logging.error(f'could not interpret {msg.payload} in msg.payload as valid event')
        except KeyError:
            logging.error(f'state transition failed for {(event, current_state, temp)}')
    
    elif msg.topic == BOILERCONTROL_TOPIC:
        conn = get_connection()
        current_state = load_current_boiler_state(conn)
        conn.close()
        try:
            event = BoilerEvent.parse_message(msg.payload.decode('utf-8'))
            (new_state, message) = boiler_transition(event, current_state)
            logging.debug(f'boiler state transition: {(event, current_state)} => {(new_state, message)}')
            publish_boiler_message(client, message)                
        except ValueError:
            logging.error(f'could not interpret {msg.payload} in msg.payload as valid boiler event')
        except KeyError:
            logging.error(f'boiler state transition failed for {(event, current_state)}')

    else:
        pass

def main_mqtt_loop():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("tempcontrol mqtt client started")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_forever()
    
