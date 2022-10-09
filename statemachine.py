from enum import Enum

# temperature regions for implementing hysteresis
# <----T0----+----T1----+----T2---->
TEMP_DELTA_MINUS = 0.5
TEMP_DELTA_PLUS = 1.0

class Temp(Enum):
    T0 = 0
    T1 = 1
    T2 = 2
    
    @staticmethod
    def get(measured, target, delta_minus = TEMP_DELTA_MINUS, delta_plus = TEMP_DELTA_PLUS):
        if target == None:
            return None
        
        temp = Temp.T0
        if measured < target - delta_minus:
            pass
        elif measured > target + delta_plus:
            temp = Temp.T2
        else:
            temp = Temp.T1
            
        return temp

# system state
class State(Enum):
    OFF = 1
    ON = 2

# events
class Event(Enum):
    OFF = 1
    ON = 2
    TEMP = 3

    @staticmethod
    def parse_message(message):
        if message[0:3].lower() == 'off':
            return (Event.OFF, None)
        elif message[0:2].lower() == 'on':
            temp = int(message[2:])
            return (Event.ON, temp)
        else:
            raise ValueError(f'Event.parse_message() could not interpret message {message}')

    @staticmethod
    def create_from(state):
        if state == State.OFF:
            return Event.OFF
        elif state == State.ON:
            return Event.ON
        else:
            raise ValueError(f'no Event corresponds to {state}')
    
    def str(self, temp = None):
        text = self.name.lower()
        if temp != None:
            text += f' {temp}'
        return text
    
# control messages
class ControlMessage(Enum):
    OFF = 1
    ON = 2
    @property
    def str(self):
        return self.name.lower()
    
# events: on, off, temp
# states: on, off
# messages: on, off
# state transition table header:
# event state temp new_state action
state_transition_table = {
    (Event.ON, State.ON, Temp.T0): (State.ON, ControlMessage.ON),
    (Event.ON, State.ON, Temp.T1): (State.ON, ControlMessage.ON),
    (Event.ON, State.ON, Temp.T2): (State.ON, ControlMessage.OFF),
    (Event.ON, State.OFF, Temp.T0): (State.ON, ControlMessage.ON),  # temp from control message
    (Event.ON, State.OFF, Temp.T1): (State.ON, ControlMessage.ON),  # temp from control message
    (Event.ON, State.OFF, Temp.T2): (State.ON, ControlMessage.OFF), # temp from control message
    (Event.ON, State.OFF, None): (State.ON, ControlMessage.ON),
    (Event.TEMP, State.ON, Temp.T0): (State.ON, ControlMessage.ON),
    (Event.TEMP, State.ON, Temp.T1): (State.ON, None),
    (Event.TEMP, State.ON, Temp.T2): (State.ON, ControlMessage.OFF),
    (Event.TEMP, State.OFF, None): (State.OFF, None),
    (Event.OFF, State.ON, Temp.T0): (State.OFF, ControlMessage.OFF), # temp from state
    (Event.OFF, State.ON, Temp.T1): (State.OFF, ControlMessage.OFF), # temp from state
    (Event.OFF, State.ON, Temp.T2): (State.OFF, ControlMessage.OFF), # temp from state
    (Event.OFF, State.OFF, None): (State.OFF, ControlMessage.OFF)
}

def transition(event, state, temp):
    (new_state, message) = state_transition_table[(event, state, temp)]
    return (new_state, message)
