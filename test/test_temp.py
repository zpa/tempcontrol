from statemachine import Temp

def test_T0():
    assert Temp.get(measured = 10, target = 12, delta_minus = 1) == Temp.T0

def test_T1_below():
    assert Temp.get(measured = 11.5, target = 12, delta_minus = 1, delta_plus = 1) == Temp.T1

def test_T1_above():
    assert Temp.get(measured = 12.5, target = 12, delta_minus = 1, delta_plus = 1) == Temp.T1

def test_T2():
    assert Temp.get(measured = 14, target = 12, delta_plus = 1) == Temp.T2
    
