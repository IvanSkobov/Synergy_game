# helicopter.py
# Класс вертолета

from config import *


class Helicopter:
    """Класс вертолета"""

    def __init__(self, w, h):
        rc = randcell(w, h)
        self.x = rc[0]
        self.y = rc[1]
        self.w = w
        self.h = h
        self.tank = START_TANK
        self.mxtank = 1
        self.score = 0
        self.lives = START_LIVES
        self.max_lives = MAX_LIVES
        self.status = ""
        self.damage_cooldown = 0

    def _set_status(self, message):
        self.status = message

    def move(self, dx, dy):
        """Перемещает вертолет"""
        nx = self.x + dx
        ny = self.y + dy
        if 0 <= nx < self.h and 0 <= ny < self.w:
            self.x = nx
            self.y = ny
            return True
        return False

    def move_up(self):
        """Перемещает вверх"""
        return self.move(-1, 0)

    def move_down(self):
        """Перемещает вниз"""
        return self.move(1, 0)

    def move_left(self):
        """Перемещает влево"""
        return self.move(0, -1)

    def move_right(self):
        """Перемещает вправо"""
        return self.move(0, 1)

    def take_water(self, map_obj):
        """Забирает воду из реки"""
        if self.tank >= self.mxtank:
            self._set_status("Резервуар полон!")
            return False

        cell = map_obj.get_cell(self.x, self.y)
        if cell == 3:  # Вода
            self.tank += 1
            self._set_status(f"Взята вода! {self.tank}/{self.mxtank}")
            return True

        self._set_status("Здесь нет воды!")
        return False

    def extinguish_fire(self, map_obj, fire_manager=None):
        """Тушит пожар"""
        if self.tank <= 0:
            self._set_status("Нет воды в резервуаре!")
            return False

        cell = map_obj.get_cell(self.x, self.y)
        if cell == 2:  # Пожар
            map_obj.set_cell(self.x, self.y, 7)  # Молодое дерево
            if fire_manager is not None:
                fire_manager.extinguish_fire(self.x, self.y)
            self.tank -= 1
            self.score += 10
            self._set_status("🔥 Пожар потушен! +10 очков")
            return True

        self._set_status("Здесь нет пожара!")
        return False

    def heal(self, map_obj):
        """Лечится в госпитале"""
        cell = map_obj.get_cell(self.x, self.y)
        if cell == 5:  # Госпиталь
            if self.score >= 30 and self.lives < self.max_lives:
                self.score -= 30
                self.lives += 1
                self._set_status(f"🏥 Лечение! Жизней: {self.lives}, Очков: {self.score}")
                return True
            if self.lives >= self.max_lives:
                self._set_status("У вас максимальное количество жизней!")
            else:
                self._set_status("Недостаточно очков для лечения! (нужно 30)")
            return False

        self._set_status("Здесь нет госпиталя!")
        return False

    def upgrade_tank(self, map_obj):
        """Улучшает резервуар в магазине"""
        cell = map_obj.get_cell(self.x, self.y)
        if cell == 6:  # Магазин
            cost = UPGRADE_COST['tank'] * self.mxtank
            if self.score >= cost and self.mxtank < MAX_TANK:
                self.score -= cost
                self.mxtank += 1
                self._set_status(f"🏪 Улучшение! Резервуар: {self.mxtank}, Очков: {self.score}")
                return True
            if self.mxtank >= MAX_TANK:
                self._set_status("Максимальный резервуар!")
            else:
                self._set_status(f"Недостаточно очков для улучшения! (нужно {cost})")
            return False

        self._set_status("Здесь нет магазина!")
        return False

    def print_stats(self):
        """HUD: 🪣 | 🏆 | 💛"""
        print(f'🪣 {self.tank}/{self.mxtank} | 🏆 {self.score} | 💛 {self.lives}')

    def take_damage(self):
        """Наносит урон вертолету (с кулдауном)"""
        if self.damage_cooldown > 0:
            return False

        self.lives -= 1
        self.damage_cooldown = DAMAGE_COOLDOWN_TICKS
        self._set_status(f"💥 Вертолет поврежден! Жизней: {self.lives}")
        if self.lives <= 0:
            self._set_status("💀 Вертолет уничтожен!")
            return True
        return False

    def tick_cooldowns(self):
        """Уменьшает кулдауны каждый тик"""
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
