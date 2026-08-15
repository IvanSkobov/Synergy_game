# clouds.py
# Класс управления погодой и облаками на карте

import random
from config import *


class CloudManager:
    """Облака на поле + смена погоды"""

    def __init__(self, map_obj, fire_manager=None):
        self.map = map_obj
        self.fire_manager = fire_manager
        self.clouds = [[0 for _ in range(map_obj.w)] for _ in range(map_obj.h)]
        self.lightning_timer = 0
        self._seed_clouds()

    def _seed_clouds(self):
        for ri in range(self.map.h):
            for ci in range(self.map.w):
                if random.random() < 0.08:
                    self.clouds[ri][ci] = 2 if random.random() < 0.25 else 1

    def update_weather(self):
        self.map.update_weather()
        self._move_clouds()

        if self.map.weather == '⛈':
            self.lightning_timer += 1
            if self.lightning_timer > 3:
                self.lightning_timer = 0
                return self.strike_lightning()
        else:
            self.lightning_timer = 0

        return False

    def _move_clouds(self):
        h, w = self.map.h, self.map.w
        new_clouds = [[0 for _ in range(w)] for _ in range(h)]

        for ri in range(h):
            for ci in range(w - 1):
                new_clouds[ri][ci + 1] = self.clouds[ri][ci]
            if random.random() < 0.1:
                new_clouds[ri][0] = 2 if random.random() < 0.2 else 1

        self.clouds = new_clouds

        if self.map.weather in ('⛈', '⛅', '☁'):
            for ri in range(h):
                for ci in range(w):
                    if self.clouds[ri][ci] == 2 and self.map.cells[ri][ci] == 1:
                        if random.random() < 0.02:
                            self.map.cells[ri][ci] = 2
                            if self.fire_manager is not None:
                                self.fire_manager.add_fire(ri, ci)

    def strike_lightning(self):
        x, y = randcell(self.map.w, self.map.h)
        self.clouds[x][y] = 2
        cell = self.map.cells[x][y]

        if cell == 1:
            self.map.cells[x][y] = 2
            if self.fire_manager is not None:
                self.fire_manager.add_fire(x, y)
            return f"⚡ Молния в дерево! ({x}, {y})"
        if cell == 3:
            return f"⚡ Молния в воду! ({x}, {y})"
        return False

    def cloud_at(self, x, y):
        if self.map.check_bounds(x, y):
            return self.clouds[x][y]
        return 0

    def get_weather_info(self):
        weather = self.map.weather
        labels = {
            '☀': 'жарко',
            '⛅': 'облачно',
            '☁': 'пасмурно',
            '🌧': 'дождь',
            '⛈': 'гроза',
        }
        label = labels.get(weather, '')
        return f'{weather} {label}'.strip()
