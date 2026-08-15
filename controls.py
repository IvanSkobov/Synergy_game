# controls.py
# Чтение клавиш: Windows-консоль (msvcrt) или пошаговый ввод в IDE

import sys


def is_interactive_console():
    """Настоящий терминал (PyCharm Terminal / cmd), не окно Run."""
    try:
        return bool(sys.stdin.isatty() and sys.stdout.isatty())
    except Exception:
        return False


def poll_key_windows():
    """
    Неблокирующее чтение одной клавиши (Windows).
    Возвращает символ в нижнем регистре или None.
    """
    try:
        import msvcrt
    except ImportError:
        return None

    if not msvcrt.kbhit():
        return None

    ch = msvcrt.getch()
    # Служебные/стрелки: префикс 00 или E0 — второй байт отбрасываем
    if ch in (b'\x00', b'\xe0'):
        if msvcrt.kbhit():
            msvcrt.getch()
        return None

    if ch == b'\r':
        return None
    if ch == b' ':
        return ' '
    if ch == b'\x1b':  # Esc = выход
        return 'q'

    try:
        return ch.decode('utf-8', errors='ignore').lower()
    except Exception:
        return None


def read_step_command():
    """
    Один ход через input() — работает в PyCharm Run.
    Пустая строка = просто следующий тик без действия.
    """
    try:
        raw = input('Ход [WASD/пробел/E/H/U/P/Q, Enter=ждать]: ')
    except EOFError:
        return 'q'
    if not raw:
        return ''
    # пробел как команда
    if raw == ' ' or raw.lower() == 'space':
        return ' '
    return raw[0].lower()
