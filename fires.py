# fires.py
# Класс управления пожарами

import random
from config import *


class FireManager:
    """Пожары, сгорание и рост деревьев"""

    def __init__(self, map_obj):
        self.map = map_obj
        self.fires = []
        self.burnt_trees = 0
        self.total_spawned = 0

    def spawn_fire(self):
        """Пожар в случайном дереве"""
        trees = []
        for ri in range(self.map.h):
            for ci in range(self.map.w):
                if self.map.cells[ri][ci] == 1:
                    trees.append((ri, ci))

        if trees:
            x, y = random.choice(trees)
            self.map.cells[x][y] = 2
            self.fires.append((x, y))
            self.total_spawned += 1
            return True
        return False

    def spread_fire(self, weather_effect=1.0):
        """Пожар перекидывается на соседние деревья"""
        new_fires = []
        for x, y in self.fires:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.map.check_bounds(nx, ny):
                    if self.map.cells[nx][ny] == 1 and random.random() < 0.3 * weather_effect:
                        self.map.cells[nx][ny] = 2
                        new_fires.append((nx, ny))

        self.fires.extend(new_fires)
        self.total_spawned += len(new_fires)
        return len(new_fires)

    def update_fires(self, helicopter=None):
        """
        Обновляет пожары. Сгоревшее дерево → клетка 💀 и штраф очков.
        """
        burnt = []
        stale = []
        burned_now = 0

        for i, (x, y) in enumerate(self.fires):
            if self.map.cells[x][y] != 2:
                stale.append(i)
                continue

            if random.random() < 0.2:
                self.map.cells[x][y] = 4  # сгорело
                self.burnt_trees += 1
                burned_now += 1
                burnt.append(i)

        for i in sorted(set(burnt + stale), reverse=True):
            del self.fires[i]

        if burned_now and helicopter is not None:
            penalty = SCORE_BURN_PENALTY * burned_now
            helicopter.lose_points(penalty)

        return burned_now

    def extinguish_fire(self, x, y):
        for i, (fx, fy) in enumerate(self.fires):
            if fx == x and fy == y:
                del self.fires[i]
                return True
        return False

    def add_fire(self, x, y):
        if self.map.cells[x][y] == 2 and (x, y) not in self.fires:
            self.fires.append((x, y))
            self.total_spawned += 1
            return True
        return False

    def rain_extinguish(self, chance=0.15):
        extinguished = 0
        for x, y in list(self.fires):
            if self.map.cells[x][y] == 2 and random.random() < chance:
                self.map.cells[x][y] = 7
                self.extinguish_fire(x, y)
                extinguished += 1
        return extinguished

    def get_fire_count(self):
        return len(self.fires)

    def get_burnt_count(self):
        return self.burnt_trees

    def grow_trees(self, weather_effect=1.0):
        """
        Периодический рост деревьев:
        - 🌱 → 🌲
        - 🟩 → 🌱 (новые деревья)
        - 💀 → 🌱 (восстановление)
        """
        grown = 0
        for ri in range(self.map.h):
            for ci in range(self.map.w):
                cell = self.map.cells[ri][ci]
                if cell == 7 and random.random() < 0.1 * weather_effect:
                    self.map.cells[ri][ci] = 1
                    grown += 1
                elif cell == 0 and random.random() < 0.01 * weather_effect:
                    self.map.cells[ri][ci] = 7
                    grown += 1
                elif cell == 4 and random.random() < 0.02 * weather_effect:
                    self.map.cells[ri][ci] = 7
                    grown += 1
        return grown
