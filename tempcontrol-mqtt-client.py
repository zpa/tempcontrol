# MQTT client for tempcontrol
#
# the client subscribes to messages on the following topics:
# (1) Shelly H&T's temperature measurement announcements
# (2) tempcontrol's web server incoming command announcements
# the client publishes messages on the topics directing the Shelly1 relays

from enum import Enum
import database as db
import statemachine as sm
import paho.mqtt.client as mqtt
import logging
import sqlite3
from config import SHELLY_HT_TOPIC, TEMPCONTROL_TOPIC, SHELLY_RELAY_TOPICS

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logging.debug(f'connected with result code {rc}')

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(SHELLY_HT_TOPIC, 2)
    logging.debug(f'subscribed to Shelly H&T topic: {SHELLY_HT_TOPIC}')

    client.subscribe(TEMPCONTROL_TOPIC, 2)
    logging.debug(f'subscribed to tempcontrol topic: {TEMPCONTROL_TOPIC}')

def publish_message(client, msg):
    logging.debug(f'publish_message called with msg: {msg}')
    if msg != None:
        for topic in SHELLY_RELAY_TOPICS:
            client.publish(topic, payload=msg.str, qos=2, retain=True)
    
# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    logging.debug(f'mqtt message received on topic {msg.topic}, payload: {msg.payload}')

    conn = db.get_connection()
    (current_state, param) = db.get_current_state(conn)
    most_recent_temp = db.get_most_recent_temp(conn)
    conn.close()

    temp_target = param
    
    if msg.topic == SHELLY_HT_TOPIC:
        try:
            temp_measured = float(msg.payload)
            temp = sm.Temp.get(temp_measured, temp_target)
            (new_state, message) = sm.transition(sm.Event.TEMP, current_state, temp)
            logging.debug(f'state transition: {(sm.Event.TEMP, current_state, temp)} => {(new_state, message)}')
            publish_message(client, message)
        except ValueError:
            logging.error(f'could not interpret {msg.payload} in msg.payload as a float')
        except KeyError:
            logging.error(f'state transition failed for {(event, current_state, temp)}')
            
    elif msg.topic == TEMPCONTROL_TOPIC:
        temp_measured = most_recent_temp
        try:
            (event, temp_from_message) = sm.Event.parse_message(msg.payload.decode('utf-8'))
            if temp_from_message != None:
                temp_target = temp_from_message

            temp = sm.Temp.get(temp_measured, temp_target)
            (new_state, message) = sm.transition(event, current_state, temp)
            logging.debug(f'state transition: {(event, current_state, temp)} => {(new_state, message)}')
            publish_message(client, message)                
        except ValueError:
            logging.error(f'could not interpret {msg.payload} in msg.payload as valid event')
        except KeyError:
            logging.error(f'state transition failed for {(event, current_state, temp)}')
    else:
        pass

def main():
    logging.basicConfig(level=logging.DEBUG)
    logging.info("tempcontrol mqtt client started")

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_forever()
    
if __name__ == '__main__':
    main()

