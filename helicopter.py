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

    def move(self, dx, dy, map_obj=None, fire_manager=None):
        """Перемещает вертолет; после хода — авто-действия на клетке"""
        nx = self.x + dx
        ny = self.y + dy
        if 0 <= nx < self.h and 0 <= ny < self.w:
            self.x = nx
            self.y = ny
            if map_obj is not None:
                self.process_cell(map_obj, fire_manager)
            return True
        return False

    def move_up(self, map_obj=None, fire_manager=None):
        return self.move(-1, 0, map_obj, fire_manager)

    def move_down(self, map_obj=None, fire_manager=None):
        return self.move(1, 0, map_obj, fire_manager)

    def move_left(self, map_obj=None, fire_manager=None):
        return self.move(0, -1, map_obj, fire_manager)

    def move_right(self, map_obj=None, fire_manager=None):
        return self.move(0, 1, map_obj, fire_manager)

    def process_cell(self, map_obj, fire_manager=None):
        """
        По заданию: пролетая над водой — берёт воду в резервуар.
        Над пожаром при наличии воды — тушит дерево.
        """
        cell = map_obj.get_cell(self.x, self.y)
        if cell == 3:
            self.take_water(map_obj, quiet_if_full=True)
        elif cell == 2 and self.tank > 0:
            self.extinguish_fire(map_obj, fire_manager)

    def take_water(self, map_obj, quiet_if_full=False):
        """Забирает воду из реки"""
        if self.tank >= self.mxtank:
            if not quiet_if_full:
                self._set_status("Резервуар полон!")
            return False

        cell = map_obj.get_cell(self.x, self.y)
        if cell == 3:
            self.tank += 1
            self._set_status(f"Взята вода! {self.tank}/{self.mxtank}")
            return True

        self._set_status("Здесь нет воды!")
        return False

    def extinguish_fire(self, map_obj, fire_manager=None):
        """Тушит пожар — получаем очки"""
        if self.tank <= 0:
            self._set_status("Нет воды в резервуаре!")
            return False

        cell = map_obj.get_cell(self.x, self.y)
        if cell == 2:
            map_obj.set_cell(self.x, self.y, 7)  # Молодое дерево
            if fire_manager is not None:
                fire_manager.extinguish_fire(self.x, self.y)
            self.tank -= 1
            self.score += SCORE_EXTINGUISH
            self._set_status(f"Пожар потушен! +{SCORE_EXTINGUISH} очков")
            return True

        self._set_status("Здесь нет пожара!")
        return False

    def lose_points(self, amount):
        """Штраф за сгоревшее дерево"""
        self.score = max(0, self.score - amount)
        self._set_status(f"Дерево сгорело! -{amount} очков (всего {self.score})")

    def heal(self, map_obj):
        """Госпиталь: здоровье за очки"""
        cell = map_obj.get_cell(self.x, self.y)
        if cell == 5:
            if self.score >= 30 and self.lives < self.max_lives:
                self.score -= 30
                self.lives += 1
                self._set_status(f"Госпиталь! Жизней: {self.lives}")
                return True
            if self.lives >= self.max_lives:
                self._set_status("Жизни на максимуме!")
            else:
                self._set_status("Нужно 30 очков для лечения")
            return False
        self._set_status("Здесь нет госпиталя!")
        return False

    def upgrade_tank(self, map_obj):
        """Магазин: увеличить число резервуаров"""
        cell = map_obj.get_cell(self.x, self.y)
        if cell == 6:
            cost = UPGRADE_COST['tank'] * self.mxtank
            if self.score >= cost and self.mxtank < MAX_TANK:
                self.score -= cost
                self.mxtank += 1
                self._set_status(f"Улучшение! Резервуаров: {self.mxtank}")
                return True
            if self.mxtank >= MAX_TANK:
                self._set_status("Максимум резервуаров!")
            else:
                self._set_status(f"Нужно {cost} очков для улучшения")
            return False
        self._set_status("Здесь нет магазина!")
        return False

    def print_stats(self):
        print(f'🪣 {self.tank}/{self.mxtank} | 🏆 {self.score} | 💛 {self.lives}')

    def take_damage(self):
        if self.damage_cooldown > 0:
            return False
        self.lives -= 1
        self.damage_cooldown = DAMAGE_COOLDOWN_TICKS
        self._set_status(f"Вертолет поврежден! Жизней: {self.lives}")
        if self.lives <= 0:
            self._set_status("Вертолет уничтожен!")
            return True
        return False

    def tick_cooldowns(self):
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
