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
            if (not getattr(self, "tut_antidote_done", False)
                    and self.antidotes > 0):
                # урок в очередь с задержкой (пункт 10): сначала игрок
                # секунду видит плашку «Отравление!», потом подсветку
                self.pending_tutorial["antidote"] = self.time + TUT_DELAY
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
            if (not getattr(self, "tut_bandage_done", False)
                    and self.bandages > 0 and self.health > 0):
                # урок в очередь с задержкой (пункт 10): сначала игрок
                # секунду видит плашку «Укус зверя!», потом подсветку
                self.pending_tutorial["bandage"] = self.time + TUT_DELAY
        elif item == "bandage":
            cap = self.bandage_cap()
            if self.bandages < cap:
                self.bandages += 1
                self.show_notice(item)
                self.notice["sub"] = "+1 бинт в запас"
            else:
                self.show_notice(item)
                self.notice["sub"] = "Карман полон — бинт потерян"
        elif item == "antidote":
            cap = self.antidote_cap()
            if self.antidotes < cap:
                self.antidotes += 1
                self.show_notice(item)
                self.notice["sub"] = "+1 противоядие в запас"
            else:
                self.show_notice(item)
                self.notice["sub"] = "Аптечка полна — противоядие потеряно"
        elif item == "compass":
            col = self.needle_idx % self.cols
            row = self.needle_idx // self.cols
            self.compass_quadrant = (row < self.rows / 2,
                                     col < self.cols / 2)
            self.show_notice(item)
            self.notice["sub"] = "Игла в подсвеченной зоне стога"
        elif item == "energy":
            self.energy_time = ENERGY_TIME
            self.show_notice(item)
            self.notice["sub"] = ("%d секунд: энергия не тратится"
                                  % int(ENERGY_TIME))
        elif item == "clover":
            self.clover_time = CLOVER_TIME
            self.show_notice(item)
            self.notice["sub"] = (
                "%d секунд: шанс %d%% спастись от ловушек"
                % (int(CLOVER_TIME), int(CLOVER_SAVE_CHANCE * 100)))

    # ---------- копание ----------



    # ---------- копание ----------
    def resolve_items(self, dug_now):
        """За один рывок срабатывает РОВНО ОДНА ловушка: из всех ловушек
        рывка выбирается самая «плохая» по ITEM_PRIORITY (камень, потом
        зверь, потом растение), остальные ловушки рывка игнорируются —
        нельзя получить сразу несколько укусов или укус и отравление
        одновременно. Клевер проверяется один раз для выбранной ловушки
        и, если спасает, рывок остаётся чистым. Если сработала ловушка —
        найденные в этом же рывке бинты и противоядия теряются. Редкие
        находки (компас, энергетик, клевер) достаются всегда и не
        блокируются ловушками. Возвращает False, если сработала
        ловушка."""
        found = [i for i in dug_now if self.cells[i]["item"]]
        if not found:
            return True
        found_items = [self.cells[i]["item"] for i in found]
        for i in found:
            self.cells[i]["item"] = None
        # редкие находки — всегда игроку
        for it in found_items:
            if it in RARE_ITEMS:
                self.trigger_item(it)
        # ловушки — ровно одна за рывок: из найденных берём самую «плохую»
        # по ITEM_PRIORITY, остальные игнорируются. Клевер проверяется один
        # раз для выбранной ловушки.
        traps = [it for it in found_items if it in ("stone", "animal",
                                                    "plant")]
        trapped = False
        saved = 0
        if traps:
            worst = min(traps, key=lambda it: ITEM_PRIORITY.get(it, 99))
            if (self.clover_time > 0
                    and random.random() < CLOVER_SAVE_CHANCE):
                saved = 1
            else:
                trapped = True
                self.trigger_item(worst)
        if saved:
            self.add_message("Клевер спас от ловушки!", GREEN_MSG)
        # лекарства достают, только если ни одна ловушка не сработала
        meds = [it for it in found_items if it in ("bandage", "antidote")]
        if meds and trapped:
            self.add_message("Найденные лекарства потеряны при ловушке!",
                             RED)
        else:
            for it in meds:
                self.trigger_item(it)
        return not trapped



    def dig_at(self, pos):
        fx = pos[0] - self.field_rect.x
        fy = pos[1] - self.field_rect.y
        cx = int(fx / self.cw)
        cy = int(fy / self.ch)
        if not (0 <= cx < self.cols and 0 <= cy < self.rows):
            return
        side = self.dig_side()
        targets = []
        if side >= DIG_CIRCLE_MIN_SIDE:
            # круг: клетки, чьи центры попадают в радиус от точки клика
            r2 = (DIG_CIRCLE_K * side) ** 2
            ux = fx / self.cw          # клик в клеточных координатах
            uy = fy / self.ch
            span = int(DIG_CIRCLE_K * side) + 1
            for y in range(cy - span, cy + span + 1):
                for x in range(cx - span, cx + span + 1):
                    if not (0 <= x < self.cols and 0 <= y < self.rows):
                        continue
                    dx = x + 0.5 - ux
                    dy = y + 0.5 - uy
                    if dx * dx + dy * dy <= r2:
                        i = y * self.cols + x
                        if not self.cells[i]["dug"]:
                            targets.append(i)
        else:
            r = (side - 1) // 2
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
        # рывок целиком или никак: сил должно хватить на все клетки
        # сразу. Во время энергетика энергия не тратится — и проверка
        # запаса сил не нужна, и запас не уменьшается.
        if self.energy_time <= 0 and self.stamina < len(targets):
            self.add_message("Не хватает сил", RED)
            return
        dug_now = []
        for i in targets:
            if self.energy_time <= 0:
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
                self.compass_quadrant = None
                if self.golden_needle:
                    self.add_message("ЗОЛОТАЯ ИГЛА! Бонус x%d"
                                     % GOLD_NEEDLE_BONUS_MULT, GOLD)
                self.save_game()
        if dug_now:
            self.digs += 1
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
