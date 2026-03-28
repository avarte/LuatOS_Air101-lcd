# aht10.py — Драйвер для датчика температуры и влажности AHT10/AHT20

from machine import I2C, Pin
import utime

class AHT10:
    ADDR = 0x38
    CMD_INIT = 0xBE
    CMD_TRIGGER = 0xAC
    CMD_RESET = 0xBA
    
    def __init__(self, i2c):
        self.i2c = i2c
        self.addr = self.ADDR
        self._init()
    
    def _init(self):
        try:
            self.i2c.writeto(self.addr, bytes([self.CMD_INIT, 0x08, 0x00]))
            utime.sleep_ms(10)
            status = self.i2c.readfrom(self.addr, 1)[0]
            if status & 0x08:
                self.i2c.writeto(self.addr, bytes([self.CMD_RESET]))
                utime.sleep_ms(20)
                self.i2c.writeto(self.addr, bytes([self.CMD_INIT, 0x08, 0x00]))
                utime.sleep_ms(10)
        except:
            pass
    
    def _trigger(self):
        try:
            self.i2c.writeto(self.addr, bytes([self.CMD_TRIGGER, 0x33, 0x00]))
            utime.sleep_ms(90)
            return True
        except:
            return False
    
    def read(self):
        try:
            if not self._trigger():
                return None, None
            
            data = self.i2c.readfrom(self.addr, 6)
            
            # Humidity: байты 1-3 (20 бит)
            humidity_raw = (data[1] << 12) | (data[2] << 4) | (data[3] >> 4)
            humidity = (humidity_raw / 2**20) * 100
            
            # Temperature: байты 3-5 (20 бит)
            temp_raw = ((data[3] & 0x0F) << 16) | (data[4] << 8) | data[5]
            temperature = (temp_raw / 2**20) * 200 - 50
            
            # Проверка диапазона
            if humidity > 100 or humidity < 0:
                return None, None
            if temperature > 100 or temperature < -40:
                return None, None
            
            return temperature, humidity
            
        except:
            return None, None
    
    def read_temperature(self):
        temp, _ = self.read()
        return temp
    
    def read_humidity(self):
        _, hum = self.read()
        return hum
    
    def reset(self):
        try:
            self.i2c.writeto(self.addr, bytes([self.CMD_RESET]))
            utime.sleep_ms(20)
            self._init()
        except:
            pass