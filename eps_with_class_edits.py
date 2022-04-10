# Rice University SEDS OwlSat Project - Power Systems Team
# Rev 4 (using class) - 8 April 2022

# This is a program for testing the OwlSat EPS
# Functions include reading input data, output data, and turning power buses on and off

# WINSTON: Big thing for safe development -- use Python's type annotations to specify what types things
# should have before you run the program and serves as a form of soft documentation, i.e. instead of:
#       def my_func(a):
# you write
#       def my_func(a: int):
# That way, everyone knows `my_func` takes an int and not a string
# If you need to take in any of a combination of types, use `Union`, i.e. instead of
#       def my_func_that_takes_an_int_or_a_string(a):
# you write
#       def my_func_that_takes_an_int_or_a_string(a: Union[int, string]):
# See: https://docs.python.org/3/library/typing.html.

import board
from enum import Enum
import time

# WINSTON: Is this module the only one that uses the I2C board?
# Not sure about the behavior of i2c.writeto, also not sure if this will be multithreaded,
# but you might consider putting `i2c` behind a Mutex to prevent simultaneous writes to the board (data races).
i2c = board.I2C()

while not i2c.try_lock():
    pass

# WINSTON: Probably obvious, but this should be rewritten for production.
try:
    while True:
        print("I2C addresses found:", [hex(device_address)
              for device_address in i2c.scan()])
        time.sleep(2)

finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
    i2c.unlock()

eps = 0x18

class State(Enum):
    ON_LOW_POWER = 0
    ON_NORMAL    = 1
    ON           = 2
    OFF          = 3
    INVALID      = 4

class State_machine(Enum):
    # WINSTON: If you have a Finite State Machine (emphasis on finite), you should use Python's enums
    # to model state. These can also have data attached (like a number below).
    # See: https://docs.python.org/3/library/enum.html.

    '''
    This is a class which automatically changes the state of the satellite
    depending on particular factors such as power draw and battery charge.
    States include: ON_NORMAL
                    ON_LOW_POWER
                    OFF
    '''
    def __init__(self):
        self.previous_states = []          # WINSTON: Should probably clear this every now and then lest it get too big
        self.state = State.INVALID

    def check_battery(self, power_system: Power):
        charge = power_system.measurements('voltage')
        if charge <= 3:
            if len(self.previous_states) >= 50:
                self.previous_states = [self.state]
            else:
                self.previous_states.append(self.state)
            return self.state = State.ON_LOW_POWER
        else:
            return self.previous_states.append(self.state)

        return self.state = State.ON_NORMAL

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

