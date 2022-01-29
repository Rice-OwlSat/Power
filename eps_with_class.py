# Rice University SEDS OwlSat Project - Power Systems Team
# Rev 3 (using class) - 28 December 2021

# This is a program for testing the OwlSat EPS
# Functions include reading input data, output data, and turning power buses on and off

import time
import board

i2c = board.I2C()

while not i2c.try_lock():
    pass

try:
    while True:
        print("I2C addresses found:", [hex(device_address)
              for device_address in i2c.scan()])
        time.sleep(2)

finally:  # unlock the i2c bus when ctrl-c'ing out of the loop
    i2c.unlock()

eps = 0x18

class State_machine:
    '''
    This is a class which automatically changes the state of the satellite
    depending on particular factors such as power draw and battery charge.
    States include: ON_NORMAL
                    ON_LOW_POWER
                    OFF
    '''
    def __init__(self):
        self.start_state = 'ON_LOW_POWER'
        self.previous_states = []
        self.state = ''

    def check_battery(self, power_system):
        charge = power_system.measurements('voltage')
        if charge <= 3:
            self.previous_states.append(self.state)
            self.state = 'ON_LOW_POWER'
        else:
            self.previous_states.append(self.state)
            self.state = 'ON_NORMAL'

    def previous_states(self, lookback_time):
        '''
        Returns previous states of the power system, depending on specified
        number in the variable lookback_time.
        '''
        if len(self.previous_states) != 0:
            recent_history = self.previous_states[(len(self.previous_states)
                                                  - lookback_time):]
            return recent_history.reverse()
            # This makes the most recent state appear first in the list
        else:
            return "No past states."

    def shutdown(self):
        self.previous_states.append(self.state)
        self.state = 'OFF'

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
    def __init__(self, state):
        self.state = state

    def measurements(self, param):
        '''
        This function returns a value for the given parameter.
        Input: string indicating 'voltage,' 'current,' or 'temperature.'
        NOTE: Only works for battery measurements at the moment, individual input
              and output channels/busses will be implemented later.
        Returns value in V, A, or C.
        '''
        result = 0
        if (self.state == 'ON_NORMAL') or (self.state == 'ON_LOW_POWER'):
            if param == 'voltage':
                i2c.writeto(eps, bytes([0x01]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0023394775
                return result
            elif param == 'batcurrent':
                i2c.writeto(eps, bytes([0x02]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0030517578
                return result
            elif param == 'temperature':
                i2c.writeto(eps, bytes([0x4F]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                if result << 0x8000:
                    result *= 0.00390625
                else:
                    result = (((result < 4)-1) | 0xFFFF) * (-0.0624)
                return result
            elif param == 'xvolts':
                i2c.writeto(eps, bytes([0x05]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0024414063
                return result
            elif param == 'xmincurrent':
                i2c.writeto(eps, bytes([0x06]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0006103516
                return result
            elif param == 'xpluscurrent':
                i2c.writeto(eps, bytes([0x07]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0006103516
                return result
            elif param == 'yvolts':
                i2c.writeto(eps, bytes([0x08]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0024414063
                return result
            elif param == 'ymincurrent':
                i2c.writeto(eps, bytes([0x09]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0006103516
                return result
            elif param == 'ypluscurrent':
                i2c.writeto(eps, bytes([0x0A]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0006103516
                return result
            elif param == 'zvolts':
                i2c.writeto(eps, bytes([0x0B]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0024414063
                return result
            elif param == 'zmincurrent':
                i2c.writeto(eps, bytes([0x0C]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0006103516
                return result
            elif param == 'zpluscurrent':
                i2c.writeto(eps, bytes([0x0D]), stop=False)
                result = bytearray(2)
                i2c.readfrom_into(eps, result)
                result = int(result, 2)
                result *= 0.0006103516
                return result
            else:
                print("Error: please enter a valid command.")
        elif self.state == 'OFF':
            print("Power Systems are off, please turn system on to perform"
                  " the requested command.")
        else:
            print("Error: unexpected satellite state.")

    def commands(self, command):
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
        if (self.state == 'ON') or (self.state == 'ON_LOW_POWER'):
            if command == 'self_lock_on':
                i2c.writeto(eps, bytes([0x0001]), stop=False)
                print("self_lock command received")
            elif command == 'self_lock_off':
                i2c.writeto(eps, bytes([0x0000]), stop=False)
                print("self_lock command received")
            elif command == 'bus3v3_on':
                i2c.writeto(eps, bytes([0x0301]), stop=False)
                print("bus3v3 command received")
            elif command == 'bus3v3_off':
                i2c.writeto(eps, bytes([0x0300]), stop=False)
                print("bus3v3 command received")
            elif command == 'bus5v_on':
                i2c.writeto(eps, bytes([0x0401]), stop=False)
                print("bus5v command received")
            elif command == 'bus5v_off':
                i2c.writeto(eps, bytes([0x0400]), stop=False)
                print("bus5v command received")
            elif command == 'lup3v3_on':
                i2c.writeto(eps, bytes([0x0501]), stop=False)
                print("lup3v3 command received")
            elif command == 'lup3v3_off':
                i2c.writeto(eps, bytes([0x0500]), stop=False)
                print("lup3v3 command received")
            elif command == 'lup5v_on':
                i2c.writeto(eps, bytes([0x0601]), stop=False)
                print("lup5v command received")
            elif command == 'lup5v_off':
                i2c.writeto(eps, bytes([0x0600]), stop=False)
                print("lup5v command received")
            elif command == 'heater1_off':
                i2c.writeto(eps, bytes([0x1000]), stop=False)
                print("heater1 command received")
            elif command == 'heater1_on':
                i2c.writeto(eps, bytes([0x1001]), stop=False)
                print("heater1 command received")
            elif command == 'heater2_off':
                i2c.writeto(eps, bytes([0x1100]), stop=False)
                print("heater2 command received")
            elif command == 'heater2_on':
                i2c.writeto(eps, bytes([0x1101]), stop=False)
                print("heater2 command received")
            elif command == 'heater3_off':
                i2c.writeto(eps, bytes([0x1200]), stop=False)
                print("heater3 command received")
            elif command == 'heater3_on':
                i2c.writeto(eps, bytes([0x1201]), stop=False)
                print("heater3 command received")
            return
        elif self.state == 'OFF':
            print("Power Systems are off, please turn on system to perform"
                  " the requested command.")
        else:
            print("Error: unexpected satellite state")

    def power_state(self, state):
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
        THRESHOLD1 = 0           # Low power battery thresholds
        THRESHOLD2 = 0
        THRESHOLD3 = 0
        THRESHOLD4 = 0
        THRESHOLD5 = 0           # 0's are placeholders for actual values
        COMMS_BUS = 'bus3v3'     # Component bus locations
        MAG_BUS = 'bus3v3'
        GNSS_BUS = 'bus3v3'
        EUV_BUS = 'bus3v3'
        PY_BUS = 'bus3v3'
        BATTERY = self.measurements('voltage')

        if state == 'OFF':
            return

        if BATTERY <= THRESHOLD5:
            self.commands(PY_BUS + '_off')
            self.state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD4:
            self.commands(COMMS_BUS + '_off')
            self.state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD3:
            self.commands(MAG_BUS + '_off')
            self.state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD2:
            self.commands(GNSS_BUS + '_off')
            self.state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD1:
            self.commands(EUV_BUS + '_off')
            self.state = 'ON_LOW_POWER'
        else:
            self.state = 'ON_NORMAL'

        return self.state

state = State_machine()





