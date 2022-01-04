import struct
from collections import namedtuple
import time

__all__ = ["DAC"]

DAC_KEYS = (
    "TX_VOA_DAC",
    "DRV_4V_DAC",
    "TEC_DAC",

    "OA_XI",
    "OA_XQ",
    "OA_YI",
    "OA_YQ",

    "SOA_DAC",
    "RX_VOA_DAC",

    "TRACE_R",

    "RX_LOS_TH_DAC",
    "MOD_VBX_DAC",
    "MOD_VBY_DAC",
    "PH_XI_AC_DAC",
    "PH_XQ_AC_DAC",
    "PH_YI_AC_DAC",
    "PH_YQ_AC_DAC",
    "PH_XP_AC_DAC",
    "PH_YP_AC_DAC",
    "SOA_PW_DAC",

    "PH_XI_DAC",
    "PH_XQ_DAC",
    "PH_XP_DAC",
    "PH_YI_DAC",
    "PH_YQ_DAC",
    "PH_YP_DAC",
    "EQ_XP_DAC",
    "EQ_YP_DAC",

    "ABC_VGA_R",
)

DACValue = namedtuple("DACValue", "d_val a_val")

class DAC:
    """
    Usage:
    dac[key] => <DACValue object>
    returns an DACValue object, which has d_val/a_val property.
    dac[key].d_val => int
    dac[key].a_val => float

    dac[key] = int   # set d_val
    dac[key] = float # set a_val
    dac[key] = value, type  # set with a tuple with data type define, type of 'value' ignored (can pass int to a_val)
    # value: float|int, type: 'd'=d_val, 'a'=a_val, 
    """
    def __init__(self, dut):
        self.__dut = dut
        self.__keys = DAC_KEYS

    def keys(self):
        return self.__keys

    def __getitem__(self, key):
        try:
            dac_index = self.keys().index(key)
        except ValueError:
            raise KeyError('%s. Not a valid DAC key.' % key)
        return self.__get_val(dac_index)
    
    def __setitem__(self, key, value):
        try:
            dac_index = self.keys().index(key)
        except ValueError:
            raise KeyError('%s. Not a valid DAC key.' % key)

        if isinstance(value, int):
            self.__set_dval(dac_index, value)
        elif isinstance(value, float):
            self.__set_aval(dac_index, value)
        elif isinstance(value, (tuple, list)):
            val, val_type = value
            if val_type == 'd':
                self.__set_dval(dac_index, val)
            elif val_type == 'a':
                self.__set_aval(dac_index, val)
            else:
                raise ValueError('Invalid value type.')
        else:
            raise TypeError('value should be int or float or tuple|list.')

    def __get_val(self, dac_index):
        self.__dut.ddb.wait_for_idle()
        
        self.__dut[0x9c02] = dac_index
        self.__dut[0x9c01] = 1
        self.__dut[0x9c00] = 0x0f05

        self.__dut.ddb.wait_for_complete()

        if 4 == self.__dut[0x9c01] and dac_index == self.__dut[0x9c02]:            
            _dval = self.__dut[0x9c03]
            val1 = self.__dut[0x9c04]
            val2 = self.__dut[0x9c05]
            _aval_bytes = val1.to_bytes(2, 'little') + val2.to_bytes(2, 'little')
            _aval = struct.unpack('<1f', _aval_bytes)[0]
        else:
            _dval = 0
            _aval = 0.0
            
        return DACValue(d_val=_dval, a_val=_aval)

    def __set_dval(self, dac_index, value):
        if not isinstance(value, int):
            raise TypeError('Digital value of DAC should be int.')
        
        self.__dut.ddb.wait_for_idle()

        self.__dut[0x9c02] = dac_index
        self.__dut[0x9c03] = value
        self.__dut[0x9c01] = 2
        self.__dut[0x9c00] = 0x0f05

        self.__dut.ddb.wait_for_complete()

    def __set_aval(self, dac_index, value):
        if not isinstance(value, (int, float)):
            raise TypeError('Analog value of DAC should be a number.')
        
        value_bytes = struct.pack('>1f', value)

        self.__dut.ddb.wait_for_idle()

        self.__dut[0x9c02] = dac_index
        self.__dut[0x9c03] = int.from_bytes(value_bytes[2:], 'big') 
        self.__dut[0x9c04] = int.from_bytes(value_bytes[:2], 'big') 
        self.__dut[0x9c01] = 3
        self.__dut[0x9c00] = 0x0f05

        self.__dut.ddb.wait_for_complete()
