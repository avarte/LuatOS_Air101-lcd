from micropython import const
from ustruct import unpack as unp

# Power Modes
BMP280_POWER_SLEEP = const(0)
BMP280_POWER_FORCED = const(1)
BMP280_POWER_NORMAL = const(3)

# Oversampling setting
BMP280_OS_ULTRALOW = const(0)
BMP280_OS_LOW = const(1)
BMP280_OS_STANDARD = const(2)
BMP280_OS_HIGH = const(3)
BMP280_OS_ULTRAHIGH = const(4)

# Use cases
BMP280_CASE_HANDHELD_LOW = const(0)
BMP280_CASE_HANDHELD_DYN = const(1)
BMP280_CASE_WEATHER = const(2)
BMP280_CASE_FLOOR = const(3)
BMP280_CASE_DROP = const(4)
BMP280_CASE_INDOOR = const(5)

_BMP280_REGISTER_ID = const(0xD0)
_BMP280_REGISTER_RESET = const(0xE0)
_BMP280_REGISTER_STATUS = const(0xF3)
_BMP280_REGISTER_CONTROL = const(0xF4)
_BMP280_REGISTER_CONFIG = const(0xF5)
_BMP280_REGISTER_DATA = const(0xF7)

_BMP280_OS_MATRIX = [
    [1, 1, 7],
    [2, 1, 9],
    [4, 1, 14],
    [8, 1, 23],
    [16, 2, 44]
]

_BMP280_CASE_MATRIX = [
    [3, 4, 4, 1],
    [3, 2, 16, 0],
    [1, 0, 0, 0],
    [3, 2, 4, 2],
    [3, 1, 0, 0],
    [3, 4, 16, 0]
]

class BMP280:
    def __init__(self, i2c_bus, addr=0x76, use_case=1):
        self._bmp_i2c = i2c_bus
        self._i2c_addr = addr
        
        self._T1 = unp('<H', self._read(0x88, 2))[0]
        self._T2 = unp('<h', self._read(0x8A, 2))[0]
        self._T3 = unp('<h', self._read(0x8C, 2))[0]
        self._P1 = unp('<H', self._read(0x8E, 2))[0]
        self._P2 = unp('<h', self._read(0x90, 2))[0]
        self._P3 = unp('<h', self._read(0x92, 2))[0]
        self._P4 = unp('<h', self._read(0x94, 2))[0]
        self._P5 = unp('<h', self._read(0x96, 2))[0]
        self._P6 = unp('<h', self._read(0x98, 2))[0]
        self._P7 = unp('<h', self._read(0x9A, 2))[0]
        self._P8 = unp('<h', self._read(0x9C, 2))[0]
        self._P9 = unp('<h', self._read(0x9E, 2))[0]
        
        self._t_raw = 0
        self._t_fine = 0
        self._t = 0
        self._p_raw = 0
        self._p = 0
        
        self.read_wait_ms = 0
        self._last_read_ts = 0
        
        if use_case is not None:
            self.use_case(use_case)
    
    def _read(self, addr, size=1):
        return self._bmp_i2c.readfrom_mem(self._i2c_addr, addr, size)
    
    def _write(self, addr, b_arr):
        if not type(b_arr) is bytearray:
            b_arr = bytearray([b_arr])
        return self._bmp_i2c.writeto_mem(self._i2c_addr, addr, b_arr)
    
    def _gauge(self):
        d = self._read(_BMP280_REGISTER_DATA, 6)
        self._p_raw = (d[0] << 12) + (d[1] << 4) + (d[2] >> 4)
        self._t_raw = (d[3] << 12) + (d[4] << 4) + (d[5] >> 4)
        self._t_fine = 0
        self._t = 0
        self._p = 0
    
    def _calc_t_fine(self):
        self._gauge()
        if self._t_fine == 0:
            var1 = (((self._t_raw >> 3) - (self._T1 << 1)) * self._T2) >> 11
            var2 = (((((self._t_raw >> 4) - self._T1) * ((self._t_raw >> 4) - self._T1)) >> 12) * self._T3) >> 14
            self._t_fine = var1 + var2
    
    @property
    def temperature(self):
        self._calc_t_fine()
        if self._t == 0:
            self._t = ((self._t_fine * 5 + 128) >> 8) / 100.0
        return self._t
    
    @property
    def pressure(self):
        self._calc_t_fine()
        if self._p == 0:
            var1 = self._t_fine - 128000
            var2 = var1 * var1 * self._P6
            var2 = var2 + ((var1 * self._P5) << 17)
            var2 = var2 + (self._P4 << 35)
            var1 = ((var1 * var1 * self._P3) >> 8) + ((var1 * self._P2) << 12)
            var1 = (((1 << 47) + var1) * self._P1) >> 33
            
            if var1 == 0:
                return 0
            
            p = 1048576 - self._p_raw
            p = int((((p << 31) - var2) * 3125) / var1)
            var1 = (self._P9 * (p >> 13) * (p >> 13)) >> 25
            var2 = (self._P8 * p) >> 19
            p = ((p + var1 + var2) >> 8) + (self._P7 << 4)
            self._p = p / 256.0
        return self._p
    
    def _write_bits(self, address, value, length, shift=0):
        d = self._read(address)[0]
        m = int('1' * length, 2) << shift
        d &= ~m
        d |= m & (value << shift)
        self._write(address, d)
    
    def _read_bits(self, address, length, shift=0):
        d = self._read(address)[0]
        return (d >> shift) & int('1' * length, 2)
    
    @property
    def power_mode(self):
        return self._read_bits(_BMP280_REGISTER_CONTROL, 2)
    
    @power_mode.setter
    def power_mode(self, v):
        self._write_bits(_BMP280_REGISTER_CONTROL, v, 2)
    
    def use_case(self, uc):
        pm, oss, iir, sb = _BMP280_CASE_MATRIX[uc]
        p_os, t_os, self.read_wait_ms = _BMP280_OS_MATRIX[oss]
        self._write(_BMP280_REGISTER_CONFIG, (iir << 2) + (sb << 5))
        self._write(_BMP280_REGISTER_CONTROL, pm + (p_os << 2) + (t_os << 5))