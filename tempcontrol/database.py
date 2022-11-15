import sqlite3
from .statemachine import State
import pandas as pd

def get_connection():
    conn = sqlite3.connect("tempcontrol.db")
    conn.row_factory = sqlite3.Row
    return conn

def load_most_recent_temp(conn):
    QUERY = '''
    SELECT temperature from Measurement ORDER BY timestamp DESC LIMIT 1;
    '''
    cur = conn.cursor()
    results = cur.execute(QUERY)
    rows = results.fetchall()
    return rows[0]['temperature']

def load_temp_after(conn, timestamp):
    df = pd.read_sql_query(f'SELECT timestamp, temperature from Measurement WHERE timestamp > "{timestamp}"', conn)
    return df
                          
def load_current_state(conn):
    QUERY = '''
    SELECT stateId, param from State ORDER BY timestamp DESC LIMIT 1;
    '''
    cur = conn.cursor()
    results = cur.execute(QUERY)
    rows = results.fetchall()
    state = State(rows[0]['stateId'])
    param = rows[0]['param']                  
    return (state, param)

def save_current_state(conn, timestamp, state, param, requester):
    QUERY = '''
    INSERT INTO State(timestamp,stateId,param,requester) VALUES (?,?,?,?)
    '''    
    cur = conn.cursor()
    cur.execute(QUERY, (timestamp, state.value, param, requester))
    conn.commit()

def save_measurement(conn, timestamp, temperature, humidity):
    QUERY = '''
    INSERT INTO Measurement(timestamp, temperature, humidity) VALUES(?,?,?);
    '''
    cur = conn.cursor()
    cur.execute(QUERY, (timestamp, temperature, humidity))
    conn.commit()

def load_last_healthcheck(conn):
    QUERY = '''
    SELECT timestamp,result FROM Healthcheck ORDER BY timestamp DESC LIMIT 1;
    '''
    cur = conn.cursor()
    results = cur.execute(QUERY)
    rows = results.fetchall()
    timestamp = rows[0]['timestamp']
    result = rows[0]['result']
    return (timestamp, result)

def save_healthcheck(conn, timestamp, result):
    QUERY = '''
    INSERT INTO Healthcheck(timestamp, result) VALUES(?,?)
    '''
    cur = conn.cursor()
    cur.execute(QUERY, (timestamp, result))
    conn.commit()

def load_max_temp_since(conn, timestamp):
    cur = conn.cursor()
    results = cur.execute(f'SELECT MAX(temperature) FROM Measurement WHERE timestamp > "{timestamp}"')
    rows = results.fetchall()
    temp = rows[0]['MAX(temperature)']
    return temp

