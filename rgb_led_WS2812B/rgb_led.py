from machine import Pin
from neopixel import NeoPixel
from st77352 import TFT
from sysfont import sysfont
from machine import SPI, reset
import utime

# =============================================================================
# === ИНИЦИАЛИЗАЦИЯ ===========================================================
# =============================================================================

spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
tft = TFT(spi, 6, 10, 7)
tft.init_7735(tft.GREENTAB80x160)
tft.rotation(3)

up_key     = Pin(13, Pin.IN, Pin.PULL_UP)
down_key   = Pin(8,  Pin.IN, Pin.PULL_UP)
left_key   = Pin(9,  Pin.IN, Pin.PULL_UP)
right_key  = Pin(5,  Pin.IN, Pin.PULL_UP)
center_key = Pin(4,  Pin.IN, Pin.PULL_UP)

led_pin = Pin(12, Pin.OUT)
np = NeoPixel(led_pin, 16)

# =============================================================================
# === НАСТРОЙКИ ===============================================================
# =============================================================================

num_leds = 8
color_r = 128
color_g = 128
color_b = 128

selected_row = 0

auto_repeat_start = 300
auto_repeat_fast = 50
hold_step = 10

# =============================================================================
# === ФУНКЦИИ ОТРИСОВКИ =======================================================
# =============================================================================

def draw_header():
    tft.fillrect((0, 0), (160, 14), TFT.BLACK)
    tft.text((40, 2), "LED CONTROL", TFT.YELLOW, sysfont, 1)

def draw_led_count(highlight=False):
    y = 18
    bg_color = TFT.WHITE if highlight else TFT.BLACK
    
    # Цвет текста: чёрный на белом фоне, белый на чёрном
    label_color = TFT.BLACK if highlight else TFT.WHITE
    value_color = TFT.BLACK if highlight else TFT.GREEN
    
    # Сначала фон
    tft.fillrect((0, y), (160, 14), bg_color)
    # Потом текст (поверх фона)
    tft.text((5, y+2), "LEDs:", label_color, sysfont, 1)
    tft.text((50, y+2), str(num_leds), value_color, sysfont, 1)
    tft.text((75, y+2), "/16", label_color, sysfont, 1)

def draw_color_bar(row, value, color, label, highlight=False):
    y = 34 + row * 14
    bar_width = 70
    fill_width = int((value / 255) * bar_width)
    
    bg_color = TFT.WHITE if highlight else TFT.BLACK
    text_color = TFT.BLACK if highlight else TFT.WHITE
    
    # Сначала фон
    tft.fillrect((0, y), (160, 14), bg_color)
    # Потом текст НАЗВАНИЯ (всегда цветной, поверх фона)
    tft.text((5, y+2), label, color, sysfont, 1)
    # Потом текст ЗНАЧЕНИЯ (чёрный на белом, цветной на чёрном)
    tft.text((35, y+2), str(value), text_color if highlight else color, sysfont, 1)
    # Потом полоса
    tft.fillrect((70, y+3), (bar_width, 8), TFT.BLACK)
    tft.rect((70, y+3), (bar_width, 8), TFT.WHITE)
    if fill_width > 0:
        tft.fillrect((71, y+4), (fill_width, 6), color)

def update_leds():
    for i in range(num_leds):
        np[i] = (color_r, color_g, color_b)
    for i in range(num_leds, 16):
        np[i] = (0, 0, 0)
    np.write()

# =============================================================================
# === УПРАВЛЕНИЕ ==============================================================
# =============================================================================

def adjust_value(row, step, update_display=True):
    global color_r, color_g, color_b, num_leds
    
    if row == 0:
        num_leds += step
        if num_leds < 1:
            num_leds = 1
        elif num_leds > 16:
            num_leds = 16
        if update_display:
            draw_led_count(selected_row == 0)
        update_leds()
    elif row == 1:
        color_r += step
        if color_r < 0:
            color_r = 0
        elif color_r > 255:
            color_r = 255
        if update_display:
            draw_color_bar(0, color_r, TFT.RED, "R:", selected_row == 1)
        update_leds()
    elif row == 2:
        color_g += step
        if color_g < 0:
            color_g = 0
        elif color_g > 255:
            color_g = 255
        if update_display:
            draw_color_bar(1, color_g, TFT.GREEN, "G:", selected_row == 2)
        update_leds()
    elif row == 3:
        color_b += step
        if color_b < 0:
            color_b = 0
        elif color_b > 255:
            color_b = 255
        if update_display:
            draw_color_bar(2, color_b, TFT.BLUE, "B:", selected_row == 3)
        update_leds()

def handle_button_with_repeat(pin, direction):
    adjust_value(selected_row, 1 * direction)
    utime.sleep_ms(100)
    
    if pin.value() == 0:
        start = utime.ticks_ms()
        while pin.value() == 0:
            if utime.ticks_diff(utime.ticks_ms(), start) > auto_repeat_start:
                adjust_value(selected_row, hold_step * direction)
                utime.sleep_ms(auto_repeat_fast)
                start = utime.ticks_ms()
            utime.sleep_ms(10)

def change_row(new_row):
    global selected_row
    old_row = selected_row
    selected_row = new_row
    
    # Перерисовываем старую строку (без выделения)
    if old_row == 0:
        draw_led_count(False)
    else:
        draw_color_bar(old_row - 1,
                      [color_r, color_g, color_b][old_row - 1],
                      [TFT.RED, TFT.GREEN, TFT.BLUE][old_row - 1],
                      ["R:", "G:", "B:"][old_row - 1],
                      False)
    
    # Перерисовываем новую строку (с выделением)
    if selected_row == 0:
        draw_led_count(True)
    else:
        draw_color_bar(selected_row - 1,
                      [color_r, color_g, color_b][selected_row - 1],
                      [TFT.RED, TFT.GREEN, TFT.BLUE][selected_row - 1],
                      ["R:", "G:", "B:"][selected_row - 1],
                      True)

# =============================================================================
# === ГЛАВНЫЙ ЦИКЛ ============================================================
# =============================================================================

tft.fill(TFT.BLACK)
draw_header()
draw_led_count(selected_row == 0)
draw_color_bar(0, color_r, TFT.RED, "R:", selected_row == 1)
draw_color_bar(1, color_g, TFT.GREEN, "G:", selected_row == 2)
draw_color_bar(2, color_b, TFT.BLUE, "B:", selected_row == 3)
update_leds()

while True:
    if up_key.value() == 0:
        new_row = (selected_row - 1) % 4
        change_row(new_row)
        while up_key.value() == 0:
            utime.sleep_ms(10)
    
    if down_key.value() == 0:
        new_row = (selected_row + 1) % 4
        change_row(new_row)
        while down_key.value() == 0:
            utime.sleep_ms(10)
    
    if left_key.value() == 0:
        handle_button_with_repeat(left_key, -1)
    
    if right_key.value() == 0:
        handle_button_with_repeat(right_key, 1)
    
    utime.sleep_ms(50)