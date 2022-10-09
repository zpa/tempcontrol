import statemachine as sm

def test_T0():
    assert sm.Temp.get(measured = 10, target = 12, delta_minus = 1) == sm.Temp.T0

def test_T1_below():
    assert sm.Temp.get(measured = 11.5, target = 12, delta_minus = 1, delta_plus = 1) == sm.Temp.T1

def test_T1_above():
    assert sm.Temp.get(measured = 12.5, target = 12, delta_minus = 1, delta_plus = 1) == sm.Temp.T1

def test_T2():
    assert sm.Temp.get(measured = 14, target = 12, delta_plus = 1) == sm.Temp.T2
    
