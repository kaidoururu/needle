# -*- coding: utf-8 -*-
# Копание: ловушки, находки, обработка клетки

import math
import random
import pygame

from game_config import *


class DiggingMixin:
    """Копание: ловушки, находки, обработка клетки"""


    # ---------- ловушки ----------
    def trigger_item(self, item):
        if item == "stone":
            if self.shovel >= STONE_IMMUNE_LVL and self.dig_side() >= 7:
                self.money = max(0, self.money - STONE_MONEY_PENALTY)
                self.show_notice(item)
                self.notice["sub"] = ("Лопата крепка: -%d монет"
                                      % STONE_MONEY_PENALTY)
            elif self.shovel >= STONE_IMMUNE_LVL:
                self.show_notice(item)
                self.notice["sub"] = ("Лопата ур.%d держит удар — "
                                      "откатов нет" % self.shovel)
            elif self.shovel > 1:
                old = self.shovel
                self.shovel = max(1, self.shovel - STONE_PENALTY)
                self.show_notice(item)
                self.notice["sub"] = ("Лопата сломана: ур.%d -> ур.%d"
                                      % (old, self.shovel))
            else:
                self.show_notice(item)
                self.notice["sub"] = "Лопата и так минимальная"
        elif item == "plant":
            old = self.health
            self.poison_time = self.poison_duration()
            self.poison_flash = 1.0
            self.show_notice(item)
            self.notice["sub"] = ("Отравление! Здоровье: %d -> %d"
                                  % (int(round(old)),
                                     int(round(self.health))))
            self.add_message("Ядовитое растение! Здоровье: %d -> %d"
                             % (int(round(old)), int(round(self.health))),
                             PURPLE_MSG)
        elif item == "animal":
            old = self.health
            dmg = self.animal_damage()
            self.health -= dmg
            self.bite_flash = 1.0
            self.show_notice(item)
            new_h = max(0, self.health)
            self.notice["sub"] = ("Здоровье: %d -> %d"
                                  % (int(round(old)), int(round(new_h))))
            self.add_message("Укус зверя! Здоровье: %d -> %d"
                             % (int(round(old)), int(round(new_h))),
                             RED)
            if self.health <= 0:
                self.health = 0
                self.dead = True
        elif item == "bandage":
            cap = self.bandage_cap()
            if self.bandages < cap:
                self.bandages += 1
                self.show_notice(item)
                if DEBUG:
                    self.notice["sub"] = "+1 бинт в запас (%d/%d)" % (
                        self.bandages, cap)
                else:
                    self.notice["sub"] = "+1 бинт в запас"
            else:
                self.show_notice(item)
                self.notice["sub"] = "Карман полон — бинт потерян"
        elif item == "antidote":
            cap = self.antidote_cap()
            if self.antidotes < cap:
                self.antidotes += 1
                self.show_notice(item)
                if DEBUG:
                    self.notice["sub"] = "+1 противоядие (%d/%d)" % (
                        self.antidotes, cap)
                else:
                    self.notice["sub"] = "+1 противоядие в запас"
            else:
                self.show_notice(item)
                self.notice["sub"] = "Аптечка полна — противоядие потеряно"
        elif item == "compass":
            col = self.needle_idx % self.cols
            row = self.needle_idx // self.cols
            north = row < self.rows / 2
            west = col < self.cols / 2
            name = {(True, True): "северо-запад",
                    (True, False): "северо-восток",
                    (False, True): "юго-запад",
                    (False, False): "юго-восток"}[(north, west)]
            self.compass_hint = "Компас: игла в %s стога" % name
            self.show_notice(item)
            self.notice["sub"] = self.compass_hint
        elif item == "magnet":
            self.magnet_ready = True
            self.show_notice(item)
            self.notice["sub"] = "Следующий рывок вдвое больше"
        elif item == "clover":
            self.clover_time = CLOVER_TIME
            self.show_notice(item)
            self.notice["sub"] = "30 секунд: шанс 50% спастись от ловушки"

    # ---------- копание ----------



    # ---------- копание ----------
    def resolve_items(self, dug_now):
        """За один рывок срабатывает только одна, худшая базовая находка.
        Приоритет: камень -> укус зверя -> растение -> бинт -> противоядие.
        Редкие находки (компас, магнит, клевер) срабатывают всегда и не
        блокируются ловушками. Возвращает False, если сработала ловушка."""
        found = [i for i in dug_now if self.cells[i]["item"]]
        if not found:
            return True
        rare = [i for i in found if self.cells[i]["item"] in RARE_ITEMS]
        base = [i for i in found if self.cells[i]["item"] not in RARE_ITEMS]
        rare_items = [self.cells[i]["item"] for i in rare]
        base_item = None
        if base:
            worst = min(base,
                        key=lambda i: ITEM_PRIORITY[self.cells[i]["item"]])
            base_item = self.cells[worst]["item"]
        for i in found:
            self.cells[i]["item"] = None
        for it in rare_items:
            self.trigger_item(it)
        if base_item:
            if (base_item in ("stone", "animal", "plant")
                    and self.clover_time > 0
                    and random.random() < CLOVER_SAVE_CHANCE):
                self.add_message("Клевер спас от ловушки!", GREEN_MSG)
                return True
            self.trigger_item(base_item)
            return False
        return True



    def dig_at(self, pos):
        cx = int((pos[0] - self.field_rect.x) / self.cw)
        cy = int((pos[1] - self.field_rect.y) / self.ch)
        if not (0 <= cx < self.cols and 0 <= cy < self.rows):
            return
        side = self.dig_side()
        if self.magnet_ready:
            side = min(14, side * MAGNET_MULT)
        r = (side - 1) // 2
        targets = []
        for dy in range(-r, side - r):
            for dx in range(-r, side - r):
                x, y = cx + dx, cy + dy
                if 0 <= x < self.cols and 0 <= y < self.rows:
                    i = y * self.cols + x
                    if not self.cells[i]["dug"]:
                        targets.append(i)
        random.shuffle(targets)
        if not targets:
            return
        if self.stamina < 1:
            self.add_message("Не хватает сил", RED)
            return
        dug_now = []
        for i in targets:
            if self.stamina < 1:
                break
            self.stamina -= 1
            self.cells[i]["dug"] = True
            dug_now.append(i)
            cell = self.cells[i]
            if cell["hay"]:
                self.hay += 1
                self.hay_value += cell["price"]
                cell["hay"] = False
            if i == self.needle_idx:
                self.won = True
                self.needle_found = True
                self.money += self.needle_bonus()
                self.compass_hint = None
                if self.golden_needle:
                    self.add_message("ЗОЛОТАЯ ИГЛА! Бонус x%d"
                                     % GOLD_NEEDLE_BONUS_MULT, GOLD)
                self.save_game()
        if dug_now:
            self.digs += 1
            self.magnet_ready = False
            self.field_dirty = True
            self.spawn_straws(dug_now)
            safe = self.resolve_items(dug_now)
            if safe:
                self.streak += 1
                if self.streak % STREAK_GOAL == 0:
                    bonus = STREAK_BONUS_BASE * self.level
                    self.money += bonus
                    self.add_message("Серия: %d рывков без ловушек, "
                                     "+%d монет" % (self.streak, bonus),
                                     GOLD)
            else:
                self.streak = 0
