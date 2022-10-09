import sqlite3
import statemachine as sm

def get_connection():
    conn = sqlite3.connect("tempcontrol.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_most_recent_temp(conn):
    QUERY = '''
    SELECT temperature from Measurement ORDER BY timestamp DESC LIMIT 1;
    '''
    cur = conn.cursor()
    results = cur.execute(QUERY)
    rows = results.fetchall()
    return rows[0]['temperature']

def get_current_state(conn):
    QUERY = '''
    SELECT stateId, param from State ORDER BY timestamp DESC LIMIT 1;
    '''
    cur = conn.cursor()
    results = cur.execute(QUERY)
    rows = results.fetchall()
    state = sm.State(rows[0]['stateId'])
    param = rows[0]['param']                  
    return (state, param)

def set_current_state(conn, timestamp, state, param, requester):
    QUERY = '''
    INSERT INTO State(timestamp,stateId,param,requester) VALUES (?,?,?,?)
    '''    
    cur = conn.cursor()
    cur.execute(QUERY, (timestamp, state.value, param, requester))
    conn.commit()

def add_measurement(conn, timestamp, temperature, humidity):
    QUERY = '''
    INSERT INTO Measurement(timestamp, temperature, humidity) VALUES(?,?,?);
    '''
    cur = conn.cursor()
    cur.execute(QUERY, (timestamp, temperature, humidity))
    conn.commit()
