from debugcolor import co

class Task:

    """
    The Task Object.
    Attributes:
        priority:    The priority level assigned to the task.
        frequency:   Number of times the task must be executed in 1 second (Hz).
        name:        Name of the task object for future reference
        color:       Debug color for serial terminal
    """

    priority = 10
    frequency = 1
    name = 'panel_current'
    color = 'gray'

    def __init__(self, satellite):
        """
        Initialize the Task using the PyCubed cubesat object.

        :type satellite: Satellite
        :param satellite: The cubesat to be registered
        """
        self.cubesat = satellite

    def debug(self,msg,level=1):
        """
        Print a debug message formatted with the task name and color
        :param msg: Debug message to print
        :param level: > 1 will print as a sub-level
        """
        if level==1:
            print('{:>30} {}'.format('['+co(msg=self.name,color=self.color)+']',msg))
        else:
            print('{}{}'.format('\t   └── ',msg))

    async def main_task(self):
        """
        Turns power buses off and on depending on the voltage level of the battery.
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

        if state == 'OFF':
            commands(PY_BUS + '_off')
            commands(EUV_BUS+ '_off')
            commands(GNSS_BUS + '_off')
            commands(MAG_BUS + '_off')
            commands(COMMS_BUS + '_off')
            print(measurements(BUS3V3), measurements(BUS5V))
        elif BATTERY <= THRESHOLD3:
            commands(PY_BUS + '_on')
            commands(EUV_BUS+ '_off')
            commands(GNSS_BUS + '_off')
            commands(MAG_BUS + '_off')
            commands(COMMS_BUS + '_off')
            print(measurements(BUS3V3), measurements(BUS5V))
            state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD2:
            commands(PY_BUS + '_on')
            commands(EUV_BUS+ '_off')
            commands(GNSS_BUS + '_off')
            commands(MAG_BUS + '_off')
            commands(COMMS_BUS + '_on')
            print(measurements(BUS3V3), measurements(BUS5V))
            state = 'ON_LOW_POWER'
        elif BATTERY <= THRESHOLD1:
            commands(PY_BUS + '_on')
            commands(EUV_BUS+ '_off')
            commands(GNSS_BUS + '_on')
            commands(MAG_BUS + '_on')
            commands(COMMS_BUS + '_on')
            print(measurements(BUS3V3), measurements(BUS5V))
            state = 'ON_LOW_POWER'
        else:
            commands(PY_BUS + '_on')
            commands(EUV_BUS+ '_on')
            commands(GNSS_BUS + '_on')
            commands(MAG_BUS + '_on')
            commands(COMMS_BUS + '_on')
            print(self.measurements(BUS3V3), self.measurements(BUS5V))
            state = 'ON_NORMAL'
