from collections import namedtuple
import time
import struct

__all__ = ["ADC"]

ADC_KEYS = (
    "ICR_3V3_ADC",
    "PI_XI",
    "PI_YI",
    "PI_YQ",
    "RX_MPD_ADC",
    "MPD_AC_ADC",
    "PI_XQ",
    "MOD_THERM_ADC",
    "MPD_DC_ADC",
    "DRV_4V_ADC",
    "MCU1INTERNAL_TEMP",
    "MCU1INTERNAL_VREFP",
    "MCU1INTERNAL_PVDD",
    "MCU1INTERNAL_IOVDD_2",
    "MCU1INTERNAL_AVDD_2",
    "MCU1INTERNAL_VREFN",
    "GA_XI",
    "GA_XQ",
    "GA_YI",
    "GA_YQ",
    "CASE_THM_ADC",
    "PCB_TEMP_ADC",
    "IN_3V3_ADC",
    "DUMMY1",
    "DUMMY2",
    "HW_VER_ADC",
    "N15V_ADC",
    "DRV_3V3_ADC",
    "RX_5V_ADC",
    "TX_5V_ADC",
    "N2V5_ADC",
    "DSP_VDD_ADC",
    "DSP_VDDA_ADC",
    "DSP_VDDA12_ADC",
    "DSP_VDDIO18_ADC",
    "DSP_VDDM_ADC",
    "MZ_MPD1_DC_ADC",
    "MZ_MPD1_AC_ADC",
)

ADCValue = namedtuple("ADCValue", "d_val a_val")

class ADC:
    """
    Usage:
    adc[key] => <ADCValue object>
    returns an ADCValue object, which has d_val/a_val property.
    adc[key].d_val = int
    adc[key].a_val = float
    """
    def __init__(self, dut):
        self.__dut = dut
        self.__keys = ADC_KEYS

    def keys(self):
        return self.__keys

    def __getitem__(self, key):
        try:
            adc_index = self.keys().index(key)
        except ValueError:
            raise KeyError('%s. Not a valid ADC key.' % key)
        return self.__get_val(adc_index)

    def __get_val(self, adc_index):
        self.__dut.ddb.wait_for_idle()
        
        self.__dut[0x9c02] = adc_index
        self.__dut[0x9c01] = 1
        self.__dut[0x9c00] = 0x0f04

        self.__dut.ddb.wait_for_complete()

        if 4 == self.__dut[0x9c01] and adc_index == self.__dut[0x9c02]:            
            _dval = self.__dut[0x9c03]
            val1 = self.__dut[0x9c04]
            val2 = self.__dut[0x9c05]
            _aval_bytes = val1.to_bytes(2, 'little') + val2.to_bytes(2, 'little')
            _aval = struct.unpack('<1f', _aval_bytes)[0]
        else:
            _dval = 0
            _aval = 0.0
            
        return ADCValue(d_val=_dval, a_val=_aval)
