import enum
from types import MappingProxyType
from collections import namedtuple

@ enum.unique
class HW_TYPE(enum.Enum):
    CFP = 0
    CFP2 = 1
    CFP4 = 2
    CFP8 = 3


HwSigPin = namedtuple('HwSigPin', 'pin_name writtable')
# pin_name: name of hardware signal pin, exactly the same as defined in
# corresponding form factor specification.
# writtable: if hardware signal can be set.

HW_SIG_PINS = MappingProxyType({
    HW_TYPE.CFP: MappingProxyType({
        # Control Pins
        'MOD_RSTn': HwSigPin('MOD_RSTn', writtable=True),
        'MOD_LOPWR': HwSigPin('MOD_LOPWR', writtable=True),
        'TX_DIS': HwSigPin('TX_DIS', writtable=True),
        'PRG_CNTL1': HwSigPin('PRG_CNTL1', writtable=True),
        'PRG_CNTL2': HwSigPin('PRG_CNTL2', writtable=True),
        'PRG_CNTL3': HwSigPin('PRG_CNTL3', writtable=True),
        # Alarm Pins
        'RX_LOS': HwSigPin('RX_LOS', writtable=False),
        'MOD_ABS': HwSigPin('MOD_ABS', writtable=False),
        'GLB_ALRMn': HwSigPin('GLB_ALRMn', writtable=False),
        'PRG_ALRM1': HwSigPin('PRG_ALRM1', writtable=False),
        'PRG_ALRM2': HwSigPin('PRG_ALRM2', writtable=False),
        'PRG_ALRM3': HwSigPin('PRG_ALRM3', writtable=False),
    }),
    HW_TYPE.CFP2: MappingProxyType({
        # Control Pins
        'MOD_RSTn': HwSigPin('MOD_RSTn', writtable=True),
        'MOD_LOPWR': HwSigPin('MOD_LOPWR', writtable=True),
        'TX_DIS': HwSigPin('TX_DIS', writtable=True),
        'PRG_CNTL1': HwSigPin('PRG_CNTL1', writtable=True),
        'PRG_CNTL2': HwSigPin('PRG_CNTL2', writtable=True),
        'PRG_CNTL3': HwSigPin('PRG_CNTL3', writtable=True),
        # Alarm Pins
        'RX_LOS': HwSigPin('RX_LOS', writtable=False),
        'MOD_ABS': HwSigPin('MOD_ABS', writtable=False),
        'GLB_ALRMn': HwSigPin('GLB_ALRMn', writtable=False),
        'PRG_ALRM1': HwSigPin('PRG_ALRM1', writtable=False),
        'PRG_ALRM2': HwSigPin('PRG_ALRM2', writtable=False),
        'PRG_ALRM3': HwSigPin('PRG_ALRM3', writtable=False),
    }),
    HW_TYPE.CFP4: MappingProxyType({
        # TBD
    }),
    HW_TYPE.CFP8: MappingProxyType({
        # TBD
    }),
})
