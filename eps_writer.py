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

    async def main_task(self, command):
        """
        Provides framework for using write commands on the EPS.
        """
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

        if self.state == State.ON or self.state == State.ON_LOW_POWER:
            try:
                i2c.writeto(eps, bytes(response_dict[command]), stop=False)
            except KeyError(e):
                print(f"Command {command} does not exist!")
        else:
            return "Satellite is off."
