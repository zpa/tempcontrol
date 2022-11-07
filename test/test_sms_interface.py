import pytest
from tempcontrol.views import Message, parse_message

def test_parse_message():
    assert parse_message('info') == (Message.INFO, None)
    assert parse_message('Info') == (Message.INFO, None)
    assert parse_message('InFo') == (Message.INFO, None)
    assert parse_message('INFO') == (Message.INFO, None)
    assert parse_message('turn off') == (Message.TURN_OFF, None)
    assert parse_message('Turn Off') == (Message.TURN_OFF, None)
    assert parse_message('TuRn OfF') == (Message.TURN_OFF, None)
    assert parse_message('TURN OFF') == (Message.TURN_OFF, None)    
    assert parse_message('heat 1') == (Message.HEAT, 1)
    assert parse_message('Heat 12') == (Message.HEAT, 12)
    assert parse_message('HeAt 123') == (Message.HEAT, 123)
    assert parse_message('HEAT 1234') == (Message.HEAT, 1234)
    assert parse_message('TURN ON') == (Message.UNKNOWN, None)
    assert parse_message('HEAT') == (Message.UNKNOWN, None)
    assert parse_message('HEAT 11.7') == (Message.UNKNOWN, None)
    assert parse_message('INFO 2') == (Message.INFO, None)
    assert parse_message('Bla') == (Message.UNKNOWN, None)
    assert parse_message('') == (Message.UNKNOWN, None)

