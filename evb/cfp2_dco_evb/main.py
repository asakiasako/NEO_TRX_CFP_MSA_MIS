from .constants import DEFAULT_PORT_CONFIG, CONTROL_PIN, ALARM_PIN, CONTROL_PIN_CMD_LIST, ALARM_PIN_CMD_LIST
import threading
import re
import serial
import time

query_lock = threading.Lock()


class CFP2DcoEVB(object):
    CONTROL_PIN = CONTROL_PIN
    ALARM_PIN = ALARM_PIN

    class QueryError(Exception):
        """
        Raised when unexpected reply is get in quering operation.
        """
        def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)

    def __init__(self, port=None, timeout=None, **kwargs):
        """
        **kwargs: These params will be passed directly to serial.Serial().__init__().
                  if a param not set, DEFAULT_PORT_CONFIG will be used. 
        """
        port_config = DEFAULT_PORT_CONFIG
        port_config.update(kwargs)
        self._serial = serial.Serial(**port_config)
        if timeout:
            self._serial.timeout = timeout  # default is 2s
        if port:
            self._serial.port = port

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        When release port when connection ends.
        """
        self.disconnect()
    
    def __write_cmd_operation(self, cmd, write_termination='\r\n'):
        """
        cmd: <str> cmd in str. no need to add prefix '*' or postfix '\r\n'
        """
        complete_cmd = ('*%s%s' % (cmd, write_termination)).encode()
        time.sleep(0.0002)
        self._serial.reset_input_buffer()
        self._serial.write(complete_cmd)
        # read cmd sent back by host and check
        reply = self._serial.readline().decode().strip().strip('*')
        if reply != 'received':
            raise self.QueryError('Unexpected reply from host board. Reply: "{reply}", Expected: "received"'.format(reply=reply))

    def __read_reply_operation(self):
        """
        return: <str> reply in str. useless information will not include.
        """
        time.sleep(0.0002)
        full_reply = self._serial.readline().decode().strip()
        m = re.match(r'\$(\w{4});(<[\w*\- ]*>){0,1}(.*)', full_reply)
        if not m:
            raise self.QueryError('Unexpected reply from host board. Reply: %s' % full_reply)
        err_code = m.group(1)
        if err_code != '0000':
            raise ValueError('EVB Error Code: %s' % err_code, err_code)
        reply = m.group(3)
        if self._serial.read(1) != b'>':
            raise ValueError('Unexpected reply after read operation.')
        return reply

    def _write_cmd(self, cmd, write_termination='\r\n'):
        """
        cmd: <str> cmd in str. no need to add prefix '*' or postfix '\r\n'
        """
        global query_lock
        lock = query_lock
        lock.acquire()
        try:
            self.__write_cmd_operation(cmd, write_termination)
            self.__read_reply_operation()
        finally:
            lock.release()

    def _query(self, cmd, write_termination='\r\n'):
        """
        cmd: <str> cmd in str. no need to add prefix '*' or postfix '\r\n'
        return: <str> reply in str. useless information will not include.
        """
        # acquire lock to ensure correct reply
        global query_lock
        lock = query_lock
        lock.acquire()
        try:
            self.__write_cmd_operation(cmd, write_termination)
            return_value = self.__read_reply_operation()
        finally:
            lock.release()
        return return_value

    @ property
    def port(self):
        return self._serial.port

    @ port.setter
    def port(self, value):
        if self.is_connected:
            raise PermissionError('Could not change port when transceiver is connected.')
        self._serial.port = value

    @ property
    def timeout(self):
        return self._serial.timeout

    @ timeout.setter
    def timeout(self, value):
        self._serial.timeout = value

    def connect(self):
        if not self.port:
            raise ValueError('Port name is not defined.')
        self._serial.open()

    def disconnect(self):
        self._serial.close() 

    @ property
    def is_connected(self):
        return self._serial.is_open

    def check_communication(self):
        try:
            self._query('Check Connection')
        except self.QueryError:
            return False
        except ValueError as e:
            if e.args[1] == '0001':
                return True
            else:
                raise e
        else:
            raise ValueError('Unexpected reply when check_communication.')

    def get_control_pin_map(self):
        result_dict = {}
        for i in CONTROL_PIN:
            pin_state = self.get_control_pin(i)
            result_dict[i.name] = pin_state
        return result_dict

    def get_alarm_pin_map(self):
        result_dict = {}
        for i in ALARM_PIN:
            pin_state = self.get_alarm_pin(i)
            result_dict[i.name] = pin_state
        return result_dict

    def _get_pin(self, pin):
        """
        pin: <enum 'CNTL_PIN'> or <enum 'ALARM_PIN'>
        """
        if isinstance(pin, CONTROL_PIN):
            pin_cmd = CONTROL_PIN_CMD_LIST[pin.value]
        elif isinstance(pin, ALARM_PIN):
            pin_cmd = ALARM_PIN_CMD_LIST[pin.value]
        else:
            raise TypeError("pin should be <enum 'CTRL_PIN'> or <enum 'ALARM_PIN'>")
        reply = self._query('{pin_cmd} -g'.format(pin_cmd=pin_cmd))
        if int(reply, base=16) == 0:
            return False
        elif int(reply, base=16) == 1:
            return True
        else:
            raise ValueError('Unexpected data received: %r' % reply)

    def get_control_pin(self, cntl_pin):
        """
        cntl_pin: <enum 'CNTL_PIN'>
        :return: <boolean> High Voltage = True, Low Voltage = False
        """
        if not isinstance(cntl_pin, CONTROL_PIN):
            raise TypeError("ctrl_pin should be <enum 'CTRL_PIN'>")
        return self._get_pin(cntl_pin)

    def set_control_pin(self, ctrl_pin, is_high):
        """
        cntl_pin: <enum 'CNTL_PIN'>
        is_high: <boolean> High Voltage = True, Low Voltage = False
        """
        if not isinstance(ctrl_pin, CONTROL_PIN):
            raise TypeError("ctrl_pin should be <enum 'CTRL_PIN'>")
        pin_cmd = CONTROL_PIN_CMD_LIST[ctrl_pin.value]
        pin_state = int(is_high)
        self._write_cmd('{pin_cmd} -s {state_int:d}'.format(pin_cmd=pin_cmd, state_int=pin_state))

    def get_alarm_pin(self, alarm_pin):
        """
        alarm_pin: <enum 'ALRM_PIN'>
        :return: <boolean> High Voltage = True, Low Voltage = False
        """
        if not isinstance(alarm_pin, ALARM_PIN):
            raise TypeError("alarm_pin should be <enum 'ALRM_PIN'>")
        return self._get_pin(alarm_pin)

    def read_mdio_register(self, register):
        """
        register: <bytes> 2 bytes of register address
        :return: <bytes> register data value
        """
        # TODO: add temporarily to fix dsp stuck issue
        time.sleep(0.01)
        if not isinstance(register, bytes):
            raise TypeError('register should be bytes type.')
        if len(register) != 2:
            raise ValueError('register length should be 2 bytes.')
        reg_int = int.from_bytes(register, 'big')
        reg_str = '0x%04X' % reg_int
        cmd = 'MDIO -g %s' % reg_str
        reply_str = self._query(cmd)
        reply_int = int(reply_str, 16)
        reply = reply_int.to_bytes(2, 'big')
        return reply

    def write_mdio_register(self, register, data):
        # TODO: add temporarily to fix dsp stuck issue
        time.sleep(0.01)
        if not isinstance(register, bytes):
            raise TypeError('register should be bytes type.')
        if len(register) != 2:
            raise ValueError('register length should be 2 bytes.')
        if not isinstance(data, bytes):
            raise TypeError('data should be bytes type.')
        if len(data) != 2:
            raise ValueError('data length should be 2 bytes.')
        reg_int = int.from_bytes(register, 'big')
        reg_str = '0x%04X' % reg_int
        data_int = int.from_bytes(data, 'big')
        data_str = '0x%04X' % data_int
        cmd = 'MDIO -s {reg} {data}'.format(reg=reg_str, data=data_str)
        self._write_cmd(cmd)

    def set_vcc(self, volt):
        safe_limit = 3.6
        if not isinstance(volt, (float, int)):
            raise TypeError('Vcc voltage should be int or float.')
        if volt >= safe_limit:
            raise ValueError('Vcc exceed the safe limit: set=%f, limit=%f' % (volt, safe_limit))
        self._write_cmd('CFPV -s {volt:f}'.format(volt=volt))

    def get_vcc_setting(self):
        return float(self._query('CFPV -g'))

    def get_vcc_monitored(self):
        return float(self._query('CFPV -gvcc'))

    def get_icc(self):
        return float(self._query('CFPI -g'))

    def get_mod_power(self):
        return float(self._query('CFPPWR -g'))