class Power:
    '''
    This is a class with methods regarding the power systems on the satellite.
    Attributes:
        read_data - must be called with an argument determining the desired data
        write_data - must be called with desired parameter to change
    Commands will be afffected by the current state of the system, which includes
    the following: ON_NORMAL
                   ON_LOW_POWER
                   OFF
    '''
    def __init__(self, state: State_Machine):
        self.state = State_Machine()

    def measurements(self, param: str) -> float:
        '''
        This function returns a value for the given parameter.
        Input: string indicating 'voltage,' 'current,' or 'temperature.'
        NOTE: Only works for battery measurements at the moment, individual input
              and output channels/busses will be implemented later.
        Returns value in V, A, or C.
        '''
        result = 0

        # This is a dictionary from command to a tuple of (bytes, lambda).
        # Lambdas are anonymous functions, i.e. `lambda r: r + 1` is equivalent to
        #
        # def my_int_func(x: int):
        #     return x + 1
        #
        # Much shorter ;)
        response_dict: Dict[str, Tuple[List[int], Callable[int, float]]] = {
            Read.VOLTAGE: ([0x300131], lambda r: r * 0.0023394775),
            Read.BATCURRENT: ([0x300231], lambda r: r * 0.0030517578),
            Read.TEMPERATURE: ([0x304F31], lambda r: (r * 0.00390625) if (r << 0x8000) else (((result < 4)-1) | 0xFFFF) * (-0.0624)),
            Read.XVOLTS: ([0x300531], lambda r: r * 0.0024414063),
            Read.XMINCURRENT: ([0x300631], lambda r: r * 0.0006103516),
            Read.XPLUSCURRENT: ([0x300731], lambda r: r * 0.0006103516),
            Read.YVOLTS: ([0x300831], lambda r: r * 0.0024414063),
            Read.YMINCURRENT: ([0x300931], lambda r: r * 0.0006103516),
            Read.YPLUSCURRENT: ([0x300A31], lambda r: r * 0.0006103516),
            Read.ZVOLTS: ([0x300B31], lambda r: r * 0.0024414063),
            Read.ZMINCURRENT: ([0x300C31], lambda r: r * 0.0006103516),
            Read.ZPLUSCURRENT: ([0x300D31], lambda r: r * 0.0006103516),
            Read.BUS3V3: ([0x300E31], lambda r: r * 0.0020345052),
            Read.BUS5V: ([0x300F31], lambda r: r * 0.0020345052)
        }

        if self.state == State.ON_NORMAL or self.state == State.ON_LOW_POWER:
            try:
                (to_write, result_conversion) = response_dict[param]
                i2c.writeto(eps, bytes(to_write), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                return result_conversion(int(result, 2))
            except KeyError(e):
                print(f"Command {param} does not exist!")
        elif self.state == State.OFF:
            # WINSTON: You might consider throwing an exception instead of printing something
            print("Power Systems are off, please turn system on to perform"
                  " the requested command.")
        else:
            # WINSTON: Ditto
            print("Error: unexpected satellite state.")

    # WINSTON: As above, you may want to consider a `Command` enum if there are a finite
    # number. Then, add another method for writing raw bytes to the I2C bus.
    #
    # You should also return something that confirms the satellite received the command and executed it
    # (if it can transmit back).
    def commands(self, command: str):
        '''
        This function sends the specified command to the EPS.
        Input: string indicating the command
        Command list:
            self_lock_on/off - 0x00
            bus3v3_on/off - 0x03
            bus5v_on/off - 0x04
            lup3v3_on/off - 0x05
            lup5v_on/off - 0x06
            heater1_on/off - 0x10
            heater2_on/off - 0x11
            heater3_on/off - 0x12
        Prints serial notification.
        '''
        # WINSTON: Same thing as above.
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
            Write.HEATER3_OFF: [0x301200],
        }

        if self.state == State.ON or self.state == State.ON_LOW_POWER:
            try:
                i2c.writeto(eps, bytes(response_dict[command]), stop=False)
            except KeyError(e):
                print(f"Command {command} does not exist!")
        elif self.state == State.OFF:
            print("Power Systems are off, please turn system on to perform"
                  " the requested command.")
        else:
            print("Error: unexpected satellite state.")

    # WINSTON: Is `state` supposed to be the state of the Power class? If it is, you should use `self.state`
    # Also, Python functions should generally either return something always or never return something
    def power_state(self, state) -> State:
        """
        Checks whether the satellite needs to be in low power mode; turns
        satellite back on if the power reaches a safe level again. Lower
        power mode consists of the following power priority points:
            1 - EPS and PyCubed (highest)
            2 - EUV Sensor Circuitry
            3 - a) GNSS, IMU, etc.
                b) Magnetorquer
            4 - UHF Transceiver (lowest)
        Devices will be turned off/placed in low power mode in reverse
        order of priority.
        """
        if self.state == State.OFF:
            return "Satellite is off."

        THRESHOLD1 = 0           # Low power battery thresholds
        THRESHOLD2 = 0
        THRESHOLD3 = 0           # 0's are placeholders for actual values
        COMMS_BUS = 'bus3v3'     # Component bus locations
        MAG_BUS = 'bus3v3'
        GNSS_BUS = 'bus3v3'
        EUV_BUS = 'bus3v3'
        PY_BUS = 'bus3v3'
        BATTERY = self.measurements('voltage')

        # if state == 'OFF':
        #     return

        # WINSTON: Is there any code to automatically turn things back on?
        # You should consider tracking the state of each bus in the class to make sure the commands went through.

        if self.state == 'OFF':
            self.commands(PY_BUS + '_off')
            self.commands(EUV_BUS+ '_off')
            self.commands(GNSS_BUS + '_off')
            self.commands(MAG_BUS + '_off')
            self.commands(COMMS_BUS + '_off')
            print(self.measurements(BUS3V3), self.measurements(BUS5V))
        elif BATTERY <= THRESHOLD3:
            self.commands(PY_BUS + '_on')
            self.commands(EUV_BUS+ '_off')
            self.commands(GNSS_BUS + '_off')
            self.commands(MAG_BUS + '_off')
            self.commands(COMMS_BUS + '_off')
            print(self.measurements(BUS3V3), self.measurements(BUS5V))
            self.state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD2:
            self.commands(PY_BUS + '_on')
            self.commands(EUV_BUS+ '_off')
            self.commands(GNSS_BUS + '_off')
            self.commands(MAG_BUS + '_off')
            self.commands(COMMS_BUS + '_on')
            print(self.measurements(BUS3V3), self.measurements(BUS5V))
            self.state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD1:
            self.commands(PY_BUS + '_on')
            self.commands(EUV_BUS+ '_off')
            self.commands(GNSS_BUS + '_on')
            self.commands(MAG_BUS + '_on')
            self.commands(COMMS_BUS + '_on')
            print(self.measurements(BUS3V3), self.measurements(BUS5V))
            self.state = 'ON_LOW_POWER'
        else:
            self.commands(PY_BUS + '_on')
            self.commands(EUV_BUS+ '_on')
            self.commands(GNSS_BUS + '_on')
            self.commands(MAG_BUS + '_on')
            self.commands(COMMS_BUS + '_on')
            print(self.measurements(BUS3V3), self.measurements(BUS5V))
            self.state = 'ON_NORMAL'

        return self.state

# WINSTON: Power class not used?
power_system = Power()





