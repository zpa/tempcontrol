from enum import Enum
from .config import TEMP_DELTA_MINUS, TEMP_DELTA_PLUS

# temperature control

# temperature regions for implementing hysteresis
# <----T0----+----T1----+----T2---->
#            |          |
#            |          +--- target + TEMP_DELTA_PLUS
#            +-------------- target - TEMP_DELTA_MINUS
class Temp(Enum):
    T0 = 0
    T1 = 1
    T2 = 2
    
    @staticmethod
    def get(measured, target, delta_minus = TEMP_DELTA_MINUS, delta_plus = TEMP_DELTA_PLUS):
        if target == None:
            return None
        
        temp = Temp.T0
        try:
            if measured < target - delta_minus:
                pass
            elif measured > target + delta_plus:
                temp = Temp.T2
            else:
                temp = Temp.T1
            
            return temp
        
        except TypeError:
            raise ValueError(f'Temp.get() could not determine region, parameters: (measured = {measured}, target = {target}, delta_minus = {delta_minus}, delta_plus = {delta_plus})')

# system state
class State(Enum):
    OFF = 1
    ON = 2
    MANUAL = 3

# events
class Event(Enum):
    OFF = 1
    ON = 2
    TEMP = 3
    MANUAL = 4

    @staticmethod
    def parse_message(message):
        if message[0:3].lower() == 'off':
            return (Event.OFF, None)
        elif message[0:2].lower() == 'on':
            temp = int(message[2:])
            return (Event.ON, temp)
        elif message[0:6].lower() == 'manual':
            return (Event.MANUAL, None)
        else:
            raise ValueError(f'Event.parse_message() could not interpret message {message}')

    @staticmethod
    def create_from(state):
        if state == State.OFF:
            return Event.OFF
        elif state == State.ON:
            return Event.ON
        elif state == State.MANUAL:
            return Event.MANUAL
        else:
            raise ValueError(f'no Event corresponds to {state}')
    
    def str_with(self, temp = None):
        text = self.name.lower()
        if temp != None:
            text += f' {temp}'
        return text
    
# Shelly relay control messages
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

    (Event.ON, State.MANUAL, Temp.T0): (State.ON, ControlMessage.ON),  # temp from control message
    (Event.ON, State.MANUAL, Temp.T1): (State.ON, ControlMessage.ON),  # temp from control message
    (Event.ON, State.MANUAL, Temp.T2): (State.ON, ControlMessage.OFF), # temp from control message
    (Event.ON, State.MANUAL, None): (State.MANUAL, ControlMessage.ON),

    (Event.TEMP, State.ON, Temp.T0): (State.ON, ControlMessage.ON),
    (Event.TEMP, State.ON, Temp.T1): (State.ON, None),
    (Event.TEMP, State.ON, Temp.T2): (State.ON, ControlMessage.OFF),
    (Event.TEMP, State.OFF, None): (State.OFF, None),
    (Event.TEMP, State.MANUAL, None): (State.MANUAL, None),

    (Event.OFF, State.ON, Temp.T0): (State.OFF, ControlMessage.OFF), # temp from state
    (Event.OFF, State.ON, Temp.T1): (State.OFF, ControlMessage.OFF), # temp from state
    (Event.OFF, State.ON, Temp.T2): (State.OFF, ControlMessage.OFF), # temp from state
    (Event.OFF, State.OFF, None): (State.OFF, ControlMessage.OFF),
    (Event.OFF, State.MANUAL, None): (State.OFF, ControlMessage.OFF),

    (Event.MANUAL, State.ON, Temp.T0): (State.MANUAL, ControlMessage.ON),
    (Event.MANUAL, State.ON, Temp.T1): (State.MANUAL, ControlMessage.ON),
    (Event.MANUAL, State.ON, Temp.T2): (State.MANUAL, ControlMessage.ON),
    (Event.MANUAL, State.OFF, None): (State.MANUAL, ControlMessage.ON),
    (Event.MANUAL, State.MANUAL, None): (State.MANUAL, ControlMessage.ON)
}

def transition(event, state, temp):
    (new_state, message) = state_transition_table[(event, state, temp)]
    return (new_state, message)

# boiler control

# system state
class BoilerState(Enum):
    OFF = 1
    ON = 2

# boiler events
class BoilerEvent(Enum):
    OFF = 1
    ON = 2

    @staticmethod
    def parse_message(message):
        if message[0:3].lower() == 'off':
            return BoilerEvent.OFF
        elif message[0:2].lower() == 'on':
            return BoilerEvent.ON
        else:
            raise ValueError(f'BoilerEvent.parse_message() could not interpret message {message}')

    @staticmethod
    def create_from(state):
        if state == BoilerState.OFF:
            return BoilerEvent.OFF
        elif state == BoilerState.ON:
            return BoilerEvent.ON
        else:
            raise ValueError(f'no BoilerEvent corresponds to {state}')

    def str(self):
        return self.name.lower()


# events: on, off
# states: on, off
# messages: on, off
# state transition table header:
# event state new_state action
boiler_state_transition_table = {
    (BoilerEvent.ON, BoilerState.ON): (BoilerState.ON, ControlMessage.ON),
    (BoilerEvent.ON, BoilerState.OFF): (BoilerState.ON, ControlMessage.ON),
    (BoilerEvent.OFF, BoilerState.ON): (BoilerState.OFF, ControlMessage.OFF),
    (BoilerEvent.OFF, BoilerState.OFF): (BoilerState.OFF, ControlMessage.OFF)
}

def boiler_transition(event, state):
    (new_state, message) = boiler_state_transition_table[(event, state)]
    return (new_state, message)
