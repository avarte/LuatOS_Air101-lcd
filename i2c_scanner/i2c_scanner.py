from st77352 import TFT
from sysfont import sysfont
from machine import I2C, Pin, SPI
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

# Кнопки
up_key     = Pin(13, Pin.IN, Pin.PULL_UP)
down_key   = Pin(8,  Pin.IN, Pin.PULL_UP)
center_key = Pin(4,  Pin.IN, Pin.PULL_UP)

# =============================================================================
# === НАСТРОЙКИ ===============================================================
# =============================================================================

devices = []
scroll_pos = 0
total_devices = 0
visible_count = 5
line_h = 12
needs_update = True

# =============================================================================
# === ФУНКЦИИ ОТРИСОВКИ =======================================================
# =============================================================================

def draw_header():
    tft.fillrect((0, 0), (160, 14), TFT.BLACK)
    tft.text((45, 2), "I2C SCAN", TFT.YELLOW, sysfont, 1)

def draw_scrollbar():
    if total_devices == 0:
        return
    
    bar_height = max(8, int((visible_count / max(1, total_devices)) * 60))
    bar_y = 14 + int((scroll_pos / max(1, total_devices - visible_count + 1)) * (60 - bar_height))
    
    tft.fillrect((0, 14), (3, 60), TFT.WHITE)
    tft.fillrect((0, bar_y), (3, bar_height), TFT.RED)

def draw_device_list():
    for i in range(visible_count):
        idx = scroll_pos + i
        y = 16 + i * line_h
        
        if idx < total_devices:
            addr, name = devices[idx]
            addr_str = f"0x{addr:02X}"
            
            tft.fillrect((4, y), (156, line_h), TFT.BLACK)
            tft.text((6, y+1), addr_str, TFT.GREEN, sysfont, 1)
            tft.text((50, y+1), name, TFT.WHITE, sysfont, 1)
        else:
            tft.fillrect((4, y), (156, line_h), TFT.BLACK)

def draw_scanning():
    tft.fill(TFT.BLACK)
    draw_header()
    tft.text((30, 35), "SCANNING...", TFT.YELLOW, sysfont, 1)
    tft.text((35, 50), "I2C BUS", TFT.WHITE, sysfont, 1)

def draw_interface():
    draw_header()
    draw_scrollbar()
    draw_device_list()

def update_interface():
    draw_scrollbar()
    draw_device_list()

# =============================================================================
# === I2C СКАНИРОВАНИЕ ========================================================
# =============================================================================

# Известные I2C устройства
KNOWN_DEVICES = {
    0x38: "AHT10/20",
    0x39: "TSL2561",
    0x3C: "OLED 0.96",
    0x3D: "OLED 1.3",
    0x40: "SI7021",
    0x44: "SHT30",
    0x50: "EEPROM",
    0x51: "EEPROM",
    0x52: "EEPROM",
    0x53: "EEPROM",
    0x68: "DS3231",
    0x69: "MPU6050",
    0x76: "BMP280",
    0x77: "BMP280",
    0x7D: "LD2410",
}

def get_device_name(addr):
    """Определяет устройство по адресу"""
    return KNOWN_DEVICES.get(addr, "Unknown")

def perform_scan():
    global devices, total_devices, scroll_pos, needs_update
    
    devices = []
    total_devices = 0
    scroll_pos = 0
    needs_update = True
    
    draw_scanning()
    
    print("\n=== I2C SCAN ===")
    print("Scanning I2C bus (0x00-0x7F)...")
    
    # Сканирование адресов 0x00-0x7F
    for addr in range(128):
        try:
            i2c.writeto(addr, bytes([0x00]))
            name = get_device_name(addr)
            devices.append((addr, name))
            print(f"  Found: 0x{addr:02X} ({name})")
        except:
            pass
    
    total_devices = len(devices)
    
    print(f"\n=== RESULTS ===")
    print(f"Devices found: {total_devices}")
    for addr, name in devices:
        print(f"  0x{addr:02X} - {name}")
    
    needs_update = True

# =============================================================================
# === УПРАВЛЕНИЕ ==============================================================
# =============================================================================

def wait_release(pin):
    while pin.value() == 0:
        utime.sleep_ms(10)

# =============================================================================
# === ГЛАВНЫЙ ЦИКЛ ============================================================
# =============================================================================

print("\n========================================")
print("I2C SCANNER")
print("========================================")
print("I2C: SCL=GPIO0, SDA=GPIO1")
print("========================================\n")

perform_scan()
draw_interface()

while True:
    if needs_update:
        update_interface()
        needs_update = False
    
    # Рескан по CENTER
    if center_key.value() == 0:
        perform_scan()
        wait_release(center_key)
    
    # Прокрутка ВВЕРХ (по 5 устройств)
    if up_key.value() == 0:
        if scroll_pos > 0:
            scroll_pos -= visible_count
            if scroll_pos < 0:
                scroll_pos = 0
            needs_update = True
        wait_release(up_key)
    
    # Прокрутка ВНИЗ (по 5 устройств)
    if down_key.value() == 0:
        if scroll_pos + visible_count < total_devices:
            scroll_pos += visible_count
            needs_update = True
        wait_release(down_key)
    
    utime.sleep_ms(50)