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
        )

    def __getitem__(self, key):
        return self.__get_pm(key)

    @property
    def keys(self):
        return self.__keys

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

        raise KeyError('Method to get DDM not exist: {key}'.format(key=key))
