import pytest
from tempcontrol.statemachine import BoilerEvent, BoilerState

def test_parse():
    assert BoilerEvent.parse_message('off') == BoilerEvent.OFF
    assert BoilerEvent.parse_message('OFF') == BoilerEvent.OFF
    assert BoilerEvent.parse_message('Off') == BoilerEvent.OFF
    
    assert BoilerEvent.parse_message('on') == BoilerEvent.ON
    assert BoilerEvent.parse_message('ON') == BoilerEvent.ON
    assert BoilerEvent.parse_message('On') == BoilerEvent.ON

    with pytest.raises(ValueError):
        BoilerEvent.parse_message('bla')

    with pytest.raises(ValueError):
        BoilerEvent.parse_message('of')

def test_create_from():
    assert BoilerEvent.create_from(BoilerState.ON) == BoilerEvent.ON
    assert BoilerEvent.create_from(BoilerState.OFF) == BoilerEvent.OFF

    with pytest.raises(ValueError):
        BoilerEvent.create_from(-999)

