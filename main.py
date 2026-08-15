# main.py
# Главный файл игры "Пожарный вертолет"

import time
import sys
import random

# UTF-8 в консоли Windows (эмодзи в print)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import *
from map import Map
from helicopter import Helicopter
from fires import FireManager
from clouds import CloudManager
from exporter import save_game
from importer import load_game
from display import enable_ansi, clear_screen, show_cursor
from controls import is_interactive_console, poll_key_windows, read_step_command


class Game:
    """Основной класс игры"""

    def __init__(self, w=DEFAULT_WIDTH, h=DEFAULT_HEIGHT, step_mode=None):
        self.width = w
        self.height = h
        self.running = True
        self.paused = False
        self.tick_count = 0
        self.clear_ticks = 0
        self.game_message = ""
        self.message_ticks = 0

        # step_mode=True: PyCharm Run — ход через input(), экран не «летит»
        if step_mode is None:
            step_mode = not is_interactive_console()
        self.step_mode = step_mode

        self.map = Map(w, h)
        self.map.generate_forest(FOREST_DENSITY, 100)
        self.map.generate_rivers(RIVER_COUNT)
        self.map.generate_buildings()

        self.helicopter = Helicopter(w, h)
        self.fire_manager = FireManager(self.map)
        self.cloud_manager = CloudManager(self.map, self.fire_manager)

        self.fire_spawn_timer = 0

    def _apply_loaded(self, loaded):
        if not loaded:
            return False
        self.map, self.helicopter, self.fire_manager, self.cloud_manager = loaded
        self.cloud_manager.fire_manager = self.fire_manager
        self.width = self.map.w
        self.height = self.map.h
        self.clear_ticks = 0
        return True

    def handle_char(self, k):
        """Обрабатывает одну клавишу (символ)."""
        if not k:
            return

        if k == 'p':
            self.paused = not self.paused
            self.game_message = (
                'Игра приостановлена' if self.paused else 'Игра продолжена'
            )
            self.message_ticks = 10
            return
        if k == 'q':
            self.running = False
            return

        if self.paused:
            if k == 's':
                save_game(
                    self.map, self.helicopter,
                    self.fire_manager, self.cloud_manager
                )
                self.game_message = "Игра сохранена"
                self.message_ticks = 10
            elif k == 'l':
                loaded = load_game()
                if self._apply_loaded(loaded):
                    self.game_message = "Игра загружена"
                else:
                    self.game_message = "Не удалось загрузить игру"
                self.message_ticks = 10
            return

        if k == 'w':
            self.helicopter.move_up(self.map, self.fire_manager)
        elif k == 's':
            self.helicopter.move_down(self.map, self.fire_manager)
        elif k == 'a':
            self.helicopter.move_left(self.map, self.fire_manager)
        elif k == 'd':
            self.helicopter.move_right(self.map, self.fire_manager)
        elif k == ' ':
            self.helicopter.take_water(self.map)
        elif k == 'e':
            self.helicopter.extinguish_fire(self.map, self.fire_manager)
        elif k == 'h':
            self.helicopter.heal(self.map)
        elif k == 'u':
            self.helicopter.upgrade_tank(self.map)

        # Статус действия вертолёта показываем ограниченное время
        if self.helicopter.status:
            self.game_message = self.helicopter.status
            self.helicopter.status = ""
            self.message_ticks = 8

    def poll_input(self):
        """Забирает все нажатые клавиши за кадр (realtime)."""
        while True:
            k = poll_key_windows()
            if k is None:
                break
            self.handle_char(k)

    def update(self):
        if self.paused:
            return

        self.tick_count += 1
        self.helicopter.tick_cooldowns()

        if self.message_ticks > 0:
            self.message_ticks -= 1
            if self.message_ticks == 0:
                self.game_message = ""
                self.helicopter.status = ""

        lightning_msg = self.cloud_manager.update_weather()
        if lightning_msg:
            self.game_message = lightning_msg
            self.message_ticks = 8

        fire_spread = self.map.get_weather_effect('fire_spread')
        tree_grow = self.map.get_weather_effect('tree_grow')

        self.fire_spawn_timer += 1
        if self.fire_spawn_timer > 10 and random.random() < 0.01 * fire_spread:
            if self.fire_manager.spawn_fire():
                self.fire_spawn_timer = 0

        self.fire_manager.spread_fire(fire_spread)

        if self.map.weather == '🌧':
            rained = self.fire_manager.rain_extinguish(0.12)
            if rained:
                self.game_message = f"🌧 Дождь потушил: {rained}"
                self.message_ticks = 8

        self.fire_manager.update_fires(self.helicopter)
        if self.helicopter.status and not self.game_message:
            self.game_message = self.helicopter.status
            self.helicopter.status = ""
            self.message_ticks = 8

        self.fire_manager.grow_trees(tree_grow)

        if self.map.get_cell(self.helicopter.x, self.helicopter.y) == 2:
            if self.helicopter.take_damage():
                self.game_over()
                return
            if self.helicopter.status:
                self.game_message = self.helicopter.status
                self.helicopter.status = ""
                self.message_ticks = 8

        if self.cloud_manager.cloud_at(self.helicopter.x, self.helicopter.y) == 2:
            if self.helicopter.take_damage():
                self.game_over()
                return
            if self.helicopter.status:
                self.game_message = self.helicopter.status
                self.helicopter.status = ""
                self.message_ticks = 8

        if self.fire_manager.get_fire_count() == 0:
            if self.fire_manager.total_spawned > 0:
                self.clear_ticks += 1
                if self.clear_ticks >= CLEAR_TICKS_FOR_VICTORY:
                    self.victory()
        else:
            self.clear_ticks = 0

    def render(self):
        if not self.step_mode:
            clear_screen()

        self.helicopter.print_stats()
        self.map.print_map(self.helicopter, self.cloud_manager.clouds)

        mode = "ПОШАГОВО" if self.step_mode else "REALTIME"
        print(f'TICK {self.tick_count} | {self.cloud_manager.get_weather_info()} | {mode}')

        if self.game_message:
            print(self.game_message)

        print('WASD движ (вода/тушение при пролёте) | H госпиталь | U магазин | P пауза | Q выход')
        if self.paused:
            print('ПАУЗА: S сохранить | L загрузить')

        sys.stdout.flush()

    def game_over(self):
        self.running = False
        print('\n' + '=' * 60)
        print('ИГРА ОКОНЧЕНА')
        print('=' * 60)
        print(f'Очки: {self.helicopter.score}')
        print(f'Сгорело деревьев: {self.fire_manager.get_burnt_count()}')
        print('=' * 60)

    def victory(self):
        self.running = False
        print('\n' + '=' * 60)
        print('ПОБЕДА!')
        print('=' * 60)
        print(f'Очки: {self.helicopter.score}')
        saved = max(0, self.tick_count - self.fire_manager.get_burnt_count())
        print(f'Деревьев спасено (оценка): {saved}')
        print('=' * 60)

    def run(self):
        enable_ansi()
        print('Добро пожаловать в игру "Пожарный вертолет"!')

        if self.step_mode:
            print()
            print('!!! Сейчас окно Run / не Terminal.')
            print('Управление: вводи букву и жми Enter (w/a/s/d/e/...).')
            print('Пустой Enter = один тик без хода.')
            print('Для realtime: Terminal → python main.py')
            print()
        else:
            print('Realtime: жми WASD прямо в этом окне (фокус на Terminal).')
            print()

        time.sleep(0.8)

        while self.running:
            if self.step_mode:
                # Сначала рисуем, потом ждём команду — ничего не «летит»
                self.render()
                if not self.running:
                    break
                cmd = read_step_command()
                self.handle_char(cmd)
                if self.running and not self.paused:
                    self.update()
                elif self.running and self.paused and cmd in ('s', 'l', 'p', 'q'):
                    pass
            else:
                self.poll_input()
                self.update()
                if not self.running:
                    break
                self.render()
                time.sleep(TICK_SLEEP)

        show_cursor()
        print('\nСпасибо за игру!')


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--load' and len(sys.argv) > 2:
            loaded = load_game(sys.argv[2])
            if loaded:
                game = Game()
                game._apply_loaded(loaded)
                game.run()
                return
            print('Не удалось загрузить сохранение.')
            return
        if sys.argv[1] == '--help':
            print('Использование: python main.py [OPTIONS]')
            print('  --load FILE  - загрузить игру из файла')
            print('  --step       - пошаговый режим (для окна Run)')
            print('  --realtime   - форсировать realtime (нужен Terminal)')
            print('  --help       - справка')
            return

    force_step = '--step' in sys.argv
    force_realtime = '--realtime' in sys.argv

    try:
        w_input = input(f'Введите ширину карты (по умолчанию {DEFAULT_WIDTH}): ')
        w = int(w_input) if w_input.strip() else DEFAULT_WIDTH

        h_input = input(f'Введите высоту карты (по умолчанию {DEFAULT_HEIGHT}): ')
        h = int(h_input) if h_input.strip() else DEFAULT_HEIGHT
    except ValueError:
        w, h = DEFAULT_WIDTH, DEFAULT_HEIGHT

    w = max(5, w)
    h = max(5, h)

    if force_step:
        step_mode = True
    elif force_realtime:
        step_mode = False
    else:
        step_mode = None  # авто: Run → step, Terminal → realtime

    game = Game(w, h, step_mode=step_mode)
    game.run()


if __name__ == "__main__":
    main()
