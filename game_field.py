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
        return 1.0 + 0.25 * self.price_lvl



    def cell_price(self, shade):
        return int(round(self.cell_base_price(shade) * self.price_mult()))



    def make_cell_item(self, shade):
        darkness = 1.0 - shade
        trap_mult = TRAP_LIGHT_MULT + (TRAP_DARK_MULT
                                       - TRAP_LIGHT_MULT) * darkness
        find_mult = BANDAGE_LIGHT_MULT + (BANDAGE_DARK_MULT
                                          - BANDAGE_LIGHT_MULT) * darkness
        p_stone = P_STONE_BASE * trap_mult
        p_plant = P_PLANT_BASE * trap_mult
        p_animal = P_ANIMAL_BASE * trap_mult
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
        self.field_dirty = True



    def restart(self):
        for c in self.cells:
            c["hay"] = True
            c["dug"] = False
        self.needle_idx = random.randrange(len(self.cells))
        self.cells[self.needle_idx]["item"] = None
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
        if self.level < MAX_LEVEL and self.needle_found:
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
            self.add_message("Уровень %d! Клеток больше, ловушки злее"
                             % self.level, BLUE_MSG)

    # ---------- аптека ----------



    # ---------- кэш картинки стога ----------
    def make_field_surface(self):
        surf = pygame.Surface(self.field_rect.size).convert()
        surf.fill(DIRT)
        icon_d = max(8, int(min(self.cw, self.ch) * 0.55))
        for i, c in enumerate(self.cells):
            x = (i % self.cols) * self.cw
            y = (i // self.cols) * self.ch
            if not c["dug"]:
                s = c["shade"]
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
                    else:
                        self.draw_antidote(surf, cx, cy, icon_d)

        if self.won:
            i = self.needle_idx
            nx = (i % self.cols) * self.cw + self.cw / 2
            ny = (i // self.cols) * self.ch + self.ch / 2
            pygame.draw.line(surf, SILVER,
                             (nx - 4, ny - self.ch * 0.4),
                             (nx + 4, ny + self.ch * 0.4), 4)

        self.field_surf = surf
        self.field_dirty = False



    def draw_field(self):
        if self.field_surf is None or self.field_dirty:
            self.make_field_surface()
        self.screen.blit(self.field_surf, self.field_rect.topleft)
        self.draw_straws()
        self.draw_messages()
        self.draw_notice()
        if self.won:
            self.draw_win_screen()
        elif self.dead:
            self.draw_death_screen()

    # ---------- описания веток лавки (с цифрами или без) ----------
