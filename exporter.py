# exporter.py
# Сохранение игры в файл

import json


def save_game(map_obj, helicopter, fire_manager, cloud_manager, filename="save.json"):
    """Сохраняет игру в файл"""

    game_data = {
        'map': {
            'w': map_obj.w,
            'h': map_obj.h,
            'cells': map_obj.cells,
            'weather': map_obj.weather,
            'weather_timer': map_obj.weather_timer
        },
        'helicopter': {
            'x': helicopter.x,
            'y': helicopter.y,
            'tank': helicopter.tank,
            'mxtank': helicopter.mxtank,
            'score': helicopter.score,
            'lives': helicopter.lives,
            'max_lives': helicopter.max_lives,
            'damage_cooldown': helicopter.damage_cooldown,
            'status': helicopter.status
        },
        'fires': {
            'fires': fire_manager.fires,
            'burnt_trees': fire_manager.burnt_trees,
            'total_spawned': fire_manager.total_spawned
        },
        'clouds': {
            'clouds': cloud_manager.clouds,
            'lightning_timer': cloud_manager.lightning_timer
        }
    }

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, indent=4, ensure_ascii=False)
        print(f"✅ Игра сохранена в {filename}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")
        return False
