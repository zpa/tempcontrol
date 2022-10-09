import sqlite3
from flask import Flask, render_template, request
from markupsafe import escape
from datetime import datetime
from enum import Enum
import paho.mqtt.publish as mqtt_publish
import database as db
import statemachine as sm
import sms

app = Flask(__name__)

@app.route('/')
@app.route('/index/')
def index():
    return "<html>tempcontrol</html>"

@app.route('/measurement/')
def measurement():
    hum = request.args.get('hum', type = int)
    temp = request.args.get('temp', type = float)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = db.get_connection()
    db.add_measurement(conn, timestamp, temp, hum)
    conn.close()
    return f'<html>@{timestamp}: {temp},{hum}</html>'

def send_message(receiver, message_body):
    print(f'Message to: {receiver}')
    print(f'Message: {message_body}')
    sms.send_sms(receiver, message_body)

class Message(Enum):
    UNKNOWN = 1
    INFO = 2
    HEAT = 3
    TURN_OFF = 4

def parse_message(message_body):
    if message_body[0:4] == 'INFO':
        return (Message.INFO, None)
    elif message_body[0:8] == 'TURN OFF':
        return (Message.TURN_OFF, None)
    elif message_body[0:4] == 'HEAT':
        try:
            temp = int(message_body[4:])
            return (Message.HEAT, temp)
        except ValueError:
            return (Message.UNKNOWN, None)
    return (Message.UNKNOWN, None)

def set_current_state(conn, timestamp, state, param, requester):
    response = 'OK'
    try:
        payload = sm.Event.create_from(state).str(param)
        mqtt_publish.single("tempcontrol/command", payload = payload, qos = 2, retain = True, hostname = "localhost", port = 1883, keepalive = 60)
    except ValueError as err:
        response = f'Error: {err}'
    except:
        response = 'Error: failed to publish mqtt message'

    db.set_current_state(conn, timestamp, state, param, requester)
    return response

def get_new_state(current_state, message):
    if message == Message.UNKNOWN or message == Message.INFO:
        return current_state
    elif message == Message.HEAT:
        return sm.State.ON
    elif message == Message.TURN_OFF:
        return sm.State.OFF
    else:
        return current_state

def get_status_info(conn):
    (state, param) = db.get_current_state(conn)
    response = ''
    if state == sm.State.OFF:
        response += 'System OFF'
    else:
        response += 'Heating ON'

    temp = db.get_most_recent_temp(conn)
    response += f', current temp {temp}C'

    if state == sm.State.ON:
        response += f', target temp {param}C'
        
    return response

def process_state_change(conn, msg, param, requester):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    (current_state, current_param) = db.get_current_state(conn)
    new_state = get_new_state(current_state, msg)
    error = set_current_state(conn, timestamp, new_state, param, requester)
    return error
    
@app.route('/turnoff/')
def turnoff():
    conn = db.get_connection()
    error = process_state_change(conn, Message.TURN_OFF, None, f'{request.user_agent} at {request.remote_addr}')
    s = get_status_info(conn)
    conn.close()
    return f'<html>{s}, {error}</html>'

@app.route('/info/')
def info():
    conn = db.get_connection()
    s = get_status_info(conn)
    conn.close()
    return f'<html>{s}</html>'

@app.route('/heat/<temperature>')
def heat(temperature):
    conn = db.get_connection()
    error = 'OK'
    try:
        error = process_state_change(conn, Message.HEAT, int(temperature), f'{request.user_agent} at {request.remote_addr}')
    except ValueError:
        error = "Error: failed to parse temperature as integer"        

    s = get_status_info(conn)
    conn.close()
    return f'<html>{s}, {error}</html>'

@app.route('/message/')
def message():
    ADMIN = '+36203732951'

    sender = request.args.get('sender', str)
    message_body = request.args.get('message_body', str)
    
    (msg, param) = parse_message(message_body)
    conn = db.get_connection()
    error = 'OK'
    
    if msg == Message.UNKNOWN:
        send_message(ADMIN, f'Failed to parse message received from {sender}')
        send_message(ADMIN, message_body)
        s = get_status_info(conn)
    elif msg == Message.INFO:
        s = get_status_info(conn)
        send_message(sender, s + ', ' + error)
    else:
        error = process_state_change(conn, msg, param, sender)
        s = get_status_info(conn)
        send_message(sender, s + ', ' + error)

    conn.close()

    return f'<html>{s}, {error}</html>'


