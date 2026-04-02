from machine import I2C, Pin
from aht10 import AHT10
from st77352 import TFT
from sysfont import sysfont
from machine import SPI
import utime

# =============================================================================
# === ИНИЦИАЛИЗАЦИЯ ===========================================================
# =============================================================================

# I2C: GPIO 0 = SCL, GPIO 1 = SDA
i2c = I2C(0, scl=Pin(0), sda=Pin(1), freq=400000)

# Дисплей
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
tft = TFT(spi, 6, 10, 7)
tft.init_7735(tft.GREENTAB80x160)
tft.rotation(3)

# Датчик
try:
    aht = AHT10(i2c)
    print("AHT10 found!")
except Exception as e:
    print(f"AHT10 NOT found! Error: {e}")
    aht = None

# =============================================================================
# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===================================================
# =============================================================================

old_temp = None
old_hum = None

# =============================================================================
# === ОТРИСОВКА ===============================================================
# =============================================================================

def draw_header():
    tft.fillrect((0, 0), (160, 14), TFT.BLACK)
    tft.text((45, 2), "AHT10 SENSOR", TFT.YELLOW, sysfont, 1)

def draw_labels():
    
    tft.text((100, 29), "Temp", TFT.WHITE, sysfont, 2)  
    tft.text((100, 53), "Hum", TFT.WHITE, sysfont, 2)   

def draw_screen_init():
    tft.fill(TFT.BLACK)
    draw_header()
    draw_labels()

def get_temp_color(temp):
    """Определяет цвет температуры"""
    if temp >= 0:
        return TFT.GREEN
    else:
        return TFT.BLUE

def update_values(temp, hum):
    """Обновляем ТОЛЬКО значения (с умными цветами)"""
    global old_temp, old_hum
    
    temp_str = f"{temp:+.1f}C"
    hum_str = f"{hum:.0f}%"
    
    temp_color = get_temp_color(temp)
    
    
    if temp_str != old_temp:
        tft.fillrect((20, 27), (70, 16), TFT.BLACK)  
        tft.text((20, 27), temp_str, temp_color, sysfont, 2)
        old_temp = temp_str
    
    if hum_str != old_hum:
        tft.fillrect((20, 52), (50, 16), TFT.BLACK)  
        tft.text((20, 52), hum_str, TFT.CYAN, sysfont, 2)
        old_hum = hum_str

def draw_error():
    """Показываем ошибку"""
    global old_temp, old_hum
    old_temp = None
    old_hum = None
    
    tft.fillrect((20, 27), (70, 16), TFT.BLACK)
    tft.fillrect((20, 52), (50, 16), TFT.BLACK)
    
    tft.text((30, 40), "Sensor", TFT.WHITE, sysfont, 1)
    tft.text((35, 55), "Error!", TFT.RED, sysfont, 1)

# =============================================================================
# === ГЛАВНЫЙ ЦИКЛ ============================================================
# =============================================================================

print("\n========================================")
print("AHT10 SENSOR TEST")
print("========================================")
print("I2C: SCL=GPIO0, SDA=GPIO1")
print("========================================\n")

draw_screen_init()

while True:
    if aht:
        temp, hum = aht.read()
        
        if temp is not None and hum is not None:
            print(f"Temp: {temp:+.1f}C  Hum: {hum:.0f}%")
            update_values(temp, hum)
        else:
            print("Read error!")
            draw_error()
    else:
        print("No sensor!")
        draw_error()
    
    utime.sleep_ms(2000)