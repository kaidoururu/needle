# -*- coding: utf-8 -*-
# Сохранение прогресса: hay_save.json рядом с файлами игры

import json
import os

from game_config import *

# Сохранение пишем в папку, в которую реально можно писать: на APK
# cwd бывает недоступен (обычно "/") — раньше сохранение могло молча
# не работать и «Продолжить» никогда не появлялось (r20)
SAVE_FILE = os.path.join(data_dir(), "hay_save.json")


class SaveMixin:
    """Сохранение и загрузка прогресса в hay_save.json"""

    def save_game(self):
        data = {
            "level": self.level,
            "money": self.money,
            "hay": self.hay,
            "hay_value": self.hay_value,
            "shovel": self.shovel,
            "cap_lvl": self.cap_lvl,
            "regen_lvl": self.regen_lvl,
            "price_lvl": self.price_lvl,
            "health_lvl": self.health_lvl,
            "bnd_lvl": self.bnd_lvl,
            "bandages": self.bandages,
            "antidotes": self.antidotes,
            "streak": self.streak,
            "max_stamina": self.max_stamina,
            "max_health": self.max_health,
            "tut_bandage_done": self.tut_bandage_done,
            "tut_antidote_done": self.tut_antidote_done,
            "mercy_used": self.mercy_used,
            "tut_shop_done": self.tut_shop_done,
        }
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError:
            pass



    def load_game(self):
        if not os.path.exists(SAVE_FILE):
            return
        self.has_save = True
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            return
        try:
            self.level = max(1, int(data.get("level", 1)))
            self.money = int(data.get("money", 0))
            self.hay = int(data.get("hay", 0))
            self.hay_value = int(data.get("hay_value", 0))
            self.shovel = max(1, int(data.get("shovel", 1)))
            self.cap_lvl = int(data.get("cap_lvl", 0))
            self.regen_lvl = int(data.get("regen_lvl", 0))
            self.price_lvl = int(data.get("price_lvl", 0))
            self.health_lvl = int(data.get("health_lvl", 0))
            self.bnd_lvl = int(data.get("bnd_lvl", 0))
            self.bandages = int(data.get("bandages", 0))
            self.antidotes = int(data.get("antidotes", 0))
            self.streak = int(data.get("streak", 0))
            self.max_stamina = float(data.get("max_stamina", STAMINA_BASE))
            self.max_health = float(data.get("max_health", HEALTH_BASE))
            self.tut_bandage_done = bool(
                data.get("tut_bandage_done", False))
            self.tut_antidote_done = bool(
                data.get("tut_antidote_done", False))
            self.mercy_used = bool(data.get("mercy_used", False))
            self.tut_shop_done = bool(
                data.get("tut_shop_done", False))
        except (TypeError, ValueError):
            pass
