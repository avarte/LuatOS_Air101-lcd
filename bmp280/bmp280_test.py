from machine import I2C, Pin, SPI
from bmp280 import BMP280
from st77352 import TFT
from sysfont import sysfont
import utime

# =============================================================================
# === ИНИЦИАЛИЗАЦИЯ ===========================================================
# =============================================================================

# I2C: GPIO 0 = SCL, GPIO 1 = SDA
i2c = I2C(0, scl=Pin(0), sda=Pin(1), freq=400000)

# Инициализация BMP280
try:
    bmp = BMP280(i2c, addr=0x76)
    print("BMP280 found at 0x76!")
except:
    try:
        bmp = BMP280(i2c, addr=0x77)
        print("BMP280 found at 0x77!")
    except Exception as e:
        print(f"BMP280 NOT found! Error: {e}")
        bmp = None

# Дисплей
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
tft = TFT(spi, 6, 10, 7)
tft.init_7735(tft.GREENTAB80x160)
tft.rotation(3)

# =============================================================================
# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===================================================
# =============================================================================

old_temp = None
old_pressure = None

# =============================================================================
# === ОТРИСОВКА ===============================================================
# =============================================================================

def draw_header():
    tft.fillrect((0, 0), (160, 14), TFT.BLACK)
    tft.text((40, 2), "BMP280 SENSOR", TFT.YELLOW, sysfont, 1)

def draw_labels():
    tft.text((100, 29), "Temp", TFT.WHITE, sysfont, 2)
    tft.text((100, 53), "Press", TFT.WHITE, sysfont, 2)

def draw_screen_init():
    tft.fill(TFT.BLACK)
    draw_header()
    draw_labels()

def get_temp_color(temp):
    if temp is None:
        return TFT.BLUE
    if temp >= 0:
        return TFT.GREEN
    else:
        return TFT.BLUE

def update_values(temp, pressure):
    global old_temp, old_pressure
    
    temp_str = f"{temp:+.1f}C" if temp is not None else "--.-C"
    press_str = f"{pressure:.1f}" if pressure is not None else "---"
    
    temp_color = get_temp_color(temp)
    
    if temp_str != old_temp:
        tft.fillrect((20, 27), (70, 16), TFT.BLACK)
        tft.text((20, 27), temp_str, temp_color, sysfont, 2)
        old_temp = temp_str
    
    if press_str != old_pressure:
        tft.fillrect((20, 52), (60, 16), TFT.BLACK)
        tft.text((20, 52), press_str, TFT.CYAN, sysfont, 2)
        old_pressure = press_str

def draw_error():
    global old_temp, old_pressure
    old_temp = None
    old_pressure = None
    
    tft.fillrect((20, 27), (70, 16), TFT.BLACK)
    tft.fillrect((20, 52), (60, 16), TFT.BLACK)
    
    tft.text((30, 40), "Sensor", TFT.WHITE, sysfont, 1)
    tft.text((35, 55), "Error!", TFT.RED, sysfont, 1)

# =============================================================================
# === ГЛАВНЫЙ ЦИКЛ ============================================================
# =============================================================================

print("\n========================================")
print("BMP280 SENSOR TEST")
print("========================================")
print("I2C: SCL=GPIO0, SDA=GPIO1")
print("========================================\n")

draw_screen_init()

while True:
    if bmp:
        try:
            temp = bmp.temperature
            pressure_hpa = bmp.pressure / 100.0
            pressure_mmhg = pressure_hpa * 0.750062
            
            print(f"Temp: {temp:+.1f}C  Pressure: {pressure_hpa:.1f}hPa ({pressure_mmhg:.1f}mmHg)")
            update_values(temp, pressure_mmhg)
        except Exception as e:
            print(f"Read error: {e}")
            draw_error()
    else:
        print("No sensor!")
        draw_error()
    
    utime.sleep_ms(2000)