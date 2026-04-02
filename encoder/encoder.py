# encoder.py — Драйвер для поворотного энкодера

from machine import Pin
import utime

class SimpleEncoder:
    def __init__(self, dt=0, clk=1, sw=12):
        self.dt = Pin(dt, Pin.IN, Pin.PULL_UP)
        self.clk = Pin(clk, Pin.IN, Pin.PULL_UP)
        self.sw = Pin(sw, Pin.IN, Pin.PULL_UP)
        
        self.last_clk = self.clk.value()
        self.last_dt = self.dt.value()
        self.last_button = True
        self.rotation_delay = 1  # ← МАКСИМАЛЬНАЯ чувствительность (было 3)
        self.last_rotation_time = 0
    
    def read_rotation(self):
        """Чтение вращения (возвращает -1, 0, или 1)"""
        clk_now = self.clk.value()
        dt_now = self.dt.value()
        
        if clk_now != self.last_clk:
            if clk_now == 0:
                if dt_now != self.last_dt:
                    if dt_now == 0:
                        direction = 1
                    else:
                        direction = -1
                    
                    current_time = utime.ticks_ms()
                    if utime.ticks_diff(current_time, self.last_rotation_time) > self.rotation_delay:
                        self.last_rotation_time = current_time
                        self.last_clk = clk_now
                        self.last_dt = dt_now
                        return direction
            
            self.last_clk = clk_now
            self.last_dt = dt_now
        
        return 0
    
    def read_button(self):
        """Чтение кнопки (True = нажата)"""
        button_now = not self.sw.value()
        
        if button_now != self.last_button:
            utime.sleep_ms(50)
            button_now = not self.sw.value()
            self.last_button = button_now
        
        return button_now