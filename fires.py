# fires.py
# Класс управления пожарами

import random
from config import *


class FireManager:
    """Класс для управления пожарами"""

    def __init__(self, map_obj):
        self.map = map_obj
        self.fires = []  # Список активных пожаров
        self.burnt_trees = 0  # Счетчик сгоревших деревьев
        self.total_spawned = 0  # Сколько пожаров когда-либо появилось

    def spawn_fire(self):
        """Создает пожар в случайном месте"""
        trees = []
        for ri in range(self.map.h):
            for ci in range(self.map.w):
                if self.map.cells[ri][ci] == 1:  # Дерево
                    trees.append((ri, ci))

        if trees:
            x, y = random.choice(trees)
            self.map.cells[x][y] = 2  # Пожар
            self.fires.append((x, y))
            self.total_spawned += 1
            return True
        return False

    def spread_fire(self, weather_effect=1.0):
        """Распространяет пожары на соседние деревья"""
        new_fires = []

        for x, y in self.fires:
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if self.map.check_bounds(nx, ny):
                    cell = self.map.cells[nx][ny]
                    if cell == 1 and random.random() < 0.3 * weather_effect:
                        self.map.cells[nx][ny] = 2
                        new_fires.append((nx, ny))

        self.fires.extend(new_fires)
        self.total_spawned += len(new_fires)
        return len(new_fires)

    def update_fires(self):
        """Обновляет состояние пожаров"""
        burnt = []
        stale = []

        for i, (x, y) in enumerate(self.fires):
            # Пожар уже потушен или клетка изменилась
            if self.map.cells[x][y] != 2:
                stale.append(i)
                continue

            # С вероятностью 20% дерево сгорает
            if random.random() < 0.2:
                self.map.cells[x][y] = 4  # Сгоревшее дерево
                self.burnt_trees += 1
                burnt.append(i)

        for i in sorted(set(burnt + stale), reverse=True):
            del self.fires[i]

        return len(burnt)

    def extinguish_fire(self, x, y):
        """Тушит пожар в указанной клетке"""
        for i, (fx, fy) in enumerate(self.fires):
            if fx == x and fy == y:
                del self.fires[i]
                return True
        return False

    def add_fire(self, x, y):
        """Регистрирует пожар, если его ещё нет в списке"""
        if self.map.cells[x][y] == 2 and (x, y) not in self.fires:
            self.fires.append((x, y))
            self.total_spawned += 1
            return True
        return False

    def rain_extinguish(self, chance=0.15):
        """Дождь может потушить часть пожаров"""
        extinguished = 0
        for x, y in list(self.fires):
            if self.map.cells[x][y] == 2 and random.random() < chance:
                self.map.cells[x][y] = 7  # Молодое дерево
                self.extinguish_fire(x, y)
                extinguished += 1
        return extinguished

    def get_fire_count(self):
        """Возвращает количество пожаров"""
        return len(self.fires)

    def get_burnt_count(self):
        """Возвращает количество сгоревших деревьев"""
        return self.burnt_trees

    def grow_trees(self, weather_effect=1.0):
        """Выращивает новые деревья"""
        grown = 0
        for ri in range(self.map.h):
            for ci in range(self.map.w):
                if self.map.cells[ri][ci] == 7:  # Молодое дерево
                    if random.random() < 0.1 * weather_effect:
                        self.map.cells[ri][ci] = 1  # Дерево
                        grown += 1
        return grown
