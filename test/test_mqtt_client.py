import pytest
import mock
import importlib
test_client = importlib.import_module("tempcontrol-mqtt-client")
from statemachine import State, ControlMessage

class Message:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_remains_off_after_temp_reading(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (State.OFF, None)
    mock_get_most_recent_temp.return_value = 12.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'11.00'))
    # must close db connection
    mock_connect.return_value.close.assert_called()
    mock_publish_message.assert_called_with(mock_client, None)

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_hysteresis(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'8.00'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'10.00'))
    mock_publish_message.assert_called_with(mock_client, None)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'13.00'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'10.00'))
    mock_publish_message.assert_called_with(mock_client, None)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'8.00'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_switches_off(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_get_current_state.return_value = (State.OFF, None)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_turns_heating_on_when_switched_on(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (State.OFF, None)
    mock_get_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_get_current_state.return_value = (State.OFF, None)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_keeps_heating_on_when_needed(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_keeps_heating_off_when_needed(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (State.OFF, None)
    mock_get_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_inconsistent_state(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (-999, None)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_not_called()
    
    mock_get_current_state.return_value = (State.OFF, None)
    mock_get_most_recent_temp.return_value = 'bla'
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_not_called()
    
    mock_get_current_state.return_value = (-999, None)
    mock_get_most_recent_temp.return_value = 'bla'
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_not_called()

@mock.patch("tempcontrol-mqtt-client.mqtt.Client")
@mock.patch("database.get_most_recent_temp")
@mock.patch("database.get_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol-mqtt-client.publish_message")
def test_wrong_temp_reading(mock_publish_message, mock_connect, mock_get_current_state, mock_get_most_recent_temp, mock_client):
    mock_get_current_state.return_value = (State.ON, 10)
    mock_get_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'bla'))
    mock_publish_message.assert_not_called()
