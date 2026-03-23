from st77352 import TFT 
from sysfont import sysfont
from machine import SPI, Pin
import network
import ntptime
import utime

# --- Настройки ---
WIFI_SSID = "название_сети"
WIFI_PASS = "пароль_сети"
UTC_OFFSET = 6 * 3600 

# --- Инициализация дисплея ---
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
tft = TFT(spi, 6, 10, 7)
tft.init_7735(tft.GREENTAB80x160)
tft.rotation(3)

# Храним старые значения цифр и даты
old_digits = [-1] * 6
old_date = ""

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    tft.fill(TFT.BLACK)
    tft.text((5, 10), "CONNECTING...", TFT.YELLOW, sysfont, 1)
    wlan.connect(WIFI_SSID, WIFI_PASS)
    while not wlan.isconnected():
        utime.sleep(0.5)
    tft.fill(TFT.BLACK)

def sync_time():
    try:
        ntptime.settime()
    except:
        pass

def draw_digit(x, y, value, old_idx, color):
    global old_digits
    if value != old_digits[old_idx]:
        # Затираем область только одной цифры
        tft.fillrect((x, y), (18, 26), TFT.BLACK)
        tft.text((x, y), str(value), color, sysfont, 3)
        old_digits[old_idx] = value

def draw_clock():
    global old_date
    t_now = utime.localtime(utime.time() + UTC_OFFSET)
    h, m, s = t_now[3], t_now[4], t_now[5]
    y_pos = 40
    color = TFT.GREEN

    # Отрисовка цифр (поциферно)
    draw_digit(15,  y_pos, h // 10, 0, color) 
    draw_digit(35,  y_pos, h % 10,  1, color) 
    
    draw_digit(65,  y_pos, m // 10, 2, color) 
    draw_digit(85,  y_pos, m % 10,  3, color) 
    
    draw_digit(115, y_pos, s // 10, 4, color) 
    draw_digit(135, y_pos, s % 10,  5, color) 

    # ДАТА
    date_now = "{:02d}.{:02d}.{:04d}".format(t_now[2], t_now[1], t_now[0])
    if date_now != old_date:
        tft.fillrect((35, 90), (100, 20), TFT.BLACK)
        tft.text((35, 90), date_now, TFT.CYAN, sysfont, 1.5)
        old_date = date_now

# --- Старт ---
connect_wifi()
sync_time()
tft.text((5, 5), WIFI_SSID, TFT.WHITE, sysfont, 1)

# Рисуем двоеточия статично
# Первое на 49, второе на 99
tft.text((49, 40), ":", TFT.GREEN, sysfont, 3)
tft.text((99, 40), ":", TFT.GREEN, sysfont, 3)

while True:
    draw_clock()
    utime.sleep_ms(50)
