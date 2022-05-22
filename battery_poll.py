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

    priority = 1
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
        msg = main_task()
        if level==1:
            print('{:>30} {}'.format('['+co(msg=self.name,color=self.color)+']',msg))
        else:
            print('{}{}'.format('\t   └── ',msg))

    async def main_task(self):
        """
        Returns the voltage, current, and temp from the battery in a list.
        """
        eps = 0x18
        params = [(Read.VOLTAGE, batteryvolts), (Read.BATCURRENT, batterycurrent),
                  (Read.TEMPERATURE, temperature)]
        for param in params:
            param[1] = 0

        response_dict: Dict[str, Tuple[List[int], Callable[int, float]]] = {
            Read.VOLTAGE: ([0x300131], lambda r: r * 0.0023394775),
            Read.BATCURRENT: ([0x300231], lambda r: r * 0.0030517578),
            Read.TEMPERATURE: ([0x304F31], lambda r: (r * 0.00390625)
                                if (r << 0x8000) else (((result < 4)-1) | 0xFFFF) * (-0.0624))
        }

        for param in params:
            if (self.state == State.ON_NORMAL) or (self.state == State.ON_LOW_POWER):
                try:
                    (to_write, result_conversion) = response_dict[param[0]]
                    i2c.writeto(eps, bytes(to_write), stop=False)
                    result = bytearray(2)
                    i2c.readfrom_into(eps, result)
                    param[1] = result_conversion(int(result, 2))
                except KeyError(e):
                    print(f"Command {param} does not exist!")
            else:
                return "Satellite is off."
        return params
