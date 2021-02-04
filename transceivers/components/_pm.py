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

            'Lane 0 Current SNR',
            'Lane 0 Average SNR',
            'Lane 0 Minimum SNR',
            'Lane 0 Maximum SNR',

            'Lane 0 Current CD',
            'Lane 0 Average CD',
            'Lane 0 Minimum CD',
            'Lane 0 Maximum CD',

            'Lane 0 Current DGD',
            'Lane 0 Average DGD',
            'Lane 0 Minimum DGD',
            'Lane 0 Maximum DGD',

            'Lane 0 Current PDL',
            'Lane 0 Average PDL',
            'Lane 0 Minimum PDL',
            'Lane 0 Maximum PDL',

            'Lane 0 Current Q',
            'Lane 0 Average Q',
            'Lane 0 Minimum Q',
            'Lane 0 Maximum Q',

            'Lane 0 Current CFO',  # MHz
            'Lane 0 Average CFO',
            'Lane 0 Minimum CFO',
            'Lane 0 Maximum CFO',

            'FEC Corrected BER',
            'FEC Uncorrectable Codeword',
            'Lane 0 Input Signal Power',
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

        if key == 'Lane 0 Current CD':
            raw = self.__trx[0xB800] * 0x10000 + self.__trx[0xB810]
            return raw if raw < 0x80000000 else (raw - 0x100000000)
        if key == 'Lane 0 Average CD':
            raw = self.__trx[0xB820] * 0x10000 + self.__trx[0xB830]
            return raw if raw < 0x80000000 else (raw - 0x100000000)
        if key == 'Lane 0 Minimum CD':
            raw = self.__trx[0xB840] * 0x10000 + self.__trx[0xB850]
            return raw if raw < 0x80000000 else (raw - 0x100000000)
        if key == 'Lane 0 Maximum CD':
            raw = self.__trx[0xB860] * 0x10000 + self.__trx[0xB870]
            return raw if raw < 0x80000000 else (raw - 0x100000000)

        if key == 'Lane 0 Current DGD':
            return self.__trx[0xB880]
        if key == 'Lane 0 Average DGD':
            return self.__trx[0xB890]
        if key == 'Lane 0 Minimum DGD':
            return self.__trx[0xB8A0]
        if key == 'Lane 0 Maximum DGD':
            return self.__trx[0xB8B0]

        if key == 'Lane 0 Current SNR':
            return self.__trx[0xBA00]*0.1
        if key == 'Lane 0 Average SNR':
            return self.__trx[0xBA10]*0.1
        if key == 'Lane 0 Minimum SNR':
            return self.__trx[0xBA20]*0.1
        if key == 'Lane 0 Maximum SNR':
            return self.__trx[0xBA30]*0.1

        if key == 'Lane 0 Current PDL':
            return self.__trx[0xB940]*0.1
        if key == 'Lane 0 Average PDL':
            return self.__trx[0xB950]*0.1
        if key == 'Lane 0 Minimum PDL':
            return self.__trx[0xB960]*0.1
        if key == 'Lane 0 Maximum PDL':
            return self.__trx[0xB970]*0.1

        if key == 'Lane 0 Current Q':
            return self.__trx[0xB980]*0.1
        if key == 'Lane 0 Average Q':
            return self.__trx[0xB990]*0.1
        if key == 'Lane 0 Minimum Q':
            return self.__trx[0xB9A0]*0.1
        if key == 'Lane 0 Maximum Q':
            return self.__trx[0xB9B0]*0.1

        if key == 'Lane 0 Current CFO':
            return self.__trx[0xB9C0]
        if key == 'Lane 0 Average CFO':
            return self.__trx[0xB9D0]
        if key == 'Lane 0 Minimum CFO':
            return self.__trx[0xB9E0]
        if key == 'Lane 0 Maximum CFO':
            return self.__trx[0xB9F0]

        if key == 'FEC Corrected BER':
            b_9070 = self.__trx[0x9070].to_bytes(2, 'little')
            b_9071 = self.__trx[0x9071].to_bytes(2, 'little')
            return struct.unpack('<f', b_9071 + b_9070)[0]
        if key == 'FEC Uncorrectable Codeword':
            return self.__trx[0xB5C3]*2**16 + self.__trx[0xB5C4]
        if key == 'Lane 0 Input Signal Power':
            return self.__trx[0xB5CF].to_signed()*0.01

        raise KeyError('Method to get PM not exist: {key}'.format(key=key))
