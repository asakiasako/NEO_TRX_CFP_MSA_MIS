import time

class DDB(object):

    def __init__(self, dut):
        self._dut = dut
        self.__default_max_count = 100  # 0.1s delay before each try.

    def idle(self):
        val = self._dut[0x9c00]
        return val == 0x0001

    def cip(self):
        val = self._dut[0x9c00]
        return val & 0xff00 == 0x0200

    def cip_or_idle(self):
        val = self._dut[0x9c00]
        return (val & 0xff00 == 0x0200) or (val == 0x0001)

    def cip_with_res(self):
        val = self._dut[0x9c00]
        return val & 0xff00 == 0x0200, val

    def success(self):
        val = self._dut[0x9c00]
        return val & 0xff00 == 0x0100

    def wait_for_complete(self, max_count=None):
        """
        max_count: period = 0.1s
        """
        max_count = max_count or self.__default_max_count
        _count = 0
        while self.cip_or_idle():
            if _count >= max_count:
                raise ValueError('Check ddb cip_or_idle failed after %d attempts.' % max_count)
            _count += 1
            time.sleep(0.1)

    def wait_for_idle(self, max_count=None):
        """
        max_count: period = 0.1s
        """
        max_count = max_count or self.__default_max_count
        _count = 0
        while not self.idle():
            if _count >= max_count:
                raise ValueError('Check ddb idle failed after %d attempts.' % max_count)
            _count += 1
            time.sleep(0.1)

    def wait_for_success(self, max_count=None):
        max_count = max_count or self.__default_max_count
        _count = 0
        while not self.success():
            if _count >= max_count:
                raise ValueError('Check ddb success failed after %d attempts.' % max_count)
            _count += 1
            time.sleep(0.1)