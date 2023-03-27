import pytest
import mock
from tempcontrol.views import Message, get_new_state, process_state_change
from tempcontrol.statemachine import State, BoilerState, Event, BoilerEvent
from tempcontrol.config import TEMPCONTROL_TOPIC, BOILERCONTROL_TOPIC
from datetime import datetime

state_transition_table = {
    (State.ON, Message.UNKNOWN): State.ON,
    (State.ON, Message.INFO): State.ON,
    (State.ON, Message.HEAT): State.ON,
    (State.ON, Message.TURN_OFF): State.OFF,
    (State.ON, Message.MANUAL_MODE): State.MANUAL,
    (State.OFF, Message.UNKNOWN): State.OFF,
    (State.OFF, Message.INFO): State.OFF,
    (State.OFF, Message.HEAT): State.ON,
    (State.OFF, Message.TURN_OFF): State.OFF,
    (State.OFF, Message.MANUAL_MODE): State.MANUAL,
    (State.MANUAL, Message.UNKNOWN): State.MANUAL,
    (State.MANUAL, Message.INFO): State.MANUAL,
    (State.MANUAL, Message.HEAT): State.ON,
    (State.MANUAL, Message.TURN_OFF): State.OFF,
    (State.MANUAL, Message.MANUAL_MODE): State.MANUAL
}

boiler_state_transition_table = {
    (BoilerState.ON, Message.BOILER_OFF): BoilerState.OFF,
    (BoilerState.ON, Message.BOILER_ON): BoilerState.ON,
    (BoilerState.OFF, Message.BOILER_OFF): BoilerState.OFF,
    (BoilerState.OFF, Message.BOILER_ON): BoilerState.ON
}

def test_get_new_state():
    for (from_state, message) in state_transition_table:
        assert get_new_state(from_state, message) == state_transition_table[(from_state, message)]

@mock.patch("tempcontrol.views.set_current_boiler_state")
@mock.patch("tempcontrol.views.set_current_state")
@mock.patch("tempcontrol.views.load_current_state")
@mock.patch("tempcontrol.views.datetime")
def test_process_state_change(mock_datetime, mock_load_current_state, mock_set_current_state, mock_set_current_boiler_state):
    CONN = 'conn'
    REQUESTER = 'cell_number'
    TIMESTAMP = 'timestamp'
    mock_datetime.now.return_value.strftime.return_value = TIMESTAMP
    for (from_state, message) in state_transition_table:
        param = None
        if message == Message.HEAT:
            param = 12
            
        mock_load_current_state.return_value = (from_state, param)
        process_state_change(CONN, message, param, REQUESTER)
        to_state = state_transition_table[(from_state, message)]
        mock_set_current_state.assert_called_with(CONN, TIMESTAMP, to_state, param, REQUESTER)
        mock_set_current_boiler_state.assert_not_called()

@mock.patch("tempcontrol.views.set_current_state")
@mock.patch("tempcontrol.views.set_current_boiler_state")
@mock.patch("tempcontrol.views.load_current_boiler_state")
@mock.patch("tempcontrol.views.datetime")
def test_process_boiler_state_change(mock_datetime, mock_load_current_boiler_state, mock_set_current_boiler_state, mock_set_current_state):
    CONN = 'conn'
    REQUESTER = 'cell_number'
    TIMESTAMP = 'timestamp'
    mock_datetime.now.return_value.strftime.return_value = TIMESTAMP
    for (from_state, message) in boiler_state_transition_table:
        mock_load_current_boiler_state.return_value = from_state
        process_state_change(CONN, message, None, REQUESTER)
        to_state = boiler_state_transition_table[(from_state, message)]
        mock_set_current_boiler_state.assert_called_with(CONN, TIMESTAMP, to_state, REQUESTER)
        mock_set_current_state.assert_not_called()

@mock.patch("tempcontrol.views.mqtt_publish.single")
@mock.patch("tempcontrol.views.save_current_state")
@mock.patch("tempcontrol.views.load_current_state")
@mock.patch("tempcontrol.views.datetime")
def test_process_state_change_including_mqtt(mock_datetime, mock_load_current_state, mock_save_current_state, mock_mqtt_publish_single):
    CONN = 'conn'
    REQUESTER = 'cell_number'
    TIMESTAMP = 'timestamp'
    mock_datetime.now.return_value.strftime.return_value = TIMESTAMP
    for (from_state, message) in state_transition_table:
        param = None
        if message == Message.HEAT:
            param = 12
            
        mock_load_current_state.return_value = (from_state, param)
        process_state_change(CONN, message, param, REQUESTER)
        to_state = state_transition_table[(from_state, message)]
        mock_mqtt_publish_single.assert_called_with(TEMPCONTROL_TOPIC, payload = Event.create_from(to_state).str_with(param), qos = 2, retain = True, hostname = "localhost", port = 1883, keepalive = 60)

@mock.patch("tempcontrol.views.mqtt_publish.single")
@mock.patch("tempcontrol.views.save_current_boiler_state")
@mock.patch("tempcontrol.views.load_current_boiler_state")
@mock.patch("tempcontrol.views.datetime")
def test_process_boiler_state_change_including_mqtt(mock_datetime, mock_load_current_boiler_state, mock_save_current_boiler_state, mock_mqtt_publish_single):
    CONN = 'conn'
    REQUESTER = 'cell_number'
    TIMESTAMP = 'timestamp'
    mock_datetime.now.return_value.strftime.return_value = TIMESTAMP
    for (from_state, message) in boiler_state_transition_table:
        mock_load_current_boiler_state.return_value = from_state
        process_state_change(CONN, message, None, REQUESTER)
        to_state = boiler_state_transition_table[(from_state, message)]
        mock_mqtt_publish_single.assert_called_with(BOILERCONTROL_TOPIC, payload = BoilerEvent.create_from(to_state).str(), qos = 2, retain = True, hostname = "localhost", port = 1883, keepalive = 60)
