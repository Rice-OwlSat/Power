# This file includes all the necessary Enum and state classes needed
# to run the EPS.
from enum import Enum
import board
i2c = board.I2C()

class State(Enum):
    ON_LOW_POWER = 0
    ON_NORMAL    = 1
    ON           = 2
    OFF          = 3
    INVALID      = 4

class Read(Enum):
    '''
    Enumeration class for the EPS read commands, which are used in the
    measurements method in the Power class.
    '''
    VOLTAGE = 1
    BATCURRENT = 2
    TEMPERATURE = 3
    XVOLTS = 4
    XMINCURRENT = 5
    XPLUSCURRENT = 6
    YVOLTS = 7
    YMINCURRENT = 8
    YPLUSCURRENT = 9
    ZVOLTS = 10
    ZMINCURRENT = 11
    ZPLUSCURRENT = 12
    BUS3V3 = 13
    BUS5V = 14

class Write(Enum):
    '''
    Enumeration class for the EPS write commands, which are used in the
    commands method in the Power class.
    '''
    SELF_LOCK_ON = 1
    SELF_LOCK_OFF = -1
    BUS3V3_ON = 2
    BUS3V3_OFF = -2
    BUS5V_ON = 3
    BUS5V_OFF = -3
    LUP3V3_ON = 4
    LUP3V3_OFF = -4
    HEATER1_ON = 5
    HEATER1_OFF = -5
    HEATER2_ON = 6
    HEATER2_OFF = -6
    HEATER3_ON = 7
    HEATER3_OFF = -7

def write(state, command):
    response_dict: Dict[str, List[int]] = {
            Write.SELF_LOCK_ON: [0x300001],
            Write.SELF_LOCK_OFF: [0x300000],
            Write.BUS3V3_ON: [0x300301],
            Write.BUS3V3_OFF: [0x300300],
            Write.BUS5V_ON: [0x300401],
            Write.BUS5V_OFF: [0x300400],
            Write.LUP3V3_ON: [0x300501],
            Write.LUP3V3_OFF: [0x300500],
            Write.LUP5V_ON: [0x300601],
            Write.LUP5V_OFF: [0x300600],
            Write.HEATER1_ON: [0x301001],
            Write.HEATER1_OFF: [0x301000],
            Write.HEATER2_ON: [0x301101],
            Write.HEATER2_OFF: [0x301100],
            Write.HEATER3_ON: [0x301201],
            Write.HEATER3_OFF: [0x301200]
        }

    if state == State.ON or state == State.ON_LOW_POWER:
        try:
            i2c.writeto(eps, bytes(response_dict[command]), stop=False)
        except KeyError(e):
            print(f"Command {command} does not exist!")
    else:
        return "Satellite is off."

class State_machine(Enum):
    '''
    This is a class which automatically changes the state of the satellite
    depending on particular factors such as power draw and battery charge.
    States include: ON_NORMAL
                    ON_LOW_POWER
                    OFF
    '''
    def __init__(self):
        self.previous_states = []
        self.state = State.INVALID

    def check_battery(self, power_system: Power):
        charge = power_system.measurements('voltage')
        if charge <= 3:
            if len(self.previous_states) >= 50:
                self.previous_states = [self.state]
            else:
                self.previous_states.append(self.state)
            self.state = State.ON_LOW_POWER
            return self.state
        else:
            return self.previous_states.append(self.state)

        self.state = State.ON_NORMAL
        return self.state

    def previous_states(self, lookback_time: int) -> List[State]:
        '''
        Returns previous states of the power system, depending on specified
        number in the variable lookback_time.
        '''
        self.previous_states[(len(self.previous_states) - lookback_time):].reverse() # Will return empty list as necessary

    def shutdown(self):
        if len(self.previous_states) >= 50:
            self.previous_states = [self.state]
        else:
            self.previous_states.append(self.state)

        self.state = State.OFF
