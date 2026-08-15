# importer.py
# Загрузка игры из файла

import json
import os
from map import Map
from helicopter import Helicopter
from fires import FireManager
from clouds import CloudManager


def load_game(filename="save.json"):
    """Загружает игру из файла. При ошибке возвращает None."""

    if not os.path.exists(filename):
        try:
            print(f"❌ Файл {filename} не найден!")
        except UnicodeEncodeError:
            print(f"File {filename} not found!")
        return None

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            game_data = json.load(f)

        # Восстанавливаем карту
        map_data = game_data['map']
        map_obj = Map(map_data['w'], map_data['h'])
        map_obj.cells = map_data['cells']
        map_obj.weather = map_data['weather']
        map_obj.weather_timer = map_data['weather_timer']

        # Восстанавливаем вертолет
        heli_data = game_data['helicopter']
        helicopter = Helicopter(map_obj.w, map_obj.h)
        helicopter.x = heli_data['x']
        helicopter.y = heli_data['y']
        helicopter.tank = heli_data['tank']
        helicopter.mxtank = heli_data['mxtank']
        helicopter.score = heli_data['score']
        helicopter.lives = heli_data['lives']
        helicopter.max_lives = heli_data['max_lives']
        helicopter.damage_cooldown = heli_data.get('damage_cooldown', 0)
        helicopter.status = heli_data.get('status', '')

        # Восстанавливаем пожары
        fire_manager = FireManager(map_obj)
        fire_manager.fires = [tuple(pos) for pos in game_data['fires']['fires']]
        fire_manager.burnt_trees = game_data['fires']['burnt_trees']
        fire_manager.total_spawned = game_data['fires'].get(
            'total_spawned', len(fire_manager.fires)
        )

        # Восстанавливаем погоду
        cloud_manager = CloudManager(map_obj, fire_manager)
        cloud_manager.clouds = game_data['clouds']['clouds']
        cloud_manager.lightning_timer = game_data['clouds']['lightning_timer']

        print(f"✅ Игра загружена из {filename}")
        return map_obj, helicopter, fire_manager, cloud_manager

    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None
