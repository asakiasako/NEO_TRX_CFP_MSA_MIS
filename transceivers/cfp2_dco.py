from ..evb import CFP2DcoEVB
from ..cfp_msa import CfpMsaMis, HW_TYPE
from .components._adc import ADC
from .components._dac import DAC
from .components._apc import APC
from .components._ddb import DDB
from .components._dsp import DSP
from .components._ddm import Ddm
from .components._pm import Pm
import time
import math

class TRx_CFP2DCO(CfpMsaMis):
    def __init__(self, comport=None, hw_type=HW_TYPE.CFP2):
        CfpMsaMis.__init__(self, hw_type)
        self.__evb = CFP2DcoEVB(port=comport)
        self.__adc = ADC(self)
        self.__adc = DAC(self)
        self.__apc = APC(self)
        self.__ddb = DDB(self)
        self.__dsp = DSP(self)
        self.__ddm = Ddm(self)
        self.__pm = Pm(self)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __repr__(self):
        return '<{classname} port={port}>'.format(classname=self.__class__.__name__, port=self.port)

    @property
    def port(self):
        return self.__evb.port

    @port.setter
    def port(self, val):
        self.__evb.port = val

    @property
    def adc(self):
        return self.__adc

    @property
    def dac(self):
        return self.__adc

    @property
    def apc(self):
        return self.__apc
    
    @property
    def ddb(self):
        return self.__ddb

    @property
    def dsp(self):
        return self.__dsp

    @property
    def ddm(self):
        return self.__ddm

    @property
    def pm(self):
        return self.__pm

    def connect(self):
        self.__evb.connect()

    def disconnect(self):
        self.__evb.disconnect()

    @property
    def is_connected(self):
        return self.__evb.is_connected

    def set_pin_state(self, pin_name, is_high_level):
        self.__evb.set_control_pin(self.__evb.CONTROL_PIN[pin_name], is_high_level)

    def get_pin_state(self, pin_name):
        if pin_name in self.__evb.CONTROL_PIN.__members__:
            return self.__evb.get_control_pin(self.__evb.CONTROL_PIN[pin_name])
        elif pin_name in self.__evb.ALARM_PIN.__members__:
            return self.__evb.get_alarm_pin(self.__evb.ALARM_PIN[pin_name])
        else:
            raise ValueError('invalid hardware pin_name')

    def write_mdio_register(self, addr, data):
        return self.__evb.write_mdio_register(addr, data)

    def read_mdio_register(self, addr):
        return self.__evb.read_mdio_register(addr)

    def get_vcc_setting(self):
        """
        return: <float> Vcc setting value
        """
        return self.__evb.get_vcc_setting()

    def get_vcc_monitor(self):
        """
        return: <float> Vcc monitor value
        """
        return self.__evb.get_vcc_monitored()

    def set_vcc(self, value):
        """
        value: <int|float> Vcc setting value
        """
        self.__evb.set_vcc(value)

    def get_icc_monitor(self):
        """
        return: <float> Icc monitor
        """
        return self.__evb.get_icc()

    def get_power_consumption(self):
        """
        return: <float> power consumption
        """
        return self.__evb.get_mod_power()

    # --- Applications ---
    def get_pn(self):
        return self[0x8034:0x8043].to_ascii_str().strip()

    def get_sn(self):
        return self[0x8044:0x8053].to_ascii_str().strip()

    def get_fw_version(self):
        self.ddb.wait_for_idle()
        self[0x9c00] = 0x0f01
        self.ddb.wait_for_success()
        if 6 == self[0x9c01]:
            if 1 == self[0x9c02]:
                _a_image = hex((self[0x9c04] << 16) | self[0x9c05])
            else:
                _a_image = 'INVALID'
            if 1 == self[0x9c03]:
                _b_image = hex((self[0x9c06] << 16) | self[0x9c07])
            else:
                _b_image = 'INVALID'
        else:
            _a_image = _b_image = 'INVALID'
        
        return {'A': _a_image, 'B': _b_image}

    def write_password(self, psw=0x01011100):
        '''
        Write password to Password Entry Area.
        If psw is not explicitly defined, default host system manufacturer 
        password 0x00001011 is write.
        '''
        self[0xB000:0xB001] = psw

    def get_module_state(self):
        # 0.00h.3.3-1
        state_code = self[0xB016]
        state_code_map = {
            0x0001: 'Initialize',
            0x0002: 'Low-Power',
            0x0004: 'High-Power-up',
            0x0008: 'TX-Off',
            0x0010: 'TX-Turn-on',
            0x0020: 'Ready',
            0x0040: 'Fault',
            0x0080: 'TX-Turn-off',
            0x0100: 'High-Power-down',
        }
        return state_code_map.get(state_code, 'Undefined: 0x{:04X}'.format(state_code))

    def get_frequency_channel(self, lane):
        """
        * lane: <int> lane
        return:
            * ch_num: <int> channel number
        """
        return self[0xB400+lane][9:0].to_unsigned()

    def set_frequency_channel(self, lane, ch_num):
        """
        * lane: <int> lane
        * ch_num: <int> channel number
        """
        self[0xB400 + lane][9: 0] = ch_num

    def set_tx_fine_tune(self, lane, offset):
        """
        * lane: <int> lane
        * offset: <int> GHz
        """
        if not -5 <= offset <= 5:
            raise ValueError('Fine tune value out of range: {offset}GHz'.format(offset=offset))
        offset = round(offset*1000)
        raw = offset if offset >= 0 else 0x10000+offset
        self[0xB430+lane] = raw

    def set_rx_fine_tune(self, lane, offset):
        """
        * lane: <int> lane
        * offset: <int> GHz
        """
        if not -5 <= offset <= 5:
            raise ValueError('Fine tune value out of range: {offset}GHz'.format(offset=offset))
        offset = round(offset*1000)
        raw = offset if offset >= 0 else 0x10000+offset
        self[0xB440+lane] = raw

    def get_current_frequency(self, lane):
        """
        * lane: <int> lane
        return:
            * <float> frequency in THz
        """
        freq1 = self[0xB450]
        freq2 = self[0xB460]
        freq = freq1 + 0.05*freq2/1000  # THz
        return freq
