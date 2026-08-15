# display.py
# Очистка экрана и выравнивание эмодзи-клеток

import os
import sys
import unicodedata


def enable_ansi():
    """Включает ANSI-коды в консоли Windows 10+."""
    if os.name != 'nt':
        return
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        # Прячем курсор — меньше мерцания
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()
    except Exception:
        pass


def show_cursor():
    try:
        sys.stdout.write('\033[?25h')
        sys.stdout.flush()
    except Exception:
        pass


def clear_screen():
    """Рисует следующий кадр с верхнего левого угла."""
    # 2J — очистить, H — курсор в (1,1)
    sys.stdout.write('\033[2J\033[H')
    sys.stdout.flush()


def _display_width(text):
    """Приблизительная ширина строки в колонках терминала."""
    width = 0
    for ch in text:
        if unicodedata.combining(ch):
            continue
        if ch in ('\ufe0f', '\ufe0e', '\u200d'):
            continue
        ea = unicodedata.east_asian_width(ch)
        width += 2 if ea in ('F', 'W') else 1
    return width


# Символы, которые в Windows-шрифтах часто рисуются уже, чем считает Unicode
_FORCE_PAD = frozenset('☁⚡☀⛅⛈🌧★☆')


def tile(symbol):
    """
    Нормализует эмодзи клетки до стабильной ширины 2.
    Иначе ⚡/☁ уже ⬛ — и границы «убегают».
    """
    if not symbol:
        return '🟩'
    cleaned = symbol.replace('\ufe0f', '').replace('\ufe0e', '')
    # Берём первую «базовую» графему без variation selector
    cleaned = cleaned[0] if cleaned else '🟩'

    w = _display_width(cleaned)
    if cleaned in _FORCE_PAD or w < 2:
        return cleaned + ' '
    return cleaned
