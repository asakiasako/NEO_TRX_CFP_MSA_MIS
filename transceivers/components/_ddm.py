class Ddm:

    def __init__(self, trx):
        self.__trx = trx
        self.__keys = (
            'Module Temperature',   # C
            'Supply Voltage',   # V
            'Network Lane 0 RX Input Power',   # mW
        )
    
    def __getitem__(self, key):
        return self.__get_ddm(key)

    @property
    def keys(self):
        return self.__keys

    def __get_ddm(self, key):
        if key not in self.keys:
            raise KeyError('Invalid key for DDM: {key}'.format(key=key))
        if key == 'Module Temp':
            return self.__trx[0xB02F].to_signed()/256
        if key == 'Module Power Supply':
            return self.__trx[0xB030]*10**(-3)
        if key == 'Network Lane 0 RX Input Power':
            return self.__trx[0xB350]*0.1*10**(-3)
        
        raise KeyError('Method to get DDM not exist: {key}'.format(key=key))
