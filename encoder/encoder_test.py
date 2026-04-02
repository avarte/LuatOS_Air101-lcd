from machine import Pin, SPI
from encoder import SimpleEncoder
from st77352 import TFT
from sysfont import sysfont
import utime

# =============================================================================
# === ИНИЦИАЛИЗАЦИЯ ===========================================================
# =============================================================================

enc = SimpleEncoder(dt=0, clk=1, sw=12)

spi = SPI(1, baudrate=40000000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))
tft = TFT(spi, 6, 10, 7)
tft.init_7735(tft.GREENTAB80x160)
tft.rotation(3)

# =============================================================================
# === ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ===================================================
# =============================================================================

values = [0, 0, 0]
selected_row = 0
total_rows = 3

bar_x = 5
bar_y_start = 20
bar_width = 100
bar_height = 14
bar_gap = 6
min_val = 0
max_val = 100

label_x = 115
full_width = 150  # Вся строка включая метку

# =============================================================================
# === ОТРИСОВКА ===============================================================
# =============================================================================

def draw_header():
    tft.fillrect((0, 0), (160, 14), TFT.BLACK)
    tft.text((44, 2), "ENCODER TEST", TFT.YELLOW, sysfont, 1)

def draw_bar(y, value, selected):
    """Рисование ОДНОЙ полосы прокрутки"""
    row_num = (y - bar_y_start) // (bar_height + bar_gap)
    
    # Очищаем ВСЮ строку
    tft.fillrect((bar_x, y), (full_width, bar_height), TFT.BLACK)
    
    if selected:
        # ВЫБРАНО: белый фон ВСЕЙ строки
        tft.fillrect((bar_x, y), (full_width, bar_height), TFT.WHITE)
        text_color = TFT.BLACK  # Чёрный текст
    else:
        # НЕ ВЫБРАНО: чёрный фон ВСЕЙ строки
        tft.fillrect((bar_x, y), (full_width, bar_height), TFT.BLACK)
        text_color = TFT.WHITE  # Белый текст
    
    # Полоса заполнения ВСЕГДА зелёная
    fill_color = TFT.GREEN
    
    # Значение
    value_str = f"{value:03d}"
    tft.text((bar_x + 3, y + 2), value_str, text_color, sysfont, 1)
    
    # Полоса заполнения
    fill_max_width = bar_width - 35
    fill_width = int((value / max_val) * fill_max_width)
    tft.fillrect((bar_x + 30, y + 2), (fill_width, bar_height - 4), fill_color)
    
    # Метка (тем же цветом что и текст)
    label = f"Row {row_num}"
    tft.text((label_x, y + 2), label, text_color, sysfont, 1)

def draw_all_bars():
    for i in range(total_rows):
        y = bar_y_start + i * (bar_height + bar_gap)
        draw_bar(y, values[i], i == selected_row)

def draw_interface():
    tft.fill(TFT.BLACK)
    draw_header()
    draw_all_bars()

def update_bar(row):
    y = bar_y_start + row * (bar_height + bar_gap)
    draw_bar(y, values[row], row == selected_row)

def update_all_bars():
    for i in range(total_rows):
        y = bar_y_start + i * (bar_height + bar_gap)
        draw_bar(y, values[i], i == selected_row)

# =============================================================================
# === ГЛАВНЫЙ ЦИКЛ ============================================================
# =============================================================================

print("\n========================================")
print("ENCODER TEST")
print("========================================")
print("DT:  GPIO0")
print("CLK: GPIO1")
print("SW:  GPIO12")
print("========================================\n")

draw_interface()
print(f"Initial: Row={selected_row}  Values={values}")

last_button_state = False

while True:
    rotation = enc.read_rotation()
    
    if rotation != 0:
        old_value = values[selected_row]
        
        if rotation > 0:
            values[selected_row] += 1
            if values[selected_row] > max_val:
                values[selected_row] = max_val
        else:
            values[selected_row] -= 1
            if values[selected_row] < min_val:
                values[selected_row] = min_val
        
        update_bar(selected_row)
        print(f"Row {selected_row}: {old_value} → {values[selected_row]}")
    
    button = enc.read_button()
    
    if button and not last_button_state:
        old_row = selected_row
        selected_row = (selected_row + 1) % total_rows
        update_all_bars()
        print(f"Row: {old_row} → {selected_row}")
    
    last_button_state = button
    
    utime.sleep_ms(5)