from debugcolor import co
import board

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
        msg = params
        if level==1:
            print('{:>30} {}'.format('['+co(msg=self.name,color=self.color)+']',msg))
        else:
            print('{}{}'.format('\t   └── ',msg))

    async def main_task(self):
        """
        Returns the voltages and plus/minus axes currents for each face of the cubesat in a list.
        """
        eps = 0x18
        i2c = board.I2C()

        params = [(Read.XVOLTS, xvolts), (Read.XMINCURRENT, xmincurrent),
                  (Read.XPLUSCURRENT, xpluscurrent), (Read.YVOLTS, yvolts),
                  (Read.YMINCURRENT, ymincurrent), (Read.YPLUSCURRENT, ypluscurrent),
                  (Read.ZVOLTS, zvolts), (Read.ZPLUSCURRENT, zpluscurrent)]

        for param in params:
            param[1] = 0

        response_dict: Dict[str, Tuple[List[int], Callable[int, float]]] = {
            Read.XVOLTS: ([0x300531], lambda r: r * 0.0024414063),
            Read.XMINCURRENT: ([0x300631], lambda r: r * 0.0006103516),
            Read.XPLUSCURRENT: ([0x300731], lambda r: r * 0.0006103516),
            Read.YVOLTS: ([0x300831], lambda r: r * 0.0024414063),
            Read.YMINCURRENT: ([0x300931], lambda r: r * 0.0006103516),
            Read.YPLUSCURRENT: ([0x300A31], lambda r: r * 0.0006103516),
            Read.ZVOLTS: ([0x300B31], lambda r: r * 0.0024414063),
            Read.ZPLUSCURRENT: ([0x300D31], lambda r: r * 0.0006103516)
        }

        if self.state == State.ON_NORMAL or self.state == State.ON_LOW_POWER:
            for param in params:
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


