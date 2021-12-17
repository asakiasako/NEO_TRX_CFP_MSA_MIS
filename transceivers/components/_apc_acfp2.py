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
        self.__dut[0xD802][1:0] = 0b11 if en else 0

    def disable(self):
        return self.enable(en=False)

    def enable_soa_control(self, en=True):
        self.__dut[0xD802][1] = int(en)

    def disable_soa_control(self):
        return self.enable_soa_control(en=False)