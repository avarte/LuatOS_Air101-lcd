from st77352 import TFT 
from sysfont import sysfont
from machine import SPI, Pin
import network
import utime

# --- Инициализация дисплея ---
spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
tft = TFT(spi, 6, 10, 7)
tft.init_7735(tft.GREENTAB80x160)
tft.rotation(3)

# --- Кнопки ---
up_key   = Pin(13, Pin.IN, Pin.PULL_UP)
down_key = Pin(8,  Pin.IN, Pin.PULL_UP)

# --- Настройка WiFi ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

tft.fill(TFT.BLACK)
tft.text((30, 35), "SCANNING WIFI...", TFT.YELLOW, sysfont, 1)

# Сканируем доступные сети
raw_nets = wlan.scan()
nets = []
for n in raw_nets:
    try:
        ssid = n[0].decode('utf-8')
    except:
        ssid = "<Hidden>"
    rssi = n[3]
    nets.append((ssid, rssi))

# Сортировка по силе сигнала
nets.sort(key=lambda x: x[1], reverse=True)

# Параметры отображения
scroll_pos = 0      
visible_count = 6   
line_h = 13         
total_nets = len(nets)
needs_update = True

def draw_interface():
    tft.fill(TFT.BLACK)
    
    if total_nets == 0:
        tft.text((20, 35), "NO NETWORKS FOUND", TFT.RED, sysfont, 1)
        return

    # 1. Полоса прокрутки (исправлен цвет с кортежа на константу)
    bar_height = max(10, int((visible_count / total_nets) * 80))
    bar_y = int((scroll_pos / total_nets) * 80)
    
    # Фоновая линия (используем белый или серый, если он есть в библиотеке)
    tft.fillrect((0, 0), (3, 80), TFT.WHITE) 
    # Ползунок (рисуем черным внутри белого или инверсно)
    tft.fillrect((0, bar_y), (3, bar_height), TFT.RED)

    # 2. Список сетей (по 6 строк)
    for i in range(visible_count):
        idx = scroll_pos + i
        if idx < total_nets:
            ssid, rssi = nets[idx]
            y = i * line_h + 2
            
            # Цвет в зависимости от уровня сигнала
            color = TFT.GREEN if rssi > -60 else (TFT.YELLOW if rssi > -80 else TFT.RED)
            
            # Форматированный вывод
            txt = "{:d}.{:.12s}".format(idx+1, ssid)
            tft.text((6, y), txt, color, sysfont, 1)
            tft.text((125, y), str(rssi), TFT.WHITE, sysfont, 1)

print(f"Found {total_nets} networks")

while True:
    if needs_update:
        draw_interface()
        needs_update = False

    # Листаем ВВЕРХ на 6 строк
    if up_key.value() == 0:
        if scroll_pos > 0:
            scroll_pos -= visible_count
            if scroll_pos < 0: scroll_pos = 0
            needs_update = True
            utime.sleep_ms(250)

    # Листаем ВНИЗ на 6 строк
    if down_key.value() == 0:
        if scroll_pos + visible_count < total_nets:
            scroll_pos += visible_count
            needs_update = True
            utime.sleep_ms(250)

    utime.sleep_ms(20)
