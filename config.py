# config.py
# Конфигурация игры

import random

# Размеры карты по умолчанию (уже — меньше риск переноса строк в консоли)
DEFAULT_WIDTH = 15
DEFAULT_HEIGHT = 10

# ТИКИ (время между обновлениями)
TICK_SLEEP = 0.35
DAMAGE_COOLDOWN_TICKS = 5
CLEAR_TICKS_FOR_VICTORY = 15

# Рамка карты (без variation selector)
FRAME = '⬛'

# Типы клеток — без \uFE0F, чтобы ширина была стабильной
CELL_TYPES = {
    0: '🟩',  # Трава
    1: '🌲',  # Дерево
    2: '🔥',  # Пожар
    3: '🌊',  # Вода
    4: '💀',  # Сгоревшее
    5: '🏥',  # Госпиталь
    6: '🏦',  # Магазин
    7: '🌱',  # Молодое дерево
}

HELICOPTER = '🚁'
# Облака без VS16 (FE0F) — иначе правая ⬛ «уезжает»
CLOUD = '☁'
THUNDER = '⚡'

# Параметры генерации
FOREST_DENSITY = 30
RIVER_COUNT = 1
FIRE_SPAWN_RATE = 5
TREE_GROW_RATE = 3

# Параметры вертолета
MAX_LIVES = 20
START_LIVES = 20
START_TANK = 0
MAX_TANK = 5
SCORE_EXTINGUISH = 10   # очки за тушение
SCORE_BURN_PENALTY = 5  # штраф, если дерево сгорело

UPGRADE_COST = {
    'tank': 100,
    'lives': 150,
    'speed': 200
}

# Погода (символы без FE0F где возможно)
WEATHER_TYPES = ['☀', '⛅', '☁', '🌧', '⛈']
WEATHER_EFFECTS = {
    '☀': {'fire_spread': 1.5, 'tree_grow': 1.0},
    '⛅': {'fire_spread': 1.0, 'tree_grow': 1.0},
    '☁': {'fire_spread': 0.8, 'tree_grow': 0.8},
    '🌧': {'fire_spread': 0.3, 'tree_grow': 1.5},
    '⛈': {'fire_spread': 2.0, 'tree_grow': 0.5},
    # совместимость со старыми сохранениями
    '☀️': {'fire_spread': 1.5, 'tree_grow': 1.0},
    '☁️': {'fire_spread': 0.8, 'tree_grow': 0.8},
    '🌧️': {'fire_spread': 0.3, 'tree_grow': 1.5},
    '⛈️': {'fire_spread': 2.0, 'tree_grow': 0.5},
}

CONTROLS = {
    'up': 'w',
    'down': 's',
    'left': 'a',
    'right': 'd',
    'water': 'space',
    'extinguish': 'e',
    'heal': 'h',
    'upgrade': 'u',
    'pause': 'p',
    'quit': 'q',
    'save': 's (на паузе)',
    'load': 'l (на паузе)'
}


def randbool(r, mxr):
    return random.randint(0, mxr) <= r


def randcell(w, h):
    return (random.randint(0, h - 1), random.randint(0, w - 1))


def randcell2(x, y):
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    d = random.choice(dirs)
    return (x + d[0], y + d[1])
