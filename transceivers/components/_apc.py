import time

__all__ = ['APC']

class APC:
    """
    apc.enable(en=True)
    apc.disable()
    """
    def __init__(self, dut):
        self.__dut = dut

    def enable(self, en=True):
        self.__dut[0x907B] = int(en)

    def disable(self):
        return self.enable(en=False)
