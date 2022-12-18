import sqlite3
from flask import Flask, render_template, request
from markupsafe import escape
from datetime import datetime, timedelta
from enum import Enum
import paho.mqtt.publish as mqtt_publish
import base64
from io import BytesIO
from matplotlib.figure import Figure
import matplotlib.dates as mdates

from tempcontrol import app

from .database import *
from .statemachine import State, Event
from .sms import send_sms
from .config import ADMIN, HEALTHCHECK_DELAY, TIMESTAMP_FORMAT

@app.route('/')
@app.route('/index/')
def index():
    MAJOR = 1
    MINOR = 2
    RELEASE_DATE = '2022-12-18'

    conn = get_connection()
    starttime = (datetime.now() - timedelta(days = 30)).strftime(TIMESTAMP_FORMAT)
    df = load_temp_after(conn, starttime)
    conn.close()

    df['timestamp'] = df['timestamp'].astype('datetime64')
    df.set_index('timestamp')

    fig = Figure()
    axs = fig.subplots(nrows=3, ncols=1)
    fig.set_figheight(7)
    fig.set_figwidth(5)
    # 30-day plot
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    axs[0].xaxis.set_major_locator(locator)
    axs[0].xaxis.set_major_formatter(formatter)
    axs[0].plot(df['timestamp'], df['temperature'])
    axs[0].set(xlabel = 'date', ylabel = 'temperature [C]')
    axs[0].set_title('Last 30 days')
    # 7-day plot
    df = df.loc[df['timestamp'] >= datetime.now() - timedelta(days=7)]
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    axs[1].xaxis.set_major_locator(locator)
    axs[1].xaxis.set_major_formatter(formatter)
    axs[1].plot(df['timestamp'], df['temperature'])
    axs[1].set(xlabel = 'date', ylabel = 'temperature [C]')
    axs[1].set_title('Last 7 days')
    # 1-day plot
    df = df.loc[df['timestamp'] >= datetime.now() - timedelta(days=1)]    
    locator = mdates.AutoDateLocator(minticks=3, maxticks=7)
    formatter = mdates.ConciseDateFormatter(locator)
    axs[2].xaxis.set_major_locator(locator)
    axs[2].xaxis.set_major_formatter(formatter)
    axs[2].plot(df['timestamp'], df['temperature'])
    axs[2].set(xlabel = 'date', ylabel = 'temperature [C]')
    axs[2].set_title('Last 24 hours')

    fig.subplots_adjust(hspace=0.75)
    # save figure to a temporary buffer
    buf = BytesIO()
    fig.savefig(buf, format="png")
    # embed the result in the html output
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f'<html><p>tempcontrol v{MAJOR}.{MINOR} created @{RELEASE_DATE}</p><p><img src="data:image/png;base64,{data}"/></p></html>'

@app.route('/measurement/')
def measurement():
    hum = request.args.get('hum', type = int)
    temp = request.args.get('temp', type = float)
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    
    conn = get_connection()
    save_measurement(conn, timestamp, temp, hum)
    conn.close()
    return f'<html>@{timestamp}: {temp},{hum}</html>'

def send_message(receiver, message_body, serial = 1):
    print(f'Message to: {receiver}')
    print(f'Message: {message_body}')
    send_sms(receiver, message_body, serial)

class Message(Enum):
    UNKNOWN = 1
    INFO = 2
    HEAT = 3
    TURN_OFF = 4
    MANUAL_MODE = 5

def parse_message(message_body):
    if message_body[0:4].upper() == 'INFO':
        return (Message.INFO, None)
    elif message_body[0:8].upper() == 'TURN OFF':
        return (Message.TURN_OFF, None)
    elif message_body[0:4].upper() == 'HEAT':
        try:
            temp = int(message_body[4:])
            return (Message.HEAT, temp)
        except ValueError:
            return (Message.UNKNOWN, None)
    elif message_body[0:11].upper() == 'MANUAL MODE':
        return (Message.MANUAL_MODE, None)
    return (Message.UNKNOWN, None)

def set_current_state(conn, timestamp, state, param, requester):
    response = 'status set OK'
    try:
        payload = Event.create_from(state).str_with(param)
        mqtt_publish.single("tempcontrol/command", payload = payload, qos = 2, retain = True, hostname = "localhost", port = 1883, keepalive = 60)
    except ValueError as err:
        response = f'error: {err}'
    except:
        response = 'error: failed to publish mqtt msg'

    save_current_state(conn, timestamp, state, param, requester)
    return response

