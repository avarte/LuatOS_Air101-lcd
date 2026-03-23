from st77352 import TFT 
from sysfont import sysfont
from machine import SPI, Pin
import utime

# --- Инициализация дисплея ---
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
tft = TFT(spi, 6, 10, 7)
tft.init_7735(tft.GREENTAB80x160)
tft.rotation(3)

# --- Кнопки  ---
up_key     = Pin(13, Pin.IN, Pin.PULL_UP)
down_key   = Pin(8,  Pin.IN, Pin.PULL_UP)
left_key   = Pin(9,  Pin.IN, Pin.PULL_UP)
right_key  = Pin(5,  Pin.IN, Pin.PULL_UP)
center_key = Pin(4,  Pin.IN, Pin.PULL_UP)

# Список кнопок: [Имя, Объект Pin, Координата Y, Старое состояние]
btns = [
    ["UP    (P13)", up_key,     20, -1],
    ["DOWN  (P8) ", down_key,   32, -1],
    ["LEFT  (P9) ", left_key,   44, -1],
    ["RIGHT (P5) ", right_key,  56, -1],
    ["CENTER(P4) ", center_key, 68, -1]
]

tft.fill(TFT.BLACK)
tft.text((30, 5), "--- BUTTONS TEST ---", TFT.YELLOW, sysfont, 1)

while True:
    for i in range(len(btns)):
        name = btns[i][0]
        pin  = btns[i][1]
        y    = btns[i][2]
        old_val = btns[i][3]
        
        current_val = pin.value()
        
        # Обновляем экран только при ИЗМЕНЕНИИ состояния (нет мерцания)
        if current_val != old_val:
            if current_val == 0: # Нажата
                tft.fillrect((5, y), (150, 11), TFT.GREEN)
                tft.text((10, y+1), name + ": [ PRESSED ]", TFT.BLACK, sysfont, 1)
            else: # Отпущена
                tft.fillrect((5, y), (150, 11), TFT.BLACK)
                tft.text((10, y+1), name + ": release", TFT.WHITE, sysfont, 1)
            
            btns[i][3] = current_val # Запоминаем новое состояние
            
    utime.sleep_ms(30)
