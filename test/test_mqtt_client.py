import pytest
import mock
import tempcontrol.tempcontrol_mqtt_client as test_client
from tempcontrol.statemachine import State, ControlMessage

class Message:
    def __init__(self, topic, payload):
        self.topic = topic
        self.payload = payload

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_remains_off_after_temp_reading(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 12.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'11.00'))
    # must close db connection
    mock_connect.return_value.close.assert_called()
    mock_publish_message.assert_called_with(mock_client, None)

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_remains_in_manual_mode_after_temp_reading(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.MANUAL, None)
    mock_load_most_recent_temp.return_value = 12.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'11.00'))
    # must close db connection
    mock_connect.return_value.close.assert_called()
    mock_publish_message.assert_called_with(mock_client, None)

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_hysteresis(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'8.00'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'10.00'))
    mock_publish_message.assert_called_with(mock_client, None)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'13.00'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'10.00'))
    mock_publish_message.assert_called_with(mock_client, None)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'8.00'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_switches_off(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_turns_heating_on_when_switched_on(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 12.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_keeps_heating_on_when_needed(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_keeps_heating_off_when_needed(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 13.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_inconsistent_state(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (-999, None)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_not_called()
    
    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 'bla'
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_not_called()
    
    mock_load_current_state.return_value = (-999, None)
    mock_load_most_recent_temp.return_value = 'bla'
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_not_called()

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_wrong_temp_reading(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.SHELLY_HT_TOPIC, b'bla'))
    mock_publish_message.assert_not_called()

@mock.patch("tempcontrol.tempcontrol_mqtt_client.mqtt.Client")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_most_recent_temp")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.load_current_state")
@mock.patch("sqlite3.connect")
@mock.patch("tempcontrol.tempcontrol_mqtt_client.publish_message")
def test_manual_mode(mock_publish_message, mock_connect, mock_load_current_state, mock_load_most_recent_temp, mock_client):
    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'manual'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'manual'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.ON, 10)
    mock_load_most_recent_temp.return_value = 12.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'manual'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.OFF, None)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'manual'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.MANUAL, None)
    mock_load_most_recent_temp.return_value = 8.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.MANUAL, None)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)

    mock_load_current_state.return_value = (State.MANUAL, None)
    mock_load_most_recent_temp.return_value = 12.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'on 10'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_load_current_state.return_value = (State.MANUAL, None)
    mock_load_most_recent_temp.return_value = 12.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'off'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.OFF)

    mock_load_current_state.return_value = (State.MANUAL, None)
    mock_load_most_recent_temp.return_value = 10.00
    test_client.on_message(mock_client, None, Message(test_client.TEMPCONTROL_TOPIC, b'manual'))
    mock_publish_message.assert_called_with(mock_client, ControlMessage.ON)
