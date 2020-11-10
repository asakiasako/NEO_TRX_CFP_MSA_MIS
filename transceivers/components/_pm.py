import struct

class Pm:

    def __init__(self, trx):
        self.__trx = trx
        self.__keys = (
            'Lane 0 Current Output Power', # dBm
            'Lane 0 Average Output Power', # dBm
            'Lane 0 Minimum Output Power', # dBm
            'Lane 0 Maximum Output Power', # dBm

            'Lane 0 Current Input Power',  # dBm
            'Lane 0 Average Input Power',  # dBm
            'Lane 0 Minimum Input Power',  # dBm
            'Lane 0 Maximum Input Power',  # dBm

            'FEC Corrected BER',
            'FEC Uncorrectable Codeword',
            'Lane 0 Average Output Power',
        )

    def __getitem__(self, key):
        return self.__get_pm(key)

    @property
    def keys(self):
        return self.__keys

    @property
    def INTERVAL_COMPLETE(self):
        return self.__trx[0xB023][2]

    @property
    def interval(self):
        return self.__trx[0xB00B][9:4] + 1

    @interval.setter
    def interval(self, seconds):
        if not isinstance(seconds, int) and seconds >= 1:
            raise ValueError('Invalid parameter: seconds={!r}'.format(seconds))
        self.__trx[0xB00B][9:4] = seconds - 1

    def __get_pm(self, key):
        if key not in self.keys:
            raise KeyError('Invalid key for DDM: {key}'.format(key=key))
        if key == 'Lane 0 Current Output Power':
            return self.__trx[0xB4A0].to_signed()*0.01
        if key == 'Lane 0 Average Output Power':
            return self.__trx[0xB4B0].to_signed()*0.01
        if key == 'Lane 0 Minimum Output Power':
            return self.__trx[0xB4C0].to_signed()*0.01
        if key == 'Lane 0 Maximum Output Power':
            return self.__trx[0xB4D0].to_signed()*0.01

        if key == 'Lane 0 Current Input Power':
            return self.__trx[0xB4E0].to_signed()*0.01
        if key == 'Lane 0 Average Input Power':
            return self.__trx[0xB4F0].to_signed()*0.01
        if key == 'Lane 0 Minimum Input Power':
            return self.__trx[0xB500].to_signed()*0.01
        if key == 'Lane 0 Maximum Input Power':
            return self.__trx[0xB510].to_signed()*0.01

        if key == 'FEC Corrected BER':
            b_9070 = self.__trx[0x9070].to_bytes(2, 'little')
            b_9071 = self.__trx[0x9071].to_bytes(2, 'little')
            return struct.unpack('<f', b_9071 + b_9070)[0]
        if key == 'FEC Uncorrectable Codeword':
            return self.__trx[0xB5C3]*2**16 + self.__trx[0xB5C4]
        if key == 'Lane 0 Average Output Power':
            return self.__trx[0xB5CE].to_signed()*0.01

        raise KeyError('Method to get DDM not exist: {key}'.format(key=key))
