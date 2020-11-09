import serial
import enum

DEFAULT_PORT_CONFIG = {
    "baudrate": 115200, 
    "bytesize": serial.EIGHTBITS,
    "stopbits": serial.STOPBITS_ONE,
    "parity": serial.PARITY_NONE,
    "timeout": 2,  # seconds
}

# define pins
@ enum.unique
class CONTROL_PIN(enum.Enum):
    MOD_RSTn = 0
    MOD_LOPWR = 1
    TX_DIS = 2
    # 3 is undefined
    PRG_CNTL3 = 4
    PRG_CNTL2 = 5
    PRG_CNTL1 = 6
    # 7 is undefined

CONTROL_PIN_CMD_LIST = [
    'MRST',     # 0
    'LPW',      # 1
    'TXD',      # 2
    None,       # 3
    'PCNTL3',   # 4
    'PCNTL2',   # 5
    'PCNTL1',   # 6
]

@ enum.unique
class ALARM_PIN(enum.Enum):
    PRG_ALRM1 = 0
    PRG_ALRM2 = 1
    PRG_ALRM3 = 2
    RX_LOS = 3
    MOD_ABS = 4
    GLB_ALRMn = 5
    # 6 is undefined
    # 7 is undefined

ALARM_PIN_CMD_LIST = [
    'PALRM1',   # 0
    'PALRM2',   # 1
    'PALRM3',   # 2
    'RXLOS',    # 3
    'MABS',     # 4
    'GALRM',    # 5
]