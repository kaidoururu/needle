# -*- coding: utf-8 -*-
# Стог: поле клеток, цены клеток, иголка, рестарт, уровни

import math
import random
import pygame

from game_config import *


class FieldMixin:
    """Стог: поле клеток, цены клеток, иголка, рестарт, уровни"""


    # ---------- стог ----------
    def cell_size(self):
        return max(CELL_MIN, CELL_START - (self.level - 1) * CELL_STEP)



    def cell_base_price(self, shade):
        for border, price in PRICE_TIERS:
            if shade >= border:
                return price
        return PRICE_TIERS[-1][1]



    def price_mult(self):
        """Множитель цены сена: рост с уровнем x апгрейд «ЦЕНА СЕНА»
        из лавки. На 1-м уровне без апгрейда — 1.0, на 5-м — 1.4 и т.д."""
        level_mult = 1.0 + HAY_PRICE_LEVEL_STEP * (self.level - 1)
        upgrade_mult = 1.0 + PRICE_UPGRADE_STEP * self.price_lvl
        return level_mult * upgrade_mult



    def cell_price(self, shade):
        return int(round(self.cell_base_price(shade) * self.price_mult()))


    def trap_growth(self):
        """Множитель ловушек: мягкий старт, разгон после 5-го уровня."""
        if self.level <= 3:
            return 0.75
        if self.level <= 5:
            return 1.0
        if self.level <= 9:
            return 1.25
        return 1.5 + ENDLESS_TRAP_GROWTH * (self.level - 10)


    def avg_trap_mult(self):
        """Средний множитель ловушек по стогу (аналитически из распределения
        оттенков: shade = U^SHADE_POWER)."""
        mean_dark = 1.0 - 1.0 / (SHADE_POWER + 1.0)
        return TRAP_LIGHT_MULT + (TRAP_DARK_MULT - TRAP_LIGHT_MULT) * mean_dark


    def is_risky_cell(self, shade):
        """Клетка «рискованная», если её ловушка заметно выше средней."""
        darkness = 1.0 - shade
        trap_mult = TRAP_LIGHT_MULT + (TRAP_DARK_MULT - TRAP_LIGHT_MULT) * darkness
        return trap_mult >= RISK_HINT_MULT * self.avg_trap_mult()



    def make_cell_item(self, shade):
        darkness = 1.0 - shade
        trap_mult = TRAP_LIGHT_MULT + (TRAP_DARK_MULT
                                       - TRAP_LIGHT_MULT) * darkness
        find_mult = BANDAGE_LIGHT_MULT + (BANDAGE_DARK_MULT
                                          - BANDAGE_LIGHT_MULT) * darkness
        grow = self.trap_growth()
        p_stone = P_STONE_BASE * trap_mult * grow
        p_plant = P_PLANT_BASE * trap_mult * grow
        p_animal = P_ANIMAL_BASE * trap_mult * grow
        p_bandage = P_BANDAGE_BASE * find_mult
        p_antidote = P_ANTIDOTE_BASE * find_mult

        roll = random.random()
        if roll < p_stone:
            return "stone"
        if roll < p_stone + p_plant:
            return "plant"
        if roll < p_stone + p_plant + p_animal:
            return "animal"
        if roll < p_stone + p_plant + p_animal + p_bandage:
            return "bandage"
        if roll < (p_stone + p_plant + p_animal + p_bandage + p_antidote):
            return "antidote"
        # редкие находки: независимый бросок, ловушкам не мешают
        rare_roll = random.random()
        if rare_roll < P_COMPASS:
            return "compass"
        if rare_roll < P_COMPASS + P_MAGNET:
            return "magnet"
        if rare_roll < P_COMPASS + P_MAGNET + P_CLOVER:
            return "clover"
        return None



    def build_field(self):
        w, h = self.screen.get_size()
        cell = self.cell_size()
        self.field_rect = pygame.Rect(0, 0, w, h - HUD_H)
        self.cols = max(1, int(self.field_rect.w // cell))
        self.rows = max(1, int(self.field_rect.h // cell))
        self.cw = self.field_rect.w / self.cols
        self.ch = self.field_rect.h / self.rows
        n = self.cols * self.rows
        self.cells = []
        for _ in range(n):
            shade = random.random() ** SHADE_POWER
            strokes = []
            for _ in range(3):
                dx1 = random.random() * max(1, self.cw - 6)
                dy1 = random.random() * max(1, self.ch - 6)
                dx2 = min(max(dx1 + random.uniform(-9, 9), 0), self.cw - 3)
                dy2 = min(max(dy1 + random.uniform(-9, 9), 0), self.ch - 3)
                strokes.append((dx1, dy1, dx2, dy2))
            self.cells.append({"hay": True, "dug": False,
                               "shade": shade, "strokes": strokes,
                               "price": self.cell_price(shade),
                               "item": self.make_cell_item(shade)})
        self.needle_idx = random.randrange(n)
        self.cells[self.needle_idx]["item"] = None
        self.golden_needle = (random.randrange(GOLD_NEEDLE_ONE_IN) == 0)
        self.compass_hint = None
        self.compass_quadrant = None
        self.field_dirty = True



    def restart(self):
        for c in self.cells:
            c["hay"] = True
            c["dug"] = False
        self.needle_idx = random.randrange(len(self.cells))
        self.cells[self.needle_idx]["item"] = None
        self.golden_needle = (random.randrange(GOLD_NEEDLE_ONE_IN) == 0)
        self.compass_hint = None
        self.compass_quadrant = None
        self.won = False
        self.dead = False
        self.needle_found = False
        self.digs = 0
        self.stamina = self.max_stamina
        self.poison_time = 0.0
        self.bite_flash = 0.0
        self.poison_flash = 0.0
        self.straws = []
        self.field_dirty = True



    def next_level(self):
        if not self.needle_found:
            return
        reward = LEVEL_REWARD_BASE * self.level  # за только что пройденный
        endless = self.level >= MAX_LEVEL
        self.level += 1
        self.needle_found = False
        self.won = False
        self.digs = 0
        self.stamina = self.max_stamina
        self.health = self.max_health
        self.poison_time = 0.0
        self.bite_flash = 0.0
        self.poison_flash = 0.0
        self.build_field()
        self.mercy_used = False   # милость судьбы доступна снова
        self.money += reward
        self.add_message("Награда за уровень: +%d монет" % reward, GREEN_MSG)
        if endless:
            self.add_message("Бесконечный стог: уровень %d! Ловушки "
                             "злее, бонус за иглу растёт" % self.level,
                             BLUE_MSG)
        else:
            self.add_message("Уровень %d! Клеток больше, ловушки злее"
                             % self.level, BLUE_MSG)

    # ---------- аптека ----------



    # ---------- кэш картинки стога ----------
    def make_field_surface(self):
        surf = pygame.Surface(self.field_rect.size).convert()
        surf.fill(DIRT)
        self.risk_cells = []
        icon_d = max(8, int(min(self.cw, self.ch) * 0.55))
        for i, c in enumerate(self.cells):
            x = (i % self.cols) * self.cw
            y = (i // self.cols) * self.ch
            if not c["dug"]:
                s = c["shade"]
                if self.is_risky_cell(s):
                    self.risk_cells.append(i)
                color = (int(184 + 56 * s), int(133 + 72 * s),
                         int(31 + 20 * s))
                pygame.draw.rect(surf, color,
                                 (x, y, self.cw - 1, self.ch - 1))
                for sx1, sy1, sx2, sy2 in c["strokes"]:
                    pygame.draw.line(surf, (235, 191, 64),
                                     (x + sx1, y + sy1),
                                     (x + sx2, y + sy2), 2)
            else:
                pygame.draw.rect(surf, (102, 77, 41),
                                 (x, y, self.cw - 1, self.ch - 1))
                if c["item"]:
                    pygame.draw.circle(
                        surf, (70, 52, 28),
                        (int(x + self.cw / 2), int(y + self.ch / 2)),
                        icon_d // 2 + 2)
                    cx, cy = x + self.cw / 2, y + self.ch / 2
                    if c["item"] == "stone":
                        self.draw_stone(surf, cx, cy, icon_d)
                    elif c["item"] == "plant":
                        self.draw_plant(surf, cx, cy, icon_d)
                    elif c["item"] == "animal":
                        self.draw_animal(surf, cx, cy, icon_d)
                    elif c["item"] == "bandage":
                        self.draw_bandage(surf, cx, cy, icon_d)
                    elif c["item"] == "antidote":
                        self.draw_antidote(surf, cx, cy, icon_d)
                    elif c["item"] == "compass":
                        self.draw_compass(surf, cx, cy, icon_d)
                    elif c["item"] == "magnet":
                        self.draw_magnet(surf, cx, cy, icon_d)
                    elif c["item"] == "clover":
                        self.draw_clover(surf, cx, cy, icon_d)

        if self.won:
            i = self.needle_idx
            nx = (i % self.cols) * self.cw + self.cw / 2
            ny = (i // self.cols) * self.ch + self.ch / 2
            needle_color = GOLD if self.golden_needle else SILVER
            pygame.draw.line(surf, needle_color,
                             (nx - 4, ny - self.ch * 0.4),
                             (nx + 4, ny + self.ch * 0.4), 4)
            pygame.draw.circle(surf, needle_color,
                               (int(nx - 4), int(ny + self.ch * 0.4)), 4)

        self.field_surf = surf
        self.field_dirty = False



    def draw_field(self):
        if self.field_surf is None or self.field_dirty:
            self.make_field_surface()
        self.screen.blit(self.field_surf, self.field_rect.topleft)
        self.draw_risk_pulse()
        self.draw_compass_highlight()
        self.draw_straws()
        self.draw_messages()
        self.draw_notice()
        self.draw_tutorial()
        self.draw_idle_hint()
        if self.won:
            self.draw_win_screen()
        elif self.dead:
            self.draw_death_screen()

    def draw_compass_highlight(self):
        """Золотая пульсирующая подсветка четверти стога с иглой."""
        if not self.compass_quadrant or self.won or self.dead:
            return
        north, west = self.compass_quadrant
        qw = self.field_rect.w / 2
        qh = self.field_rect.h / 2
        x0 = self.field_rect.x + (0 if west else qw)
        y0 = self.field_rect.y + (0 if north else qh)
        p = 0.55 + 0.45 * math.sin(self.time * 5.0)
        ov = pygame.Surface((max(1, int(qw)), max(1, int(qh))),
                            pygame.SRCALPHA)
        ov.fill((255, 200, 60, int(60 * p)))
        self.screen.blit(ov, (int(x0), int(y0)))
        pygame.draw.rect(self.screen, GOLD,
                         (int(x0), int(y0), int(qw), int(qh)),
                         max(3, int(2 + 4 * p)), border_radius=12)

    def draw_risk_pulse(self):
        """Слабое красное мерцание самых тёмных клеток, пока они не
        раскопаны (исчезает сразу после клика, даже если поле ещё
        не перерисовано)."""
        if (not getattr(self, "risk_cells", None) or self.won or self.dead):
            return
        p = 0.5 + 0.5 * math.sin(self.time * RISK_PULSE_SPEED)
        alpha = int(RISK_PULSE_MIN_ALPHA
                    + (RISK_PULSE_MAX_ALPHA - RISK_PULSE_MIN_ALPHA) * p)
        tw = max(1, int(self.cw))
        th = max(1, int(self.ch))
        tile = pygame.Surface((tw, th), pygame.SRCALPHA)
        pygame.draw.rect(tile, (200, 30, 30, alpha), tile.get_rect(),
                         border_radius=max(2, tw // 4))
        ox, oy = self.field_rect.topleft
        for i in self.risk_cells:
            if self.cells[i]["dug"]:
                continue
            x = int(ox + (i % self.cols) * self.cw)
            y = int(oy + (i // self.cols) * self.ch)
            self.screen.blit(tile, (x, y))
