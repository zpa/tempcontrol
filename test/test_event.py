import pytest
from tempcontrol.statemachine import Event, State

def test_parse():
    assert Event.parse_message('off') == (Event.OFF, None)
    assert Event.parse_message('OFF') == (Event.OFF, None)
    assert Event.parse_message('Off') == (Event.OFF, None)
    
    assert Event.parse_message('on1') == (Event.ON, 1)
    assert Event.parse_message('ON1') == (Event.ON, 1)
    assert Event.parse_message('On1') == (Event.ON, 1)
    assert Event.parse_message('on 1') == (Event.ON, 1)
    assert Event.parse_message('on 1 ') == (Event.ON, 1)
    assert Event.parse_message('on 12') == (Event.ON, 12)

    assert Event.parse_message('manual') == (Event.MANUAL, None)
    assert Event.parse_message('MANUAL') == (Event.MANUAL, None)
    assert Event.parse_message('MaNuAl') == (Event.MANUAL, None)

    with pytest.raises(ValueError):
        Event.parse_message('bla')

    with pytest.raises(ValueError):
        Event.parse_message('on12c')

    with pytest.raises(ValueError):
        Event.parse_message('onoff')

    with pytest.raises(ValueError):
        Event.parse_message('on12.3')

def test_create_from():
    assert Event.create_from(State.ON) == Event.ON
    assert Event.create_from(State.OFF) == Event.OFF
    assert Event.create_from(State.MANUAL) == Event.MANUAL

    with pytest.raises(ValueError):
        Event.create_from(-999)

def test_str_with():
    assert Event.OFF.str_with() == 'off'
    assert Event.ON.str_with() == 'on'
    assert Event.ON.str_with(1) == 'on 1'
    assert Event.MANUAL.str_with() == 'manual'

