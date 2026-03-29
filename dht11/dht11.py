# dht11.py — Драйвер для датчика температуры и влажности DHT11

from machine import Pin
import utime
import dht

class DHT11:
    def __init__(self, pin=0):
        self.sensor = dht.DHT11(Pin(pin, Pin.IN, Pin.PULL_UP))
        self.last_temp = None
        self.last_hum = None
    
    def read(self):
        """Чтение температуры и влажности"""
        try:
            self.sensor.measure()
            temp = self.sensor.temperature()
            hum = self.sensor.humidity()
            
            self.last_temp = temp
            self.last_hum = hum
            
            return temp, hum
        except:
            return None, None
    
    def read_temperature(self):
        """Только температура"""
        temp, _ = self.read()
        return temp
    
    def read_humidity(self):
        """Только влажность"""
        _, hum = self.read()
        return hum
    
    def get_last_temp(self):
        """Последнее успешное значение температуры"""
        return self.last_temp
    
    def get_last_hum(self):
        """Последнее успешное значение влажности"""
        return self.last_hum