import collections
from ._utils import check_range, check_type
from collections import Sequence


# this class extends int, and add some methods to suit reg-map
class RegisterValue(int):
    """
    This type is to support slice operator in register value.
    """
    def __init__(self, reg_addr, value, cfp_msa_mis_obj):
        super(RegisterValue, self).__init__()
        self.__reg_addr = reg_addr
        self.__value = value
        self.__cfp_msa_mis_obj = cfp_msa_mis_obj

    def __new__(cls, reg_addr, value, cfp_msa_mis_obj):
        return super(RegisterValue, cls).__new__(cls, value)

    def __int__(self):
        return self.__value
        
    def __getitem__(self, position):
        if isinstance(position, slice):
            start, stop, step = position.start, position.stop, position.step
            if step or (start < stop):
                raise ValueError('slice for RegisterValue should like reg_map_value[7:4]. start should be larger than stop, and step param is not allowed.')
            if not (15 >= start >= stop >= 0):
                raise ValueError('bit index out of range 0 to 15.')
            else:
                bits_val = ((2**(start+1)-1) & self.__value) >> stop
                return bits_val
        elif isinstance(position, int):
            check_range(position, 0, 15)
            return self.__value >> position & 1
        else:
            raise TypeError('indices should be int or slice')

    def __setitem__(self, position, value):
        if isinstance(position, slice):
            start, stop, step = position.start, position.stop, position.step
            if step or (start < stop):
                raise ValueError('slice for RegisterValue should like value[7:4]. start should be larger than stop, and step param is not allowed.')
            if not (15 >= start >= stop >= 0):
                raise ValueError('bit index out of range 0 to 15.')
            check_type(value, int)
            if not 0 <= value <= 2**(start-stop+1) - 1:
                raise ValueError('value out of range for bit_width=%d' % (start-stop+1))

            origin_data = self.__value
            result_data = ((2**(start-stop+1)-1) << stop ^ (2 ** 16 -1)) & origin_data | (value << stop)

            self.__cfp_msa_mis_obj[self.__reg_addr] = result_data
        elif isinstance(position, int):
            check_range(position, 0, 15)
            check_type(value, int)
            check_range(value, 0, 1)

            origin_data = self.__value
            result_data = ((1 << position) ^ (2 ** 16 -1)) & origin_data | (value << position)

            self.__cfp_msa_mis_obj[self.__reg_addr] = result_data
        else:
            raise TypeError('indices should be int or slice')

    def to_signed(self):
        return int(self) if self < 0x10000/2 else self-0x10000


class RegisterSequence(Sequence):
    """
    A list of RegisterValue objects with several additional util methods.
    """
    def __new__(cls, seq, *args, **kwargs):
        # check register values
        for i, v in enumerate(seq):
            if not isinstance(v, int):
                raise TypeError('Invalid type of RegisterSequence[{idx:d}]={val!r}. Should be int.'.format(idx=i, val=v))
            if not 0 <= v < 0xFFFF:
                raise ValueError('Invalid value of RegisterSequence[{idx:d}]={val!r}. Range: 0<=val<=0xFFFF'.format(idx=i, val=v))
        obj = super(RegisterSequence, cls).__new__(cls)
        obj.__data = tuple(seq)
        return obj

    def __repr__(self):
        return '<RegisterSequence: ({str_data})>'.format(str_data=', '.join('0x{:04X}'.format(i) for i in self.__data))

    def __getitem__(self, idx):
        return self.__data[idx]

    def __len__(self):
        return len(self.__data)

    def to_unsigned(self):
        return int.from_bytes(self.to_bytes(), 'big')

    def to_signed(self):
        length = len(self)
        unsigned = self.to_unsigned()
        value = unsigned if unsigned < 0x10000**length/2 else unsigned-0x10000 ** length
        return value

    def to_ascii_str(self):
        return ''.join([chr(i) for i in self.__data])
