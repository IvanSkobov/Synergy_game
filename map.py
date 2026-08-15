# map.py
# Класс игровой карты

import random
from config import *
from display import tile


class Map:
    """Класс игровой карты"""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.cells = [[0 for _ in range(w)] for _ in range(h)]
        self.weather = '☀'
        self.weather_timer = 0

    def check_bounds(self, x, y):
        return 0 <= x < self.h and 0 <= y < self.w

    def generate_forest(self, r, mxr):
        for ri in range(self.h):
            for ci in range(self.w):
                if randbool(r, mxr):
                    self.cells[ri][ci] = 1

    def generate_rivers(self, count):
        for _ in range(count):
            length = self.w * self.h // 4
            x, y = randcell(self.w, self.h)
            for _ in range(length):
                if self.check_bounds(x, y):
                    self.cells[x][y] = 3
                nx, ny = randcell2(x, y)
                if self.check_bounds(nx, ny):
                    x, y = nx, ny
                else:
                    x, y = randcell(self.w, self.h)

    def _empty_cells(self):
        return [
            (ri, ci)
            for ri in range(self.h)
            for ci in range(self.w)
            if self.cells[ri][ci] == 0
        ]

    def generate_buildings(self):
        empty = self._empty_cells()

        while len(empty) < 2:
            ri = random.randint(0, self.h - 1)
            ci = random.randint(0, self.w - 1)
            if self.cells[ri][ci] != 3:
                self.cells[ri][ci] = 0
                empty = self._empty_cells()

        hx, hy = random.choice(empty)
        self.cells[hx][hy] = 5
        empty = [(r, c) for r, c in empty if (r, c) != (hx, hy)]

        sx, sy = random.choice(empty)
        self.cells[sx][sy] = 6

    def _cell_symbol(self, ri, ci, helicopter=None, clouds=None):
        if helicopter and helicopter.x == ri and helicopter.y == ci:
            return HELICOPTER
        if clouds is not None:
            c = clouds[ri][ci]
            if c == 2:
                return THUNDER
            if c == 1:
                return CLOUD
        return CELL_TYPES.get(self.cells[ri][ci], '🟩')

    def print_map(self, helicopter=None, clouds=None):
        """
        Печатает поле одной порцией: каждая строка — готовая строка
        из выровненных tile(), чтобы ⬛ не «убегали».
        """
        border = tile(FRAME)
        lines = []

        top = border * (self.w + 2)
        lines.append(top)

        for ri in range(self.h):
            parts = [border]
            for ci in range(self.w):
                parts.append(tile(self._cell_symbol(ri, ci, helicopter, clouds)))
            parts.append(border)
            lines.append(''.join(parts))

        lines.append(top)
        # Один print — меньше шансов, что буфер порвёт строку посередине
        print('\n'.join(lines))

    def get_cell(self, x, y):
        if self.check_bounds(x, y):
            return self.cells[x][y]
        return None

    def set_cell(self, x, y, value):
        if self.check_bounds(x, y):
            self.cells[x][y] = value

    def update_weather(self):
        self.weather_timer += 1
        if self.weather_timer > random.randint(10, 30):
            self.weather = random.choice(WEATHER_TYPES)
            self.weather_timer = 0
            return True
        return False

    def get_weather_effect(self, key):
        return WEATHER_EFFECTS.get(self.weather, {}).get(key, 1.0)