def get_new_state(current_state, message):
    if message == Message.UNKNOWN or message == Message.INFO:
        return current_state
    elif message == Message.HEAT:
        return State.ON
    elif message == Message.TURN_OFF:
        return State.OFF
    elif message == Message.MANUAL_MODE:
        return State.MANUAL
    else:
        return current_state

# status message format:
# System OFF, current XXC, target NA, HC at <timestamp>: {OK | NO TEMP SINCE <timestamp> | MAX TEMP XXC SINCE <timestamp>}
# Heating ON, current XXC, target XXC, HC at <timestamp>: {OK | NO TEMP SINCE <timestamp> | MAX TEMP XXC SINCE <timestamp>}
# Manual mode, current XXC, target NA, HC at <timestamp>: {OK | NO TEMP SINCE <timestamp> | MAX TEMP XXC SINCE <timestamp>}
def get_status_info(conn):
    (state, param) = load_current_state(conn)
    response = ''

    # system state
    if state == State.OFF:
        response += 'System OFF'
    elif state == State.ON:
        response += 'Heating ON'
    else:
        response += 'MANUAL mode'

    # current temp
    temp = load_most_recent_temp(conn)
    response += f', current {temp}C'

    # target temp
    if param == None:
        param = 'N/A'
        
    response += f', target {param}'

    if state == State.ON:
        response += 'C'

    # healthcheck status
    (timestamp, result) = load_last_healthcheck(conn)
    response += f', HC({timestamp}): {result}'
    
    return response

def process_state_change(conn, msg, param, requester):
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    (current_state, current_param) = load_current_state(conn)
    new_state = get_new_state(current_state, msg)
    error = set_current_state(conn, timestamp, new_state, param, requester)
    return error

@app.route('/manualmode/')
def manualmode():
    conn = get_connection()
    error = process_state_change(conn, Message.MANUAL_MODE, None, f'{request.user_agent} at {request.remote_addr}')
    s = get_status_info(conn)
    conn.close()
    return f'<html>{s}, {error}</html>'

@app.route('/turnoff/')
def turnoff():
    conn = get_connection()
    error = process_state_change(conn, Message.TURN_OFF, None, f'{request.user_agent} at {request.remote_addr}')
    s = get_status_info(conn)
    conn.close()
    return f'<html>{s}, {error}</html>'

@app.route('/info/')
def info():
    conn = get_connection()
    s = get_status_info(conn)
    conn.close()
    return f'<html>{s}</html>'

@app.route('/heat/<temperature>')
def heat(temperature):
    conn = get_connection()
    error = ''
    try:
        error = process_state_change(conn, Message.HEAT, int(temperature), f'{request.user_agent} at {request.remote_addr}')
    except ValueError:
        error = "error: failed to parse temp as int"        

    s = get_status_info(conn)
    conn.close()
    return f'<html>{s}, {error}</html>'

@app.route('/message/')
def message():
    sender = request.args.get('sender', str)
    message_body = request.args.get('message_body', str)
    
    (msg, param) = parse_message(message_body)
    conn = get_connection()
    error = 'msg processed OK'
    
    if msg == Message.UNKNOWN:
        send_message(ADMIN, f'Failed to parse message received from {sender}', serial = 1)
        send_message(ADMIN, message_body, serial = 2)
        s = get_status_info(conn)
    elif msg == Message.INFO:
        s = get_status_info(conn)
        (timestamp_last_str, result_last) = load_last_healthcheck(conn)
    else:
        error = process_state_change(conn, msg, param, sender)
        s = get_status_info(conn)
        send_message(sender, s + ', ' + error)

    conn.close()

    return f'<html>{s}, {error}</html>'

@app.route('/healthcheck/')
def healthcheck():
    conn = get_connection()
    (current_state, current_param) = load_current_state(conn)
    (timestamp_last_str, result_last) = load_last_healthcheck(conn)
    timestamp_last = datetime.strptime(timestamp_last_str, TIMESTAMP_FORMAT)
    timestamp_now = datetime.now()
    if timestamp_now > timestamp_last + HEALTHCHECK_DELAY:
        timestamp = timestamp_now.strftime(TIMESTAMP_FORMAT)
        result = 'OK'
        # perform healthchecks
        max_temp = load_max_temp_since(conn, timestamp_last_str)
        if max_temp == None:
            result = f'NO TEMP SINCE {timestamp_last_str}'
            send_message(ADMIN, result)
        elif current_state == State.ON and max_temp < current_param:
            result = f'MAX TEMP {max_temp}C SINCE {timestamp_last_str}'
            send_message(ADMIN, result)
        save_healthcheck(conn, timestamp, result)
    else:
        timestamp = timestamp_last_str
        result = result_last
        
    return f'<html>healthcheck ran @{timestamp}, result: {result}</html>'
