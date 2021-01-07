from abc import ABC, abstractmethod
from .constants import HW_TYPE, HW_SIG_PINS
from ._utils import check_range
from ._types import RegisterValue, RegisterSequence
from collections.abc import Iterable
import re
import time
import math

class CfpMsaMis(ABC):
    def __init__(self, hw_type):
        """
        :Params:
            - **hw_type** - <enum 'HW_TYPE'> hardware type, CFP2/...
        """
        # information
        self.hw_type = hw_type
        # hardware pin map
        self.hw_pin = HW_SIG_PINS[hw_type]

    def __getitem__(self, position):
        if isinstance(position, int):
            if not 0 <= position <= 0xFFFF:
                raise IndexError('TWI register address should between 0x0000 and 0xFFFF.')
            reg_addr_bytes = position.to_bytes(2, 'big')
            int_value = int.from_bytes(self.read_mdio_register(reg_addr_bytes), 'big')
            return RegisterValue(position, int_value, self)
        if isinstance(position, slice):
            start, stop, step = position.start, position.stop, position.step
            if step is None:
                step = 1
            if step != 1:
                raise ValueError('step of slice should be 1. Only sequential register addresses are valid.')
            if not 0 <= start <= stop <= 0xFFFF:
                raise IndexError('MDIO register address should between 0x0000 and 0xFFFF.')
            list_data = []
            for _addr in range(start, stop+1):
                list_data.append(int.from_bytes(self.read_mdio_register(_addr.to_bytes(2, 'big')), 'big'))
            return RegisterSequence(list_data)
        if isinstance(position, str):
            if position in self.hw_pin:
                state = self.get_pin_state(position)
            else:
                raise KeyError('Invalid signal name: %s' % position)
            return state

        raise TypeError('indices should be int, str or slice')

    def __setitem__(self, position, value):
        if isinstance(position, int):
            if not 0 <= position <= 0xFFFF:
                raise IndexError('TWI register address should between 0x0000 and 0xFFFF.')
            if not isinstance(value, int):
                raise TypeError('Register value should be int')
            if not 0 <= value <= 0xFFFF:
                raise ValueError('TWI register value should between 0x0000 and 0xFFFF.')
            reg_addr_bytes = position.to_bytes(2, 'big')
            data_bytes = value.to_bytes(2, 'big')
            self.write_mdio_register(reg_addr_bytes, data_bytes)
        elif isinstance(position, str):
            if not isinstance(value, bool):
                raise TypeError('pin state setting value should be bool')
            if position in self.hw_pin:
                pin_name, writtable = self.hw_pin[position]
                if not writtable:
                    raise PermissionError('Module signal pin %s is read-only.' % position)
                return self.set_pin_state(pin_name, value)
            else:
                raise KeyError('Invalid signal pin name: %s' % position)
        elif isinstance(position, slice):
            start, stop, step = position.start, position.stop, position.step
            if step is None:
                step = 1
            if step != 1:
                raise ValueError('only sequential register addresses are valid.')
            if not 0 <= start <= stop <= 0xFFFF:
                raise IndexError('TWI register address should between 0x00 and 0xFF.')
            if not isinstance(value, int):
                raise TypeError('value should be int')
            data_len = stop - start + 1
            if isinstance(value, int):
                data_bytes = value.to_bytes(data_len*2, 'big')
            elif isinstance(value, Iterable):
                # other iterables
                list_bytes = [i.to_bytes(2, 'big') for i in value]
                data_bytes = b''.join(list_bytes)
            else:
                raise TypeError('value should be int, bytes, bytearray, or other Iterable of int.')
            if len(data_bytes) != data_len*2:
                raise ValueError('Length of slice and data do not match.')
            for _idx, _addr in enumerate(range(start, stop+1)):
                i_data = data_bytes[2*_idx: 2*_idx+2]
                self.write_mdio_register(_addr.to_bytes(2, 'big'), i_data)
        else:
            raise TypeError('indices should be int or str or slice')

    # BASIC FUNCTIONS (L1)
    # HW signal/CMIS generic signal management, TWI R/W operations
    # Some functions must be override when extended.
    @ abstractmethod
    def set_pin_state(self, pin_name, is_high_level):
        """
        pin_name: str, pin name defined in corresponding HW spec
        is_high_level: bool, True for high pin level and False for low pin level
        """

    @ abstractmethod
    def get_pin_state(self, pin_name):
        """
        pin_name: str, pin name defined in corresponding HW spec
        returns a bool, True for high pin level and False for low pin level
        """

    @ abstractmethod
    def write_mdio_register(self, addr, data):
        """
        random write of twi register.
        addr: bytes.
        data: bytes.
        """

    @ abstractmethod
    def read_mdio_register(self, addr):
        """
        random read of twi register
        addr: bytes.
        """
