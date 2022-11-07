import pytest
import mock
from tempcontrol.views import Message, get_new_state, process_state_change
from tempcontrol.statemachine import State
from datetime import datetime

state_transition_table = {
    (State.ON, Message.UNKNOWN): State.ON,
    (State.ON, Message.INFO): State.ON,
    (State.ON, Message.HEAT): State.ON,
    (State.ON, Message.TURN_OFF): State.OFF,
    (State.OFF, Message.UNKNOWN): State.OFF,
    (State.OFF, Message.INFO): State.OFF,
    (State.OFF, Message.HEAT): State.ON,
    (State.OFF, Message.TURN_OFF): State.OFF
}
    
def test_get_new_state():
    for (from_state, message) in state_transition_table:
        assert get_new_state(from_state, message) == state_transition_table[(from_state, message)]

@mock.patch("tempcontrol.views.set_current_state")
@mock.patch("tempcontrol.views.load_current_state")
@mock.patch("tempcontrol.views.datetime")
def test_process_state_change(mock_datetime, mock_load_current_state, mock_set_current_state):
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

