import time
import struct

class DSP:
    def __init__(self, dut):
        self.__dut = dut
        self.__dsp_ch_frame = None

    @property
    def dsp_ch_frame(self):
        if not self.__dsp_ch_frame:
            raw = self.__dut[0x9006]
            self.__dsp_ch_frame = [raw >> 8, raw & (2**8-1)]
        return self.__dsp_ch_frame

    def api(self, byteArray):
        self.__dut.ddb.wait_for_idle()

        txlen = len(byteArray)
        i = 0
        while i < (txlen/2):
            self.__dut[0x9c03+i] = (byteArray[2*i]) | (byteArray[2*i+1] << 8)
            i += 1
        if txlen%2:
            self.__dut[0x9c03+i] = byteArray[2*i]
            i += 1
        self.__dut[0x9c02] = 0x0002
        self.__dut[0x9c01] = i+1
        self.__dut[0x9c00] = 0x0f07 # payload size
 
        self.__dut.ddb.wait_for_complete()

        resArray = []
        rxlen = self.__dut[0x9c01]
        i = 0
        while i < rxlen:
            data = self.__dut[0x9c02+i]
            resArray.append(data>>8)
            resArray.append(data & 0xFF)
            i += 1
        return struct.pack('%sB'%len(resArray), *resArray)

    def firmware_information(self):
        request = b'\x08\x00\xe1\x01\x2c\x00\x00\x00'
        response = self.api(request)
        rsp = {}
        rsp['dFirmwareVersion'] = hex(struct.unpack('<I', response[0x4:0x8])[0])
        rsp['aGitHash'] = response[0x8:0x14]
        rsp['aCpiosGitHash'] = response[0x14:0x20]
        rsp['aRm'] = hex(struct.unpack('<I', response[0x20:0x24])[0])
        return rsp

    def trigger_monitors(self):
        request = b'\x08\x00\x6c\x01\x04\x00\x00\x00'
        return self.api(request)

    def SetHostIngressLanePolarity(self, polarity):
        request = b'\x0c\x00\x10\x01\x04\x00\x00\x00' + struct.pack('b', polarity) + b'\x00\x00\x00'
        return self.api(request)

    def SetOtuClientTestPatternGeneratorConfig(self, channel,direction, signal_type, keep_incoming_fs, enable):
        request = b'\x10\x00\x76\x01\x04\x00\x00\x00' + \
                  struct.pack('B', channel) + \
                  struct.pack('B', direction) + \
                  struct.pack('B', signal_type) + \
                  struct.pack('B', keep_incoming_fs) + \
                  struct.pack('B', enable) + b'\x00\x00\x00'
        return self.api(request)

    def SetOtuClientTestPatternCheckerConfig(self, channel, direction, signal_type, enable):
        request = b'\x0c\x00\x78\x01\x04\x00\x00\x00' + \
                  struct.pack('B', channel) + \
                  struct.pack('B', direction) + \
                  struct.pack('B', signal_type) + \
                  struct.pack('B', enable)
        return self.api(request)

    def GetErrorCorrectionStatistics(self, channel, direction):
        request = b'\x0c\x00\x67\x01\x84\x00\x00\x00' + \
                  struct.pack('B', channel) + \
                  struct.pack('B', direction) + b'\x00\x00'
        return self.api(request)

    def get_error_correction_statistics(self, channel, direction):
        request = b'\x0c\x00\x67\x01\x84\x00\x00\x00' + \
            struct.pack('B', channel) + \
            struct.pack('B', direction) + b'\x00\x00'
        response = self.api(request)
        rsp = {}
        rsp['accum_bit_count'] = struct.unpack('<Q', response[4:0xc])[0]
        rsp['accum_corrected_error_count'] = struct.unpack('<Q', response[0xc:0x14])[0]
        rsp['accum_uncorrected_codeword_count'] = struct.unpack('<Q', response[0x14:0x1c])[0]
        rsp['accum_codeword_count'] = struct.unpack('<Q', response[0x1c:0x24])[0]
        rsp['max_corrected_bit_count'] = struct.unpack('<Q', response[0x24:0x2c])[0]
        rsp['max_corrected_error_count'] = struct.unpack('<Q', response[0x2c:0x34])[0]
        rsp['max_uncorrected_codeword_count'] = struct.unpack('<Q', response[0x34:0x3c])[0]
        rsp['max_codeword_count'] = struct.unpack('<Q', response[0x3c:0x44])[0]
        rsp['min_corrected_bit_count'] = struct.unpack('<Q', response[0x44:0x4c])[0]
        rsp['min_corrected_error_count'] = struct.unpack('<Q', response[0x4c:0x54])[0]
        rsp['min_uncorrected_codeword_count'] = struct.unpack('<Q', response[0x54:0x5c])[0]
        rsp['min_codeword_count'] = struct.unpack('<Q', response[0x5c:0x64])[0]
        rsp['instant_corrected_bit_count'] = struct.unpack('<Q', response[0x64:0x6c])[0]
        rsp['instant_corrected_error_count'] = struct.unpack('<Q', response[0x6c:0x74])[0]
        rsp['instant_uncorrected_codeword_count'] = struct.unpack('<Q', response[0x74:0x7c])[0]
        rsp['instant_codeword_count'] = struct.unpack('<Q', response[0x7c:0x84])[0]
        return rsp

    def get_ber(self):
        ch1_frame, ch2_frame = self.dsp_ch_frame
        ch1 = self.get_error_correction_statistics(ch1_frame, 1)
        ch2 = self.get_error_correction_statistics(ch2_frame, 1)
        if ch1['accum_bit_count'] <= 0 or ch2['accum_bit_count'] <= 0:
            uncorrected_codeword = -1
            corrected_ber = 1
        else:
            corrected_ber = (ch1['accum_corrected_error_count'] + 
                    ch2['accum_corrected_error_count']) / (ch1['accum_bit_count'] + 
                    ch2['accum_bit_count'])
            uncorrected_codeword = (ch1['accum_uncorrected_codeword_count'] +
                    ch2['accum_uncorrected_codeword_count'])

        print('========\nCOR BER: %.3e, UNCOR CODEWORD: %.3e\n========' % (corrected_ber, uncorrected_codeword))

        return uncorrected_codeword, corrected_ber

    def ReStartLineIngressDsp(self, action):
        # action: 0=Stop, 1=Start, 2=Toggle
        request = b'\x0c\x00\xf5\x01\x04\x00\x00\x00' + \
                  struct.pack('B', action) + b'\x00'*3
        return self.api(request)

    def get_temperature(self):
        sensor_id_0, sensor_id_1, sensor_id_2, sensor_id_3 = 2, 8, 10, 11
        request = b'\x0c\x00\xe6\x01\x14\x00\x00\x00' + \
                struct.pack('B', sensor_id_0) + \
                struct.pack('B', sensor_id_1) + \
                struct.pack('B', sensor_id_2) + \
                struct.pack('B', sensor_id_3)
        response = self.api(request)
        t1 = struct.unpack('<i', response[0x4:0x8])[0]/4
        t2 = struct.unpack('<i', response[0x8:0xc])[0]/4
        t3 = struct.unpack('<i', response[0xc:0x10])[0]/4
        t4 = struct.unpack('<i', response[0x10:0x14])[0]/4
        return t1, t2, t3, t4
