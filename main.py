# -*- coding: utf-8 -*-
"""Игла «Игла в стоге сена» — единый файл.
Все модули проекта вшиты как исходный текст и загружаются
каждый в своём пространстве имён: перекрёстные импорты
работают без правок кода. Запуск: python igla_v_stoge_one.py
"""
import sys

try:
    import pygame
except ImportError:
    print("Сначала установите pygame: pip install pygame")
    sys.exit(1)

import types

def _load_module(name, source):
    module = types.ModuleType(name)
    sys.modules[name] = module
    exec(compile(source, name + ".py", "exec"), module.__dict__)
    return module

GAME_CONFIG_SOURCE = r'''
# -*- coding: utf-8 -*-
# Игра "Игла в стоге сена" на pygame.
# Справка по игре — кнопка «?» в панели внизу, всплывает как лавка.

import sys

try:
    import pygame
except ImportError:
    print("Сначала установите pygame: pip install pygame")
    sys.exit(1)

# ---------- настройки ----------
STAMINA_BASE = 20
STAMINA_STEP = 4
REGEN_BASE = 1.2
REGEN_STEP = 1.0
MAX_LEVEL = 10
NEEDLE_BONUS_BASE = 300
SHOP_H = 970           # высота лавки: 6 панелей + шапка
HELP_H = 1600   # высота справки: новые разделы
SLIDE_SPEED = 4.0
SHOP_PANEL_H = 120
SHOP_GAP = 10
SHOP_TOP = 140

# анимация копания: разлетающиеся соломинки
STRAW_MIN = 3
STRAW_MAX = 6
STRAW_LIFE = 0.7
STRAW_SPEED = 190
STRAW_GRAVITY = 260

# здоровье и укусы
HEALTH_BASE = 100
HEALTH_STEP = 10
ANIMAL_DAMAGE_BASE = 10
ANIMAL_DAMAGE_STEP = 6
BANDAGE_HEAL = 25
# здоровье само НЕ восстанавливается — только бинты

# отравление
POISON_RATE_BASE = 0.5
POISON_RATE_STEP = 0.4
POISON_DUR_BASE = 45.0
POISON_DUR_STEP = 6.0

# аптека
BANDAGE_CAP_BASE = 2
BANDAGE_CAP_STEP = 2
ANTIDOTE_CAP_BASE = 1
ANTIDOTE_CAP_STEP = 1

# размер клетки: чем дальше уровень, тем мельче (клеток всё больше)
CELL_START = 44
CELL_MIN = 12
CELL_STEP = 4

# цены сена по цвету клетки: жёлтое — 1 монета, коричневое — 5
PRICE_TIERS = ((0.75, 1), (0.5, 2), (0.3, 3), (0.0, 5))

# ---------- баланс ловушек и находок ----------
P_STONE_BASE = 0.003
P_PLANT_BASE = 0.012
P_ANIMAL_BASE = 0.012
P_BANDAGE_BASE = 0.020
P_ANTIDOTE_BASE = 0.012
TRAP_LIGHT_MULT = 0.5
TRAP_DARK_MULT = 2.5
BANDAGE_LIGHT_MULT = 1.6
BANDAGE_DARK_MULT = 0.2
SHADE_POWER = 1.6

STONE_PENALTY = 1
STONE_IMMUNE_LVL = 4     # с этой лопаты камень не откатывает уровень
STONE_MONEY_PENALTY = 10 # на максимальной лопате камень бьёт по кошельку

# приоритет находок за один рывок: чем меньше число, тем «хуже»
ITEM_PRIORITY = {"stone": 0, "animal": 1, "plant": 2,
                 "bandage": 3, "antidote": 4,
                 "compass": 5, "magnet": 5, "clover": 5}
RARE_ITEMS = ("compass", "magnet", "clover")

# ---------- редкие находки ----------
P_COMPASS = 0.004
P_MAGNET = 0.003
P_CLOVER = 0.004
CLOVER_TIME = 30.0         # сколько секунд действует клевер
CLOVER_SAVE_CHANCE = 0.35  # шанс спастись от сработавшей ловушки
MAGNET_MULT = 2            # во сколько раз больше следующий рывок

# ---------- золотая игла ----------
GOLD_NEEDLE_ONE_IN = 15    # каждый N-й стог
GOLD_NEEDLE_BONUS_MULT = 5

# ---------- серии рывков ----------
STREAK_GOAL = 10
STREAK_BONUS_BASE = 50     # x уровень монет за каждые 10 чистых рывков

# ---------- бесконечный стог ----------
ENDLESS_TRAP_GROWTH = 0.05  # +5% ловушек за уровень после MAX_LEVEL
ENDLESS_BONUS_MULT = 1.25   # бонус за иглу растёт в степенной прогрессии

# ---------- смерть ----------
DEATH_MONEY_KEEP = 0.5      # после смерти остаётся 50% монет

# ---------- удержание игрока ----------
LEVEL_REWARD_BASE = 15      # монет за пройденный уровень: 15 x уровень
LOW_HEALTH_FREE = 30        # при здоровье ниже — «милость судьбы»
RISK_HINT_MULT = 2.2        # клетки с ловушкой во столько раз выше средней


NOTICE_TIME = 2.2
IDLE_HINT_AFTER = 6.0       # сек бездействия до подсказки

# экранные вспышки: укус — красный, отравление — фиолетовый
BITE_FLASH_ALPHA = 185
POISON_FLASH_ALPHA = 185
POISON_TINT_ALPHA = 60
FLASH_FADE = 0.85

# цвета (R, G, B)
DIRT = (85, 60, 33)
HUD_BG = (40, 30, 18)
HUD_H = 260
PANEL_BG = (62, 46, 26)
PANEL_EDGE = (110, 82, 40)
SHOP_BG = (30, 22, 12)
TEXT = (255, 245, 220)
BTN = (150, 100, 40)
BTN_HOVER = (180, 130, 60)
BTN_DISABLED = (90, 70, 45)
BTN_OK = (70, 130, 60)
BTN_OK_HOVER = (95, 160, 80)
BTN_NEXT = (90, 110, 170)
BTN_NEXT_HOVER = (120, 145, 205)
GOLD = (255, 200, 60)
SILVER = (230, 235, 240)
RED = (235, 90, 90)
HEALTH_RED = (220, 55, 55)
STAMINA_BLUE = (70, 120, 235)
POISON_PURPLE = (170, 80, 220)
BITE_RED = (200, 30, 30)
POISON_FLASH = (140, 40, 200)
GREEN_MSG = (140, 230, 140)
BLUE_MSG = (150, 190, 255)
PURPLE_MSG = (210, 150, 240)
MSG_BG = (15, 10, 6)
STONE_GRAY = (150, 150, 155)
PLANT_GREEN = (90, 170, 80)
PLANT_FLOWER = (200, 90, 190)
ANIMAL_BROWN = (110, 70, 40)
ICON_SHOVEL_WOOD = (146, 100, 48)
ICON_SHOVEL_WOOD_DARK = (108, 72, 32)
ICON_SHOVEL_METAL = (176, 182, 192)
ICON_SHOVEL_METAL_DARK = (90, 92, 100)
ICON_SHOVEL_SHINE = (224, 228, 236)
ICON_BATTERY = (90, 200, 110)
ICON_BOLT = (255, 210, 70)
ICON_HAY = (235, 190, 60)
ICON_HEART = (230, 70, 80)
ICON_COIN = (255, 200, 60)
ICON_COIN_DARK = (190, 140, 30)
ANTIDOTE_GLASS = (215, 235, 225)
ANTIDOTE_LIQUID = (80, 190, 110)
ANTIDOTE_CORK = (170, 120, 60)
'''

GAME_FIELD_SOURCE = r'''
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
        return (1.0 + 0.25 * self.price_lvl) * (1.0 + 0.1 * (self.level - 1))



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
        self.free_bandage_used = False
        self.stamina = self.max_stamina
        self.poison_time = 0.0
        self.bite_flash = 0.0
        self.poison_flash = 0.0
        self.straws = []
        self.field_dirty = True



    def next_level(self):
        if not self.needle_found:
            return
        endless = self.level >= MAX_LEVEL
        reward = LEVEL_REWARD_BASE * self.level
        self.money += reward
        self.free_bandage_used = False
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
        if endless:
            self.add_message("Бесконечный стог: уровень %d! Ловушки "
                             "злее, бонус за иглу растёт" % self.level,
                             BLUE_MSG)
        else:
            self.add_message("Уровень %d! Клеток больше, ловушки злее"
                             % self.level, BLUE_MSG)
        self.add_message("Уровень пройден! +%d монет" % reward, GOLD)

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
        self.draw_risk_flicker()
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


    def draw_risk_flicker(self):
        """Слабое красное мерцание самых тёмных клеток — там чаще ловушки."""
        if self.won or self.dead:
            return
        risky = []
        for i, c in enumerate(self.cells):
            if c["dug"]:
                continue
            trap_mult = TRAP_LIGHT_MULT + (TRAP_DARK_MULT
                                           - TRAP_LIGHT_MULT) * (1.0 - c["shade"])
            if trap_mult >= RISK_HINT_MULT:
                risky.append(i)
        if not risky:
            return
        p = 0.5 + 0.5 * math.sin(self.time * 4.0)
        cw = max(1, int(self.cw) - 1)
        ch = max(1, int(self.ch) - 1)
        ov = pygame.Surface((cw, ch), pygame.SRCALPHA)
        ov.fill((235, 60, 60, int(16 + 20 * p)))
        for i in risky:
            x = self.field_rect.x + (i % self.cols) * self.cw
            y = self.field_rect.y + (i // self.cols) * self.ch
            self.screen.blit(ov, (int(x), int(y)))
'''

GAME_HEALTH_SOURCE = r'''
# -*- coding: utf-8 -*-
# Здоровье: укусы, отравление, бинты и противоядия

import math
import random
import pygame

from game_config import *


class HealthMixin:
    """Здоровье: укусы, отравление, бинты и противоядия"""


    # ---------- аптека ----------
    def bandage_cap(self):
        return BANDAGE_CAP_BASE + BANDAGE_CAP_STEP * self.bnd_lvl



    def antidote_cap(self):
        return ANTIDOTE_CAP_BASE + ANTIDOTE_CAP_STEP * self.bnd_lvl



    def animal_damage(self):
        return ANIMAL_DAMAGE_BASE + ANIMAL_DAMAGE_STEP * self.level



    def poison_rate(self):
        return POISON_RATE_BASE + POISON_RATE_STEP * self.level



    def poison_duration(self):
        """Длительность яда растёт с уровнем без потолка."""
        return POISON_DUR_BASE + POISON_DUR_STEP * self.level



    def use_bandage(self):
        if self.bandages <= 0:
            self.add_message("Бинтов нет — ищите в стоге", RED)
            return
        if self.health >= self.max_health:
            self.add_message("Здоровье полное — бинт не нужен", GREEN_MSG)
            return
        self.bandages -= 1
        self.health = min(self.max_health, self.health + BANDAGE_HEAL)
        self.add_message("Бинт использован", GREEN_MSG)
        self.tut_bandage_done = True
        if self.tutorial and self.tutorial.get("item") == "bandage":
            self.tutorial = None
        self.save_game()



    def use_antidote(self):
        if self.antidotes <= 0:
            self.add_message("Противоядий нет — ищите в стоге", RED)
            return
        if self.poison_time <= 0:
            self.add_message("Вы не отравлены — противоядие не нужно",
                             GREEN_MSG)
            return
        self.antidotes -= 1
        self.poison_time = 0.0
        self.add_message("Противоядие выпито — отравление снято!",
                         GREEN_MSG)
        self.tut_antidote_done = True
        if self.tutorial and self.tutorial.get("item") == "antidote":
            self.tutorial = None
        self.save_game()


    def maybe_free_bandage(self):
        """Милость судьбы: раз за уровень бесплатный бинт при низком здоровье."""
        if getattr(self, "free_bandage_used", False):
            return
        if self.health <= 0 or self.health > LOW_HEALTH_FREE:
            return
        if self.bandages > 0:
            return
        self.free_bandage_used = True
        self.bandages = 1
        self.add_message("Милость судьбы: в соломе нашёлся бинт!",
                         GREEN_MSG)
'''

GAME_EFFECTS_SOURCE = r'''
# -*- coding: utf-8 -*-
# Эффекты: сообщения, таблички находок, вспышки, соломинки

import math
import random
import pygame

from game_config import *


class EffectsMixin:
    """Эффекты: сообщения, таблички находок, вспышки, соломинки"""


    # ---------- сообщения и таблички ----------
    def add_message(self, text, color):
        self.messages.append({"text": text, "color": color, "life": 2.6})



    def show_notice(self, item):
        titles = {
            "stone": "КАМЕНЬ!",
            "plant": "ЯДОВИТОЕ РАСТЕНИЕ!",
            "animal": "УКУС ЗВЕРЯ!",
            "bandage": "БИНТ!",
            "antidote": "ПРОТИВОЯДИЕ!",
            "compass": "КОМПАС!",
            "magnet": "МАГНИТ!",
            "clover": "КЛЕВЕР!",
        }
        self.notice = {"item": item, "title": titles.get(item, item),
                       "sub": "", "life": NOTICE_TIME}



    def draw_notice(self):
        n = self.notice
        if not n:
            return
        alpha = max(0, min(255, int(255 * min(1.0, n["life"] / 0.5))))
        w, h = self.screen.get_size()
        pw, ph = 460, 260
        px = (w - pw) // 2
        py = self.field_rect.top + (self.field_rect.h - ph) // 2 - 40

        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (25, 18, 10, int(235 * alpha / 255)),
                         (0, 0, pw, ph), border_radius=18)
        pygame.draw.rect(panel, (255, 210, 80, int(200 * alpha / 255)),
                         (0, 0, pw, ph), 4, border_radius=18)
        self.screen.blit(panel, (px, py))

        icon_cx = px + pw // 2
        icon_cy = py + 92
        if n["item"] == "stone":
            self.draw_stone(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "plant":
            self.draw_plant(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "animal":
            self.draw_animal(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "bandage":
            self.draw_bandage(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "antidote":
            self.draw_antidote(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "compass":
            self.draw_compass(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "magnet":
            self.draw_magnet(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "clover":
            self.draw_clover(self.screen, icon_cx, icon_cy, 110, alpha)

        color = GREEN_MSG if n["item"] in ("bandage", "antidote",
                                           "compass", "magnet",
                                           "clover") else RED
        t1 = self.font_big.render(n["title"], True, color)
        t1.set_alpha(alpha)
        self.screen.blit(t1, t1.get_rect(center=(w // 2, py + 178)))
        if n["sub"]:
            t2 = self.font_mid.render(n["sub"], True, TEXT)
            t2.set_alpha(alpha)
            self.screen.blit(t2, t2.get_rect(center=(w // 2, py + 226)))



    def draw_messages(self):
        """Сообщения на тёмной плашке — читаются на любом фоне стога."""
        y = self.field_rect.top + 14
        for m in self.messages:
            alpha = max(0, min(255, int(255 * m["life"] / 1.2)))
            surf = self.font_mid.render(m["text"], True, m["color"])
            pad = 10
            pill_w = surf.get_width() + pad * 2
            pill_h = surf.get_height() + pad * 2
            pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pygame.draw.rect(pill, MSG_BG + (int(215 * alpha / 255),),
                             (0, 0, pill_w, pill_h), border_radius=10)
            px = self.field_rect.centerx - pill_w // 2
            self.screen.blit(pill, (px, y))
            surf.set_alpha(alpha)
            self.screen.blit(surf, (px + pad, y + pad))
            y += pill_h + 4

    # ---------- экранные вспышки ----------



    # ---------- экранные вспышки ----------
    def draw_screen_effects(self):
        w, h = self.screen.get_size()
        if self.bite_flash > 0:
            alpha = int(BITE_FLASH_ALPHA * self.bite_flash)
            if alpha > 0:
                ov = pygame.Surface((w, h), pygame.SRCALPHA)
                ov.fill(BITE_RED + (alpha,))
                self.screen.blit(ov, (0, 0))
        if self.poison_flash > 0:
            alpha = int(POISON_FLASH_ALPHA * self.poison_flash)
            if alpha > 0:
                ov = pygame.Surface((w, h), pygame.SRCALPHA)
                ov.fill(POISON_FLASH + (alpha,))
                self.screen.blit(ov, (0, 0))
        elif self.poison_time > 0:
            ov = pygame.Surface((w, h), pygame.SRCALPHA)
            ov.fill(POISON_FLASH + (POISON_TINT_ALPHA,))
            self.screen.blit(ov, (0, 0))



    def update_flashes(self, dt):
        if self.bite_flash > 0:
            self.bite_flash = max(0.0, self.bite_flash - FLASH_FADE * dt)
        if self.poison_flash > 0:
            self.poison_flash = max(0.0, self.poison_flash - FLASH_FADE * dt)

    # ---------- соломинки от копания ----------



    # ---------- соломинки от копания ----------
    def spawn_straws(self, cell_indices):
        for i in cell_indices:
            x = self.field_rect.x + (i % self.cols) * self.cw + self.cw / 2
            y = self.field_rect.y + (i // self.cols) * self.ch + self.ch / 2
            count = random.randint(STRAW_MIN, STRAW_MAX)
            for _ in range(count):
                ang = random.uniform(0, 2 * math.pi)
                speed = STRAW_SPEED * random.uniform(0.4, 1.2)
                self.straws.append({
                    "x": x + random.uniform(-self.cw / 3, self.cw / 3),
                    "y": y + random.uniform(-self.ch / 3, self.ch / 3),
                    "vx": math.cos(ang) * speed,
                    "vy": math.sin(ang) * speed - 70,
                    "ang": random.uniform(0, math.pi),
                    "spin": random.uniform(-9, 9),
                    "len": random.uniform(0.4, 0.8) * min(self.cw, self.ch),
                    "life": STRAW_LIFE * random.uniform(0.7, 1.2),
                    "color": random.choice([(235, 191, 64), (250, 214, 96),
                                            (210, 165, 50)]),
                })



    def update_straws(self, dt):
        alive = []
        for s in self.straws:
            s["life"] -= dt
            if s["life"] <= 0:
                continue
            s["vy"] += STRAW_GRAVITY * dt
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            s["ang"] += s["spin"] * dt
            alive.append(s)
        self.straws = alive



    def draw_straws(self):
        for s in self.straws:
            alpha = max(0, min(255,
                               int(255 * s["life"] / (STRAW_LIFE * 0.6))))
            half = s["len"] / 2
            dx = math.cos(s["ang"]) * half
            dy = math.sin(s["ang"]) * half
            color = s["color"]
            if alpha < 255:
                surf = pygame.Surface(
                    (int(abs(dx) * 2) + 4, int(abs(dy) * 2) + 4),
                    pygame.SRCALPHA)
                cxx = surf.get_width() // 2
                cyy = surf.get_height() // 2
                pygame.draw.line(surf, color,
                                 (cxx - dx, cyy - dy), (cxx + dx, cyy + dy), 3)
                surf.set_alpha(alpha)
                self.screen.blit(surf,
                                 (int(s["x"] - cxx), int(s["y"] - cyy)))
            else:
                pygame.draw.line(self.screen, color,
                                 (s["x"] - dx, s["y"] - dy),
                                 (s["x"] + dx, s["y"] + dy), 3)

    # ---------- экономика ----------
'''

GAME_ECONOMY_SOURCE = r'''
# -*- coding: utf-8 -*-
# Экономика: цены улучшений, продажа сена, покупки

import math
import random
import pygame

from game_config import *


class EconomyMixin:
    """Экономика: цены улучшений, продажа сена, покупки"""


    # ---------- экономика ----------
    def dig_side(self):
        return min(7, 1 + (self.shovel - 1) // 2)



    def regen_rate(self):
        return REGEN_BASE + REGEN_STEP * self.regen_lvl



    def needle_bonus(self):
        bonus = NEEDLE_BONUS_BASE * self.level
        if self.level > MAX_LEVEL:
            bonus *= ENDLESS_BONUS_MULT ** (self.level - MAX_LEVEL)
        if getattr(self, "golden_needle", False):
            bonus *= GOLD_NEEDLE_BONUS_MULT
        return int(bonus)

    # --- цены улучшений ---


    def shovel_cost(self):
        return int(40 * 1.9 ** (self.shovel - 1))



    def cap_cost(self):
        return int(100 * 1.6 ** self.cap_lvl)



    def regen_cost(self):
        return int(80 * 1.6 ** self.regen_lvl)



    def price_cost(self):
        return int(400 * 2.0 ** self.price_lvl)



    def health_cost(self):
        return int(150 * 1.7 ** self.health_lvl)



    def bnd_cost(self):
        return int(250 * 1.7 ** self.bnd_lvl)



    def sell(self):
        if self.hay > 0:
            self.money += self.hay_value
            self.hay = 0
            self.hay_value = 0
            self.save_game()



    def buy(self, kind):
        bought = False
        if kind == "shovel":
            cost = self.shovel_cost()
            if self.money >= cost:
                self.money -= cost
                self.shovel += 1
                bought = True
        elif kind == "cap":
            cost = self.cap_cost()
            if self.money >= cost:
                self.money -= cost
                self.cap_lvl += 1
                self.max_stamina += STAMINA_STEP
                self.stamina += STAMINA_STEP
                bought = True
        elif kind == "regen":
            cost = self.regen_cost()
            if self.money >= cost:
                self.money -= cost
                self.regen_lvl += 1
                bought = True
        elif kind == "price":
            cost = self.price_cost()
            if self.money >= cost:
                self.money -= cost
                self.price_lvl += 1
                bought = True
        elif kind == "health":
            cost = self.health_cost()
            if self.money >= cost:
                self.money -= cost
                self.health_lvl += 1
                self.max_health += HEALTH_STEP
                self.health += HEALTH_STEP
                bought = True
        elif kind == "bnd":
            cost = self.bnd_cost()
            if self.money >= cost:
                self.money -= cost
                self.bnd_lvl += 1
                bought = True
        if bought:
            self.shop_surf = None
            self.save_game()

    # ---------- геометрия интерфейса ----------



    # ---------- описания веток лавки ----------
    def shop_item_info(self, key):
        if key == "shovel":
            return "ЛОПАТА", "Копает больше клеток за рывок"
        if key == "cap":
            return "ЗАПАС СИЛ", "Больше сил на рывки"
        if key == "regen":
            return "СКОРОСТЬ СИЛ", "Силы восстанавливаются быстрее"
        if key == "price":
            return "ЦЕНА СЕНА", "Сено продается дороже"
        if key == "health":
            return "ЗДОРОВЬЕ", "Больше запас здоровья"
        if key == "bnd":
            return "АПТЕЧКА", ("Бинтов: %d/%d   Противоядий: %d/%d"
                               % (self.bandages, self.bandage_cap(),
                                  self.antidotes, self.antidote_cap()))
        return "", ""
'''

GAME_UI_SOURCE = r'''
# -*- coding: utf-8 -*-
# Интерфейс: HUD, кнопки, полосы здоровья и сил, монеты,
# крутящиеся значки бонусов, обучение и подсказка простоя

import math
import random
import pygame

from game_config import *


class UIMixin:
    """Интерфейс: HUD, кнопки, полосы, значки бонусов, подсказки"""


    # ---------- геометрия интерфейса ----------
    def build_ui(self):
        w, h = self.screen.get_size()
        hud_top = h - HUD_H
        bw = (w - 32) // 3
        self.main_buttons = {
            "sell": pygame.Rect(8, hud_top + 196, bw, 60),
            "shop": pygame.Rect(bw + 16, hud_top + 196, bw, 60),
            "next": pygame.Rect(2 * bw + 24, hud_top + 196, bw, 60),
        }
        self.bandage_btn = pygame.Rect(w - 134, hud_top + 98, 92, 56)
        self.antidote_btn = pygame.Rect(w - 234, hud_top + 98, 92, 56)
        self.help_button = pygame.Rect(w - 300, hud_top + 96, 58, 58)
        self.pause_button = pygame.Rect(w - 370, hud_top + 96, 58, 58)

        self.shop_panel_h = min(SHOP_H, h)
        self.shop_panels = []
        self.shop_buttons = {}
        keys = ("shovel", "cap", "regen", "price", "health", "bnd")
        for i, key in enumerate(keys):
            panel = pygame.Rect(12, SHOP_TOP + i * (SHOP_PANEL_H + SHOP_GAP),
                                w - 24, SHOP_PANEL_H)
            if panel.bottom > self.shop_panel_h - 84:
                break
            self.shop_panels.append((key, panel))
            self.shop_buttons["buy_" + key] = pygame.Rect(
                panel.right - 210, panel.y + 34, 196, 52)
        self.shop_buttons["close"] = pygame.Rect(
            w // 2 - 180, self.shop_panel_h - 72, 360, 58)

        self.help_panel_h = min(HELP_H, h)
        self.help_surf = None



    def shop_offset(self):
        return int(self.shop_panel_h * self.shop_slide)



    def help_offset(self):
        return int(self.help_panel_h * self.help_slide)

    # ---------- вспомогательная отрисовка ----------



    def draw_button(self, rect, text, enabled=True, ok=False, next_btn=False):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        if not enabled:
            color = BTN_DISABLED
        elif next_btn:
            color = BTN_NEXT_HOVER if hovered else BTN_NEXT
        elif ok:
            color = BTN_OK_HOVER if hovered else BTN_OK
        elif hovered:
            color = BTN_HOVER
        else:
            color = BTN
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (30, 20, 10), rect, 2,
                         border_radius=10)
        label = self.txt(text, self.font_small)
        self.screen.blit(label, label.get_rect(center=rect.center))



    def draw_centered(self, text, font, y, color=TEXT):
        surf = self.txt(text, font, color)
        self.screen.blit(surf, surf.get_rect(
            center=(self.screen.get_width() // 2, y)))



    def draw_bar(self, bar, ratio, label_text="", pulse=False,
                 fixed_color=None):
        fill_w = int(bar.w * ratio)

        if fixed_color is not None:
            r, g, b = fixed_color
            if pulse and ratio < 0.15:
                p = 0.5 + 0.5 * math.sin(self.time * 8.0)
                factor = 0.55 + 0.45 * p
                r, g, b = int(r * factor), int(g * factor), int(b * factor)
        else:
            if ratio > 0.5:
                t = (1.0 - ratio) * 2.0
                r, g, b = int(80 + 175 * t), int(200 - 30 * t), 60
            else:
                t = ratio * 2.0
                r, g, b = 255, int(60 + 140 * t), 60
            if pulse and ratio < 0.15:
                p = 0.5 + 0.5 * math.sin(self.time * 8.0)
                r, g, b = (int(120 + (r - 120) * p),
                           int(30 + (g - 30) * p), 40)

        pygame.draw.rect(self.screen, (70, 55, 35), bar, border_radius=5)
        if fill_w > 0:
            fill = pygame.Rect(bar.x + 2, bar.y + 2,
                               max(4, fill_w - 4), bar.h - 4)
            pygame.draw.rect(self.screen, (r, g, b), fill,
                             border_radius=5)
            shine = pygame.Rect(fill.x, fill.y, fill.w, max(2, fill.h // 3))
            pygame.draw.rect(self.screen,
                             (min(255, r + 60), min(255, g + 50),
                              min(255, b + 40)), shine, border_radius=4)
        pygame.draw.rect(self.screen, (30, 20, 10), bar, 2,
                         border_radius=5)
        label = self.txt(label_text, self.font_small)
        self.screen.blit(label, label.get_rect(center=bar.center))



    def draw_coin(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        cn = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(cn, ICON_COIN_DARK, (r, r), r)
        pygame.draw.circle(cn, ICON_COIN, (r, r), r - max(1, d // 14))
        pygame.draw.circle(cn, (255, 235, 160),
                           (r - r // 3, r - r // 3), max(1, r // 4))
        if alpha is not None:
            cn.set_alpha(alpha)
        surf.blit(cn, (int(cx - r), int(cy - r)))



    def draw_pill_button(self, rect, kind, can_use, count_text):
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = BTN_OK_HOVER if (hovered and can_use) else (
            BTN_OK if can_use else BTN_DISABLED)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (30, 20, 10), rect, 2,
                         border_radius=10)
        icon_d = rect.h - 10
        draw = self.draw_bandage if kind == "bandage" else self.draw_antidote
        draw(self.screen, rect.x + icon_d // 2 + 5, rect.centery, icon_d)
        count = self.txt(count_text, self.font_small, TEXT)
        self.screen.blit(count,
                         (rect.x + icon_d + 8,
                          rect.centery - count.get_height() // 2))



    def draw_pill_icon(self, rect, kind):
        icon_d = rect.h - 10
        if kind == "bandage":
            self.draw_bandage(self.screen, rect.x + icon_d // 2 + 5,
                              rect.centery, icon_d)
        else:
            self.draw_antidote(self.screen, rect.x + icon_d // 2 + 5,
                               rect.centery, icon_d)

    # ---------- HUD ----------

    def draw_hud(self):
        w, h = self.screen.get_size()
        hud_top = h - HUD_H
        pygame.draw.rect(self.screen, HUD_BG, (0, hud_top, w, HUD_H))
        pygame.draw.rect(self.screen, PANEL_EDGE, (0, hud_top, w, 4))

        hud_text = ("Уровень: %d   Деньги: %d   Сено: %d пучков"
                    % (self.level, self.money, self.hay))
        self.screen.blit(self.txt(hud_text, self.font_small),
                         (10, hud_top + 10))

        self.draw_bar(pygame.Rect(10, hud_top + 38, w - 20, 24),
                      self.stamina / self.max_stamina, pulse=True,
                      fixed_color=STAMINA_BLUE, label_text="Силы")

        if self.poison_time > 0:
            health_label = "Здоровье: ОТРАВЛЕНИЕ!"
            color = POISON_PURPLE
        else:
            health_label = "Здоровье"
            color = HEALTH_RED
        self.draw_bar(pygame.Rect(10, hud_top + 70, w - 20, 24),
                      max(0.0, self.health) / self.max_health,
                      pulse=True, fixed_color=color,
                      label_text=health_label)

        self.draw_button(self.main_buttons["sell"],
                         "Продать сено (+%d)" % self.hay_value,
                         self.hay > 0)
        self.draw_button(self.main_buttons["shop"], "Лавка улучшений")

        if self.needle_found:
            self.draw_button(self.main_buttons["next"],
                             "Уровень %d ->" % (self.level + 1),
                             next_btn=True)
        else:
            self.draw_button(self.main_buttons["next"],
                             "Найдите иголку", enabled=False)

        # иконка бинтов: всегда видно, сколько из скольких
        self.draw_pill_button(
            self.bandage_btn, "bandage",
            self.bandages > 0 and self.health < self.max_health,
            "%d/%d" % (self.bandages, self.bandage_cap()))

        # иконка противоядия: всегда видно, сколько из скольких
        self.draw_pill_button(
            self.antidote_btn, "antidote",
            self.antidotes > 0 and self.poison_time > 0,
            "%d/%d" % (self.antidotes, self.antidote_cap()))

        self.draw_pause_button()

    # ---------- кнопка паузы ----------

    def draw_pause_button(self):
        rect = self.pause_button
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = BTN_HOVER if hovered else BTN
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (30, 20, 10), rect, 2,
                         border_radius=10)
        label = self.txt("II", self.font_small)
        self.screen.blit(label, label.get_rect(center=rect.center))

    # ---------- крутящиеся значки активных бонусов ----------

    def draw_bonus_icons(self):
        if self.won or self.dead:
            return
        icons = []
        if self.compass_quadrant:
            icons.append(("compass", None))
        if self.magnet_ready:
            icons.append(("magnet", None))
        if self.clover_time > 0:
            icons.append(("clover", self.clover_time / CLOVER_TIME))
        if not icons:
            return
        fr = self.field_rect
        d = 52
        for k, (name, frac) in enumerate(icons):
            cx = fr.right - 40 - k * (d + 12)
            cy = fr.bottom - 40
            ring = pygame.Surface((d + 16, d + 16), pygame.SRCALPHA)
            pygame.draw.circle(ring, (25, 18, 10, 205),
                               ((d + 16) // 2, (d + 16) // 2),
                               (d + 16) // 2)
            pygame.draw.circle(ring, (255, 200, 60, 235),
                               ((d + 16) // 2, (d + 16) // 2),
                               (d + 16) // 2, 3)
            self.screen.blit(ring, (int(cx - (d + 16) / 2),
                                    int(cy - (d + 16) / 2)))
            icon = self.icon_cache.get((name, d))
            if icon is None:
                icon = self.shop_icon(name, d)
            rot = pygame.transform.rotate(icon, -self.time * 90.0)
            self.screen.blit(rot, rot.get_rect(center=(int(cx), int(cy))))
            if frac is not None:
                rr = d // 2 + 7
                arc_rect = pygame.Rect(0, 0, 2 * rr, 2 * rr)
                arc_rect.center = (int(cx), int(cy))
                pygame.draw.arc(self.screen, (110, 230, 110), arc_rect,
                                math.pi / 2,
                                math.pi / 2 + 2 * math.pi * frac, 4)

    # ---------- обучение: подсветка бинта/противоядия ----------

    def draw_tutorial(self):
        if not self.tutorial or self.won or self.dead:
            return
        item = self.tutorial.get("item")
        rect = self.bandage_btn if item == "bandage" else self.antidote_btn
        p = 0.5 + 0.5 * math.sin(self.time * 6.0)
        grow = int(6 * p)
        pygame.draw.rect(self.screen, GOLD,
                         rect.inflate(grow * 2, grow * 2), 4,
                         border_radius=12)
        if item == "bandage":
            text = "Нажмите на бинт, чтобы вылечиться!"
        else:
            text = "Нажмите на противоядие, чтобы вылечиться!"
        surf = self.font_mid.render(text, True, GOLD)
        w = self.screen.get_width()
        y = self.field_rect.top + 110
        pill = pygame.Surface((surf.get_width() + 26,
                               surf.get_height() + 16), pygame.SRCALPHA)
        pygame.draw.rect(pill, MSG_BG + (230,), pill.get_rect(),
                         border_radius=12)
        self.screen.blit(pill, pill.get_rect(center=(w // 2, y)))
        self.screen.blit(surf, surf.get_rect(center=(w // 2, y)))
        arrow_y = rect.top - 30
        pygame.draw.polygon(self.screen, GOLD,
                            [(rect.centerx, rect.top - 6),
                             (rect.centerx - 11, arrow_y),
                             (rect.centerx + 11, arrow_y)])

    # ---------- подсказка простоя ----------

    def draw_idle_hint(self):
        hint = self.idle_hint
        if not hint or self.won or self.dead:
            return
        w = self.screen.get_width()
        surf = self.font_mid.render(hint["text"], True, GOLD)
        y = self.field_rect.top + 60
        pill = pygame.Surface((surf.get_width() + 26,
                               surf.get_height() + 16), pygame.SRCALPHA)
        pygame.draw.rect(pill, MSG_BG + (230,), pill.get_rect(),
                         border_radius=12)
        pygame.draw.rect(pill, GOLD + (230,), pill.get_rect(), 2,
                         border_radius=12)
        self.screen.blit(pill, pill.get_rect(center=(w // 2, y)))
        self.screen.blit(surf, surf.get_rect(center=(w // 2, y)))
        p = 0.5 + 0.5 * math.sin(self.time * 5.0)
        target = hint.get("target")
        if target is not None:
            grow = int(8 * p)
            pygame.draw.rect(self.screen, GOLD,
                             target.inflate(grow * 2, grow * 2), 4,
                             border_radius=10)
        cell = hint.get("cell")
        if cell is not None:
            x = self.field_rect.x + (cell % self.cols) * self.cw
            yy = self.field_rect.y + (cell // self.cols) * self.ch
            r = pygame.Rect(int(x), int(yy), int(self.cw), int(self.ch))
            pygame.draw.rect(self.screen, GOLD,
                             r.inflate(int(8 * p), int(8 * p)), 3,
                             border_radius=4)
'''

GAME_DRAWINGS_SOURCE = r'''
# -*- coding: utf-8 -*-
# Рисунки: находки и иконки лавки

import math
import random
import pygame

from game_config import *


class DrawingsMixin:
    """Рисунки: находки и иконки лавки"""


    # ---------- рисунки находок ----------
    def draw_stone(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        rock = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(rock, (60, 60, 66), (r, r + r // 6), r)
        pygame.draw.circle(rock, STONE_GRAY, (r, r - r // 10),
                           int(r * 0.88))
        pygame.draw.circle(rock, (185, 185, 190),
                           (r - r // 3, r - r // 3), int(r * 0.28))
        pygame.draw.arc(rock, (90, 90, 96), (r // 4, r // 4,
                                             d - r // 2, d - r // 2),
                        2.6, 4.6, max(2, r // 8))
        if alpha is not None:
            rock.set_alpha(alpha)
        surf.blit(rock, (int(cx - r), int(cy - r)))



    def draw_plant(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        pl = pygame.Surface((d, d), pygame.SRCALPHA)
        cxx, cyy = int(r), int(r)
        pygame.draw.line(pl, PLANT_GREEN,
                         (cxx, int(cyy + r * 0.9)), (cxx, int(cyy - r * 0.2)),
                         max(3, r // 6))
        pygame.draw.line(pl, PLANT_GREEN,
                         (cxx, int(cyy + r * 0.3)),
                         (int(cxx - r * 0.6), int(cyy + r * 0.05)),
                         max(3, r // 8))
        pygame.draw.line(pl, PLANT_GREEN,
                         (cxx, int(cyy + r * 0.5)),
                         (int(cxx + r * 0.6), int(cyy + r * 0.25)),
                         max(3, r // 8))
        for k in (-0.1, 0.2):
            pygame.draw.line(pl, PLANT_GREEN,
                             (cxx, int(cyy + r * k)),
                             (int(cxx - r * 0.18), int(cyy + r * (k - 0.12))),
                             max(2, r // 10))
        fr = int(r * 0.42)
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            fx = cxx + int(math.cos(rad) * fr)
            fy = cyy - int(r * 0.35) + int(math.sin(rad) * fr)
            pygame.draw.circle(pl, PLANT_FLOWER, (fx, fy), max(3, fr // 2))
        pygame.draw.circle(pl, (255, 220, 90),
                           (cxx, cyy - int(r * 0.35)), max(2, fr // 3))
        if alpha is not None:
            pl.set_alpha(alpha)
        surf.blit(pl, (int(cx - r), int(cy - r)))



    def draw_animal(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        an = pygame.Surface((d, d), pygame.SRCALPHA)
        cxx, cyy = int(r), int(r)
        pad_w, pad_h = int(r * 0.9), int(r * 0.7)
        pygame.draw.ellipse(an, ANIMAL_BROWN,
                            (cxx - pad_w // 2, cyy, pad_w, pad_h))
        toe_r = max(3, r // 5)
        for tx, ty in ((-0.55, -0.45), (0, -0.62), (0.55, -0.45)):
            pygame.draw.circle(an, ANIMAL_BROWN,
                               (int(cxx + tx * r), int(cyy + ty * r)), toe_r)
        for k in (-1, 0, 1):
            pygame.draw.line(an, (230, 70, 70),
                             (int(cxx + k * r * 0.5), int(cyy - r * 0.8)),
                             (int(cxx + k * r * 0.4), int(cyy + r * 0.9)),
                             max(2, r // 10))
        if alpha is not None:
            an.set_alpha(alpha)
        surf.blit(an, (int(cx - r), int(cy - r)))



    def draw_bandage(self, surf, cx, cy, d, alpha=None):
        """Рулон бинта: белый цилиндр, торец со спиралью,
        свисающий хвостик и красный крест."""
        r = d // 2
        bd = pygame.Surface((d, d), pygame.SRCALPHA)

        body_h = int(d * 0.56)
        body_w = int(d * 0.66)
        bx = int(d * 0.06)
        by = (d - body_h) // 2
        corner = max(3, body_h // 4)

        tail = pygame.Rect(bx + body_w - body_h // 3,
                           by + body_h - 4,
                           int(d * 0.30), int(d * 0.20))
        pygame.draw.rect(bd, (238, 235, 228), tail,
                         border_radius=max(3, d // 16))
        pygame.draw.rect(bd, (196, 192, 184), tail, max(2, d // 30),
                         border_radius=max(3, d // 16))

        body = pygame.Rect(bx, by, body_w, body_h)
        pygame.draw.rect(bd, (252, 250, 245), body, border_radius=corner)
        pygame.draw.rect(bd, (192, 188, 180), body, max(2, d // 26),
                         border_radius=corner)
        shade = pygame.Rect(bx + 4, by + body_h - max(3, d // 16),
                            body_w - 8, max(3, d // 16))
        pygame.draw.rect(bd, (226, 222, 214), shade,
                         border_radius=max(2, corner // 2))

        er = body_h // 2
        ecx = bx + er
        ecy = by + body_h // 2
        pygame.draw.circle(bd, (226, 222, 214), (ecx, ecy), er - 1)
        pygame.draw.circle(bd, (188, 184, 176), (ecx, ecy), er - 1,
                           max(2, d // 26))
        pygame.draw.circle(bd, (200, 196, 188), (ecx, ecy),
                           max(2, int(er * 0.62)), max(2, d // 30))
        pygame.draw.circle(bd, (200, 196, 188), (ecx, ecy),
                           max(2, int(er * 0.30)), max(2, d // 30))

        ccx = bx + int(body_w * 0.60)
        ccy = by + body_h // 2
        arm = max(3, d // 9)
        pygame.draw.rect(bd, (206, 58, 58),
                         (ccx - arm // 2, ccy - arm * 2, arm, arm * 4),
                         border_radius=arm // 3)
        pygame.draw.rect(bd, (206, 58, 58),
                         (ccx - arm * 2, ccy - arm // 2, arm * 4, arm),
                         border_radius=arm // 3)

        if alpha is not None:
            bd.set_alpha(alpha)
        surf.blit(bd, (int(cx - r), int(cy - r)))



    def draw_antidote(self, surf, cx, cy, d, alpha=None):
        """Флакон противоядия: стеклянная колба с зелёной жидкостью,
        пробка и белая этикетка с крестом."""
        r = d // 2
        ad = pygame.Surface((d, d), pygame.SRCALPHA)

        cork_w = int(d * 0.30)
        cork_h = int(d * 0.16)
        cork = pygame.Rect(int(d * 0.35), int(d * 0.06), cork_w, cork_h)
        pygame.draw.rect(ad, ANTIDOTE_CORK, cork,
                         border_radius=max(2, d // 14))
        pygame.draw.rect(ad, (130, 90, 42), cork, max(2, d // 30),
                         border_radius=max(2, d // 14))

        neck = pygame.Rect(int(d * 0.40), int(d * 0.20),
                           int(d * 0.20), int(d * 0.12))
        pygame.draw.rect(ad, ANTIDOTE_GLASS, neck)

        flask_r = int(d * 0.28)
        fcx, fcy = d // 2, int(d * 0.60)
        pygame.draw.circle(ad, ANTIDOTE_GLASS, (fcx, fcy), flask_r)
        pygame.draw.circle(ad, (150, 175, 165), (fcx, fcy), flask_r,
                           max(2, d // 26))
        liquid_r = int(flask_r * 0.78)
        pygame.draw.circle(ad, ANTIDOTE_LIQUID,
                           (fcx, fcy + int(d * 0.03)), liquid_r)
        pygame.draw.circle(ad, (245, 252, 248),
                           (fcx - liquid_r // 3, fcy - liquid_r // 3),
                           max(2, liquid_r // 4))

        lbl = pygame.Rect(fcx - int(d * 0.17), fcy - int(d * 0.10),
                          int(d * 0.34), int(d * 0.20))
        pygame.draw.rect(ad, (250, 248, 240), lbl,
                         border_radius=max(2, d // 20))
        arm = max(2, d // 16)
        pygame.draw.rect(ad, ANTIDOTE_LIQUID,
                         (lbl.centerx - arm // 2, lbl.centery - arm,
                          arm, arm * 2))
        pygame.draw.rect(ad, ANTIDOTE_LIQUID,
                         (lbl.centerx - arm, lbl.centery - arm // 2,
                          arm * 2, arm))

        if alpha is not None:
            ad.set_alpha(alpha)
        surf.blit(ad, (int(cx - r), int(cy - r)))

    # ---------- иконки лавки ----------



    # ---------- иконки лавки ----------
    def shop_icon(self, key, size=110):
        cache_key = (key, size)
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        s = size

        if key == "shovel":
            handle = pygame.Rect(int(s * 0.28), int(s * 0.07),
                                 int(s * 0.44), int(s * 0.09))
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD, handle,
                             border_radius=max(3, s // 20))
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD_DARK, handle,
                             max(2, s // 30), border_radius=max(3, s // 20))
            shaft = pygame.Rect(int(s * 0.47), int(s * 0.13),
                                int(s * 0.07), int(s * 0.37))
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD, shaft)
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD_DARK, shaft,
                             max(2, s // 30))
            pygame.draw.line(surf, (200, 150, 90),
                             (int(s * 0.485), int(s * 0.15)),
                             (int(s * 0.485), int(s * 0.47)),
                             max(2, s // 40))
            collar = pygame.Rect(int(s * 0.42), int(s * 0.48),
                                 int(s * 0.16), int(s * 0.08))
            pygame.draw.rect(surf, (112, 114, 124), collar,
                             border_radius=max(2, s // 30))
            blade_pts = [(int(s * 0.35), int(s * 0.55)),
                         (int(s * 0.65), int(s * 0.55)),
                         (int(s * 0.63), int(s * 0.80)),
                         (int(s * 0.50), int(s * 0.93)),
                         (int(s * 0.37), int(s * 0.80))]
            pygame.draw.polygon(surf, ICON_SHOVEL_METAL, blade_pts)
            pygame.draw.polygon(surf, ICON_SHOVEL_METAL_DARK, blade_pts,
                                max(2, s // 28))
            pygame.draw.line(surf, ICON_SHOVEL_SHINE,
                             (int(s * 0.41), int(s * 0.59)),
                             (int(s * 0.44), int(s * 0.78)),
                             max(2, s // 26))
        elif key == "cap":
            body = pygame.Rect(int(size * 0.22), int(size * 0.30),
                               int(size * 0.56), int(size * 0.46))
            pygame.draw.rect(surf, (90, 90, 96), body,
                             border_radius=max(3, size // 16))
            pygame.draw.rect(surf, (90, 90, 96),
                             (int(size * 0.42), int(size * 0.22),
                              int(size * 0.16), int(size * 0.08)))
            seg_w = int(body.w // 3) - 4
            for i in range(2):
                seg = pygame.Rect(body.x + 4 + i * (seg_w + 4),
                                  body.y + 4, seg_w, body.h - 8)
                pygame.draw.rect(surf, ICON_BATTERY, seg,
                                 border_radius=max(2, size // 22))
        elif key == "regen":
            pts = [(int(size * 0.56), int(size * 0.10)),
                   (int(size * 0.28), int(size * 0.56)),
                   (int(size * 0.48), int(size * 0.56)),
                   (int(size * 0.40), int(size * 0.92)),
                   (int(size * 0.72), int(size * 0.42)),
                   (int(size * 0.52), int(size * 0.42))]
            pygame.draw.polygon(surf, ICON_BOLT, pts)
            pygame.draw.lines(surf, (200, 160, 30), False, pts, 2)
        elif key == "price":
            pygame.draw.circle(surf, (150, 100, 40),
                               (c, int(size * 0.60)), int(size * 0.30))
            pygame.draw.circle(surf, (180, 130, 55),
                               (c, int(size * 0.60)), int(size * 0.30),
                               max(2, size // 30))
            pygame.draw.ellipse(surf, (170, 120, 50),
                                (int(c - size * 0.14), int(size * 0.22),
                                 int(size * 0.28), int(size * 0.14)))
            a = max(3, size // 14)
            pygame.draw.line(surf, ICON_COIN,
                             (int(c - size * 0.13), int(size * 0.56)),
                             (int(c + size * 0.13), int(size * 0.56)), a)
            pygame.draw.line(surf, ICON_COIN,
                             (int(c - size * 0.13), int(size * 0.68)),
                             (int(c + size * 0.13), int(size * 0.68)), a)
            pygame.draw.line(surf, ICON_COIN,
                             (c, int(size * 0.46)),
                             (c, int(size * 0.78)), a)
        elif key == "health":
            r = int(size * 0.22)
            surf_h = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf_h, ICON_HEART,
                               (int(c - r * 0.9), int(size * 0.42)), r)
            pygame.draw.circle(surf_h, ICON_HEART,
                               (int(c + r * 0.9), int(size * 0.42)), r)
            pygame.draw.polygon(
                surf_h, ICON_HEART,
                [(int(c - r * 1.85), int(size * 0.50)),
                 (int(c + r * 1.85), int(size * 0.50)),
                 (int(c), int(size * 0.88))])
            arm = max(3, size // 14)
            pygame.draw.rect(surf_h, (250, 245, 240),
                             (c - arm // 2, int(size * 0.40),
                              arm, int(size * 0.26)),
                             border_radius=arm // 3)
            pygame.draw.rect(surf_h, (250, 245, 240),
                             (int(c - size * 0.10), int(size * 0.50),
                              int(size * 0.20), arm),
                             border_radius=arm // 3)
            surf.blit(surf_h, (0, 0))
        elif key == "bnd":
            self.draw_bandage(surf, int(s * 0.38), c, int(s * 0.66))
            self.draw_antidote(surf, int(s * 0.74), int(s * 0.62),
                               int(s * 0.52))
        elif key == "compass":
            self.draw_compass(surf, c, c, int(s * 0.78))
        elif key == "magnet":
            self.draw_magnet(surf, c, c, int(s * 0.78))
        elif key == "clover":
            self.draw_clover(surf, c, c, int(s * 0.78))

        self.icon_cache[cache_key] = surf
        return surf

    # ---------- кэш картинки стога ----------


    def draw_compass(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        cp = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(cp, (70, 60, 40), (r, r), r)
        pygame.draw.circle(cp, (235, 220, 185), (r, r), int(r * 0.86))
        pygame.draw.circle(cp, (70, 60, 40), (r, r), int(r * 0.62))
        pygame.draw.line(cp, (60, 70, 190),
                         (r, r - int(r * 0.55)), (r, r + int(r * 0.1)),
                         max(3, r // 5))
        pygame.draw.line(cp, (200, 60, 50),
                         (r, r + int(r * 0.55)), (r, r - int(r * 0.1)),
                         max(3, r // 5))
        pygame.draw.circle(cp, (240, 230, 200), (r, r), max(2, r // 5))
        if alpha is not None:
            cp.set_alpha(alpha)
        surf.blit(cp, (int(cx - r), int(cy - r)))



    def draw_magnet(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        mg = pygame.Surface((d, d), pygame.SRCALPHA)
        lw = max(4, r // 3)
        pygame.draw.rect(mg, (200, 60, 60),
                         (r - lw, int(r * 0.25), lw, int(r * 0.75)),
                         border_radius=lw // 2)
        pygame.draw.rect(mg, (70, 90, 200),
                         (r + 1, int(r * 0.25), lw, int(r * 0.75)),
                         border_radius=lw // 2)
        pygame.draw.circle(mg, (225, 215, 200),
                           (r, r + int(r * 0.2)), int(r * 0.72), lw)
        pygame.draw.rect(mg, (225, 215, 200),
                         (r - lw - 1, r + int(r * 0.45), lw + 2,
                          int(r * 0.3)))
        pygame.draw.rect(mg, (225, 215, 200),
                         (r + 1, r + int(r * 0.45), lw + 2, int(r * 0.3)))
        if alpha is not None:
            mg.set_alpha(alpha)
        surf.blit(mg, (int(cx - r), int(cy - r)))



    def draw_clover(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        cl = pygame.Surface((d, d), pygame.SRCALPHA)
        lr = int(r * 0.42)
        for dx, dy in ((-lr, -lr // 3), (lr, -lr // 3), (0, lr // 2)):
            pygame.draw.circle(cl, (60, 150, 70), (r + dx, r + dy), lr)
        pygame.draw.line(cl, (40, 110, 50),
                         (r, r + lr), (r, r + r - 2), max(3, r // 8))
        if alpha is not None:
            cl.set_alpha(alpha)
        surf.blit(cl, (int(cx - r), int(cy - r)))
'''

GAME_SHOP_SOURCE = r'''
# -*- coding: utf-8 -*-
# Лавка улучшений: поверхность и выдвижная панель

import math
import random
import pygame

from game_config import *


class ShopMixin:
    """Лавка улучшений: поверхность и выдвижная панель"""


    # ---------- выдвижная лавка ----------
    def make_shop_surface(self):
        w, h = self.screen.get_size()
        self.shop_panel_h = min(SHOP_H, h)
        ph = self.shop_panel_h
        surf = pygame.Surface((w, ph)).convert()
        surf.fill(SHOP_BG)
        pygame.draw.rect(surf, PANEL_EDGE, (0, 0, w, 4))

        title = self.font_big.render("ЛАВКА УЛУЧШЕНИЙ", True, GOLD)
        surf.blit(title, title.get_rect(center=(w // 2, 40)))

        for key, panel in self.shop_panels:
            if panel.bottom > ph - 84:
                continue
            it_title, it_desc = self.shop_item_info(key)
            lvl = {"shovel": self.shovel, "cap": self.cap_lvl,
                   "regen": self.regen_lvl, "price": self.price_lvl,
                   "health": self.health_lvl, "bnd": self.bnd_lvl}[key]
            pygame.draw.rect(surf, PANEL_BG, panel, border_radius=14)
            pygame.draw.rect(surf, PANEL_EDGE, panel, 3, border_radius=14)

            icon = self.shop_icon(key, 80)
            surf.blit(icon, (panel.x + 12, panel.y + 20))

            heading = "%s   ур. %d" % (it_title, lvl)
            surf.blit(self.font_shop_head.render(heading, True, GOLD),
                      (panel.x + 104, panel.y + 10))
            surf.blit(self.font_shop_desc.render(it_desc, True, TEXT),
                      (panel.x + 104, panel.y + 58))

        self.shop_surf = surf
        self.shop_buttons["close"] = pygame.Rect(
            w // 2 - 180, ph - 72, 360, 58)



    def draw_shop(self):
        if self.shop_slide <= 0.0:
            return
        if self.shop_surf is None:
            self.make_shop_surface()
        w, h = self.screen.get_size()
        dy = self.shop_offset()
        top = h - dy

        if top > 0:
            shade = pygame.Surface((w, top), pygame.SRCALPHA)
            shade.fill((0, 0, 0, min(120, int(120 * self.shop_slide))))
            self.screen.blit(shade, (0, 0))

        self.screen.blit(self.shop_surf, (0, top))

        # шапка: монета и счётчик (монеты видны всегда)
        row_cy = top + SHOP_TOP - 46
        self.draw_coin(self.screen, 34, row_cy, 36)
        money_text = self.font_mid.render("Монет: %d" % self.money,
                                          True, GOLD)
        self.screen.blit(money_text,
                         (60, row_cy - money_text.get_height() // 2))

        costs = {
            "shovel": self.shovel_cost(),
            "cap": self.cap_cost(),
            "regen": self.regen_cost(),
            "price": self.price_cost(),
            "health": self.health_cost(),
            "bnd": self.bnd_cost(),
        }
        for key, cost in costs.items():
            if "buy_" + key not in self.shop_buttons:
                continue
            rect = self.shop_buttons["buy_" + key].move(0, top)
            affordable = self.money >= cost
            # цена показывается ВСЕГДА, в обоих режимах
            btn_text = "Купить (%d)" % cost
            self.draw_button(rect, btn_text,
                             enabled=affordable, ok=affordable)

        self.draw_button(self.shop_buttons["close"].move(0, top),
                         "Скрыть лавку")

    # ---------- экран победы ----------



    def open_shop(self):
        self.shop_target = 1.0
        self.help_target = 0.0



    def close_shop(self):
        self.shop_target = 0.0
'''

GAME_HELP_SOURCE = r'''
# -*- coding: utf-8 -*-
# Справка «?»: поверхность и выдвижная панель

import math
import random
import pygame

from game_config import *


class HelpMixin:
    """Справка «?»: поверхность и выдвижная панель"""


    # ---------- выдвижная справка «?» ----------
    def make_help_surface(self):
        w, h = self.screen.get_size()
        self.help_panel_h = min(HELP_H, h)
        ph = self.help_panel_h
        surf = pygame.Surface((w, ph)).convert()
        surf.fill(SHOP_BG)
        pygame.draw.rect(surf, PANEL_EDGE, (0, 0, w, 4))

        title = self.font_big.render("СПРАВКА ПО ИГРЕ", True, GOLD)
        surf.blit(title, title.get_rect(center=(w // 2, 44)))

        lines = [
            ("ЦЕЛЬ", GOLD),
            ("Найти иголку в стоге сена и продать остальное.", TEXT),
            ("Тап — рывок лопатой: каждая вскрытая клетка", TEXT),
            ("стоит 1 силу. Большая лопата копает больше клеток,", TEXT),
            ("но и рискует сильнее — ловушки срабатывают все!", TEXT),
            ("", TEXT),
            ("МЕНЮ И ПАУЗА", GOLD),
            ("Кнопка «II» или Esc — пауза: продолжить,", TEXT),
            ("рестарт уровня, новая игра, выход в меню.", TEXT),
            ("Если долго ничего не делать, появится", TEXT),
            ("подсказка: куда нажать или где копать.", TEXT),
            ("", TEXT),
            ("ТОРГОВЛЯ", GOLD),
            ("Копите сено и продавайте кнопкой «Продать сено»", TEXT),
            ("внизу — она показывает, сколько монет дадут.", TEXT),
            ("Закрыть справку — «?» или тап по стогу.", TEXT),
            ("", TEXT),
            ("ЦЕНА СЕНА", GOLD),
            ("Чем желтее клетка, тем дешевле сено, чем коричневее —", TEXT),
            ("тем дороже, но тем реже оно встречается", TEXT),
            ("и тем вероятнее в нём ловушка!", RED),
            ("Тёмные клетки мерцают красным —", RED),
            ("там ловушки чаще всего.", RED),
            ("", TEXT),
            ("ЛОВУШКИ И НАХОДКИ", GOLD),
            ("Камень — лопата откатывается на 1 уровень.", RED),
            ("Укус зверя — бьёт всё сильнее с каждым уровнем", RED),
            ("и окаймляет экран красным.", RED),
            ("Ядовитое растение — ОТРАВЛЯЕТ: здоровье тает", PURPLE_MSG),
            ("каждую секунду, экран мутит фиолетовым, а яд", PURPLE_MSG),
            ("крепчает и действует дольше на дальних уровнях.", PURPLE_MSG),
            ("", TEXT),
            ("ЗДОРОВЬЕ НЕ ВОССТАНАВЛИВАЕТСЯ САМО", GOLD),
            ("Лечить можно только бинтами. Ноль здоровья", RED),
            ("— вы УМИРАЕТЕ: теряете 50% монет, сено", RED),
            ("сгорает, уровень заново, силы обнуляются.", RED),
            ("Если здоровье на исходе, а бинтов нет —", GREEN_MSG),
            ("раз за уровень найдётся бесплатный бинт.", GREEN_MSG),
            ("", TEXT),
            ("АПТЕЧКА ВНИЗУ", GOLD),
            ("Бинт — тап по белому рулону: лечит.", GREEN_MSG),
            ("Противоядие — тап по флакону: снимает отравление.", GREEN_MSG),
            ("Если карман полон — лишнее теряется!", RED),
            ("При первом укусе или отравлении игра", TEXT),
            ("подсветит нужное лекарство — просто нажмите.", TEXT),
            ("", TEXT),
            ("ЛОВУШКИ В РЫВКЕ", GOLD),
            ("Срабатывают ВСЕ ловушки в накопанных клетках.", RED),
            ("Бинты и противоядия теряются, если", RED),
            ("в рывке сработала хоть одна ловушка.", RED),
            ("", TEXT),
            ("РЕДКИЕ НАХОДКИ", GOLD),
            ("Компас — подсвечивает часть стога с иглой.", GREEN_MSG),
            ("Магнит — следующий рывок копает вдвое больше.", GREEN_MSG),
            ("Клевер — 30 секунд: шанс 35% спастись от ловушки.",
             GREEN_MSG),
            ("Редкие находки не теряются от ловушек.", GREEN_MSG),
            ("", TEXT),
            ("СЕРИЯ РЫВКОВ", GOLD),
            ("Каждые 10 рывков без ловушек — бонус монетами.", GOLD),
            ("Ловушка рвёт серию.", TEXT),
            ("", TEXT),
            ("НАГРАДА ЗА УРОВЕНЬ", GOLD),
            ("Прошли уровень — бонус 15 x уровень монет.", GOLD),
            ("Первые уровни мягче: ловушки слабее,", TEXT),
            ("пока вы учитесь — дальше стог злее.", TEXT),
            ("Сено дорожает с уровнем — уровни короче.", TEXT),
            ("", TEXT),
            ("БЕСКОНЕЧНЫЙ СТОГ И ЗОЛОТАЯ ИГЛА", GOLD),
            ("Уровней нет — стог бесконечен: ловушки", GOLD),
            ("злее, а бонус за иглу растёт. Золотая игла", GOLD),
            ("(1 из 15 стогов) даёт бонус x5.", GOLD),
            ("", TEXT),
            ("ЛАВКА УЛУЧШЕНИЙ", GOLD),
            ("Шесть веток: лопата, запас и скорость сил,", TEXT),
            ("цена сена, здоровье, аптека. Всё быстро дорожает.", TEXT),
        ]
        step = max(22, min(30, (ph - 160) // max(1, len(lines))))
        y = 88
        for text, color in lines:
            if text:
                surf.blit(self.font_shop_desc.render(text, True, color),
                          (30, y))
            y += step

        self.help_surf = surf



    def draw_help_panel(self):
        if self.help_slide <= 0.0:
            return
        if self.help_surf is None:
            self.make_help_surface()
        w, h = self.screen.get_size()
        dy = self.help_offset()
        top = h - dy

        if top > 0:
            shade = pygame.Surface((w, top), pygame.SRCALPHA)
            shade.fill((0, 0, 0, min(140, int(140 * self.help_slide))))
            self.screen.blit(shade, (0, 0))

        self.screen.blit(self.help_surf, (0, top))
        # кнопки закрытия нет: «?» или тап по стогу



    def draw_help_button(self):
        rect = self.help_button
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = BTN_HOVER if hovered else BTN
        pygame.draw.circle(self.screen, color, rect.center, rect.w // 2)
        pygame.draw.circle(self.screen, (30, 20, 10), rect.center,
                           rect.w // 2, 3)
        label = self.font_shop_head.render("?", True, TEXT)
        self.screen.blit(label, label.get_rect(center=rect.center))

    # ---------- выдвижная лавка ----------



    def open_help(self):
        self.help_target = 1.0
        self.shop_target = 0.0



    def close_help(self):
        self.help_target = 0.0
'''

GAME_SCREENS_SOURCE = r'''
# -*- coding: utf-8 -*-
# Экраны: начальное меню, пауза, победа и смерть

import math
import random
import pygame

from game_config import *


class ScreensMixin:
    """Экраны: начальное меню, пауза, победа и смерть"""


    # ---------- начальный экран ----------
    def draw_menu_screen(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((20, 14, 8, 190))
        self.screen.blit(overlay, (0, 0))
        cx = w // 2
        self.draw_centered("ИГЛА В СТОГЕ СЕНА", self.font_big,
                           int(h * 0.20), GOLD)
        ny = int(h * 0.20) + 62
        needle_color = GOLD if getattr(self, "golden_needle", False) \
            else SILVER
        pygame.draw.line(self.screen, needle_color, (cx - 40, ny + 30),
                         (cx + 40, ny - 30), 5)
        pygame.draw.circle(self.screen, needle_color, (cx - 40, ny + 30), 8)

        bw, bh, gap = 420, 66, 22
        y0 = int(h * 0.40)
        r1 = pygame.Rect(cx - bw // 2, y0, bw, bh)
        r2 = pygame.Rect(cx - bw // 2, y0 + (bh + gap), bw, bh)
        r3 = pygame.Rect(cx - bw // 2, y0 + 2 * (bh + gap), bw, bh)
        self.menu_buttons = {"continue": r1, "new": r2, "quit": r3}
        self.draw_button(r1, "Продолжить игру", enabled=self.has_save)
        self.draw_button(r2, "Начать новую игру")
        self.draw_button(r3, "Выход")

    # ---------- меню паузы ----------
    def draw_pause_screen(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((20, 14, 8, 170))
        self.screen.blit(overlay, (0, 0))
        pw, ph = 460, 372
        px, py = (w - pw) // 2, (h - ph) // 2
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (25, 18, 10, 240), panel.get_rect(),
                         border_radius=18)
        pygame.draw.rect(panel, (255, 210, 80, 230), panel.get_rect(), 4,
                         border_radius=18)
        self.screen.blit(panel, (px, py))
        self.draw_centered("ПАУЗА", self.font_big, py + 52, GOLD)
        bw, bh, gap = 380, 56, 14
        y0 = py + 112
        names = [("continue", "Продолжить"),
                 ("restart", "Рестарт уровня"),
                 ("new", "Начать новую игру"),
                 ("menu", "Выход в меню")]
        self.pause_buttons = {}
        for i, (key, text) in enumerate(names):
            r = pygame.Rect(px + (pw - bw) // 2, y0 + i * (bh + gap), bw, bh)
            self.pause_buttons[key] = r
            self.draw_button(r, text, next_btn=(key == "continue"))

    # ---------- экран победы ----------
    def draw_win_screen(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((20, 14, 8, 215))
        self.screen.blit(overlay, (0, 0))

        cx = w // 2
        self.draw_centered("ИГОЛКА НАЙДЕНА!",
                           self.font_big, int(h * 0.24), GOLD)
        ny = int(h * 0.24) + 55
        needle_color = GOLD if self.golden_needle else SILVER
        pygame.draw.line(self.screen, needle_color, (cx - 40, ny + 30),
                         (cx + 40, ny - 30), 5)
        pygame.draw.circle(self.screen, needle_color, (cx - 40, ny + 30), 8)

        stats = [
            "Открыт уровень %d" % (self.level + 1),
            "Монет в кармане: %d" % self.money,
            "Бинты: %d/%d   Противоядия: %d/%d"
            % (self.bandages, self.bandage_cap(),
               self.antidotes, self.antidote_cap()),
        ]
        for i, line in enumerate(stats):
            self.draw_centered(line, self.font_mid,
                               int(h * 0.24) + 110 + i * 42)

        if self.golden_needle:
            self.draw_centered(
                "ЗОЛОТАЯ ИГЛА! Бонус x%d" % GOLD_NEEDLE_BONUS_MULT,
                self.font_mid, int(h * 0.24) + 110 + len(stats) * 42,
                GOLD)

        bw, bh, gap = 220, 60, 14
        y0 = int(h * 0.68)
        total = bw * 3 + gap * 2
        x0 = cx - total // 2
        r1 = pygame.Rect(x0, y0, bw, bh)
        r2 = pygame.Rect(x0 + bw + gap, y0, bw, bh)
        r3 = pygame.Rect(x0 + 2 * (bw + gap), y0, bw, bh)
        self.win_buttons = {"again": r1, "next": r2, "keep": r3}
        self.draw_button(r1, "Играть снова")
        self.draw_button(r2, "Уровень %d ->" % (self.level + 1),
                         next_btn=True)
        self.draw_button(r3, "Остаться в стоге")

    # ---------- экран смерти ----------
    def draw_death_screen(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((60, 10, 10, 225))
        self.screen.blit(overlay, (0, 0))

        cx = w // 2
        self.draw_centered("ВЫ УМЕРЛИ",
                           self.font_big, int(h * 0.28), RED)
        lines = [
            "Потеряно %d%% монет, непроданное сено сгорело."
            % int((1.0 - DEATH_MONEY_KEEP) * 100),
            "Силы обнулены — придётся ждать восстановления.",
            "Уровень начнётся заново — стог перевёрнут.",
            "Улучшения сохраняются.",
        ]
        for i, line in enumerate(lines):
            self.draw_centered(line, self.font_mid,
                               int(h * 0.28) + 90 + i * 44)

        bw, bh = 340, 60
        y0 = int(h * 0.66)
        r1 = pygame.Rect(cx - bw // 2, y0, bw, bh)
        self.death_buttons = {"continue": r1}
        self.draw_button(r1, "Продолжить", ok=True)
'''

GAME_DIGGING_SOURCE = r'''
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
                self.tutorial = {"item": "antidote"}
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
                self.tutorial = {"item": "bandage"}
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
        elif item == "magnet":
            self.magnet_ready = True
            self.show_notice(item)
            self.notice["sub"] = "Следующий рывок вдвое больше"
        elif item == "clover":
            self.clover_time = CLOVER_TIME
            self.show_notice(item)
            self.notice["sub"] = (
                "%d секунд: шанс %d%% спастись от ловушек"
                % (int(CLOVER_TIME), int(CLOVER_SAVE_CHANCE * 100)))

    # ---------- копание ----------



    # ---------- копание ----------
    def resolve_items(self, dug_now):
        """Срабатывают ВСЕ ловушки в накопанных клетках.
        Клевер спасает от каждой сработавшей ловушки отдельно
        (шанс CLOVER_SAVE_CHANCE). Бинты и противоядия достаются,
        только если в рывке не сработала ни одна ловушка.
        Редкие находки срабатывают всегда. Возвращает False,
        если сработала хоть одна ловушка."""
        found = [i for i in dug_now if self.cells[i]["item"]]
        if not found:
            return True
        rare = [i for i in found if self.cells[i]["item"] in RARE_ITEMS]
        base = [i for i in found if self.cells[i]["item"] not in RARE_ITEMS]
        rare_items = [self.cells[i]["item"] for i in rare]
        base_items = [self.cells[i]["item"] for i in base]
        for i in found:
            self.cells[i]["item"] = None
        for it in rare_items:
            self.trigger_item(it)
        trapped = False
        lost_supplies = False
        for it in base_items:
            if it in ("stone", "animal", "plant"):
                if (self.clover_time > 0
                        and random.random() < CLOVER_SAVE_CHANCE):
                    self.add_message("Клевер спас от ловушки!", GREEN_MSG)
                    continue
                self.trigger_item(it)
                trapped = True
            elif trapped:
                lost_supplies = True
        if lost_supplies:
            self.add_message("Ловушка в рывке: лекарства потеряны", RED)
        return not trapped



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
                self.compass_quadrant = None
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
'''

GAME_LOOP_SOURCE = r'''
# -*- coding: utf-8 -*-
# Главный цикл: меню/игра/пауза, события, клики, отрисовка кадра

import math
import random
import pygame

from game_config import *


class LoopMixin:
    """Главный цикл: состояния меню/игры/паузы, события, клики"""


    # ---------- меню и пауза ----------
    def handle_menu_click(self, pos):
        for name, rect in self.menu_buttons.items():
            if rect.collidepoint(pos):
                if name == "continue":
                    self.state = "game"
                    return None
                if name == "new":
                    self.start_new_game()
                    self.state = "game"
                    return None
                if name == "quit":
                    return "quit"
        return None



    def open_pause(self):
        if self.won or self.dead:
            return
        self.state = "pause"
        self.shop_target = 0.0
        self.help_target = 0.0
        self.tutorial = None
        self.idle_hint = None



    def handle_pause_click(self, pos):
        for name, rect in self.pause_buttons.items():
            if rect.collidepoint(pos):
                if name == "continue":
                    self.state = "game"
                elif name == "restart":
                    self.restart()
                    self.state = "game"
                elif name == "new":
                    self.start_new_game()
                    self.state = "game"
                elif name == "menu":
                    self.save_game()
                    self.tutorial = None
                    self.idle_hint = None
                    self.state = "menu"

    # ---------- обработка кликов в игре ----------
    def handle_click(self, pos):
        if self.dead:
            for name, rect in self.death_buttons.items():
                if rect.collidepoint(pos):
                    if name == "continue":
                        lost = int(self.money * (1.0 - DEATH_MONEY_KEEP))
                        self.money = int(self.money * DEATH_MONEY_KEEP)
                        self.hay = 0
                        self.hay_value = 0
                        self.stamina = 0.0
                        self.health = self.max_health
                        self.poison_time = 0.0
                        self.clover_time = 0.0
                        self.compass_hint = None
                        self.compass_quadrant = None
                        self.magnet_ready = False
                        self.streak = 0
                        self.bandages = min(self.bandages,
                                            self.bandage_cap())
                        self.antidotes = min(self.antidotes,
                                             self.antidote_cap())
                        self.build_field()
                        self.won = False
                        self.needle_found = False
                        self.digs = 0
                        self.straws = []
                        self.dead = False
                        self.bite_flash = 0.0
                        self.poison_flash = 0.0
                        self.tutorial = None
                        self.save_game()
                        self.add_message(
                            "Вы возродились. Потеряно %d монет, сено "
                            "сгорело. Уровень %d заново, силы на нуле"
                            % (lost, self.level), RED)
                    return
            return

        if self.help_slide > 0.95:
            h = self.screen.get_height()
            top = h - self.help_offset()
            visible = pygame.Rect(0, max(0, top), self.screen.get_width(),
                                  self.help_offset())
            if not visible.collidepoint(pos):
                self.close_help()
            return

        if self.won:
            for name, rect in self.win_buttons.items():
                if rect.collidepoint(pos):
                    if name == "again":
                        self.restart()
                    elif name == "keep":
                        self.won = False
                        self.field_dirty = True
                    elif name == "next":
                        self.next_level()
                    return
            return

        if self.shop_slide > 0.95:
            h = self.screen.get_height()
            top = h - self.shop_offset()
            visible = pygame.Rect(0, max(0, top), self.screen.get_width(),
                                  self.shop_offset())
            if not visible.collidepoint(pos):
                self.close_shop()
                return
            for name, rect in self.shop_buttons.items():
                if rect.move(0, top).collidepoint(pos):
                    if name == "close":
                        self.close_shop()
                    elif name.startswith("buy_"):
                        self.buy(name[4:])
                    return
            return

        if self.bandage_btn.collidepoint(pos):
            self.use_bandage()
            return
        if self.antidote_btn.collidepoint(pos):
            self.use_antidote()
            return

        for name, rect in self.main_buttons.items():
            if rect.collidepoint(pos):
                if name == "sell":
                    if self.hay > 0:
                        self.sell()
                        self.add_message("Сено продано", GREEN_MSG)
                elif name == "shop":
                    self.open_shop()
                elif name == "next":
                    if self.needle_found:
                        self.next_level()
                return
        self.dig_at(pos)

    # ---------- подсказка простоя ----------
    def update_idle_hint(self):
        if self.idle_time < IDLE_HINT_AFTER:
            return
        if self.idle_hint is not None:
            return
        if self.won or self.dead or self.tutorial:
            return
        if self.shop_slide > 0.5 or self.help_slide > 0.5:
            return
        if self.needle_found:
            self.idle_hint = {
                "text": "Нажмите «Уровень %d», чтобы идти дальше"
                        % (self.level + 1),
                "target": self.main_buttons["next"].copy(),
                "cell": None}
        elif self.poison_time > 0 and self.antidotes > 0:
            self.idle_hint = {
                "text": "Вы отравлены! Нажмите на флакон",
                "target": self.antidote_btn.copy(), "cell": None}
        elif self.health < self.max_health * 0.4 and self.bandages > 0:
            self.idle_hint = {
                "text": "Мало здоровья! Нажмите на бинт",
                "target": self.bandage_btn.copy(), "cell": None}
        elif self.hay_value > 0:
            self.idle_hint = {
                "text": "Продайте сено, чтобы получить монеты",
                "target": self.main_buttons["sell"].copy(),
                "cell": None}
        else:
            undug = [i for i, c in enumerate(self.cells) if not c["dug"]]
            if undug:
                i = random.choice(undug)
                self.idle_hint = {"text": "Копайте здесь!",
                                  "target": None, "cell": i}

    # ---------- главный цикл ----------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            self.time += dt

            if self.state == "game":
                if self.stamina < self.max_stamina:
                    self.stamina = min(self.max_stamina,
                                       self.stamina +
                                       self.regen_rate() * dt)

                if self.clover_time > 0:
                    self.clover_time = max(0.0, self.clover_time - dt)
                    if self.clover_time == 0.0:
                        self.add_message("Клевер больше не действует",
                                         GREEN_MSG)

                if self.poison_time > 0:
                    self.poison_time -= dt
                    if self.poison_time <= 0:
                        self.poison_time = 0.0
                        self.add_message("Отравление прошло", GREEN_MSG)
                    else:
                        self.health -= self.poison_rate() * dt
                        if self.health <= 0:
                            self.health = 0
                            self.dead = True

                self.maybe_free_bandage()
                self.update_flashes(dt)
                self.update_straws(dt)

                for m in self.messages:
                    m["life"] -= dt
                self.messages = [m for m in self.messages
                                 if m["life"] > 0]
                if self.notice:
                    self.notice["life"] -= dt
                    if self.notice["life"] <= 0:
                        self.notice = None

                if self.shop_slide < self.shop_target:
                    self.shop_slide = min(self.shop_target,
                                          self.shop_slide +
                                          SLIDE_SPEED * dt)
                elif self.shop_slide > self.shop_target:
                    self.shop_slide = max(self.shop_target,
                                          self.shop_slide -
                                          SLIDE_SPEED * dt)
                if self.help_slide < self.help_target:
                    self.help_slide = min(self.help_target,
                                          self.help_slide +
                                          SLIDE_SPEED * dt)
                elif self.help_slide > self.help_target:
                    self.help_slide = max(self.help_target,
                                          self.help_slide -
                                          SLIDE_SPEED * dt)

                self.idle_time += dt
                self.update_idle_hint()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state != "menu":
                        self.save_game()
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        event.size, pygame.RESIZABLE)
                    self.make_fonts()
                    self.build_field()
                    self.build_ui()
                    self.field_dirty = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "game":
                            self.open_pause()
                        elif self.state == "pause":
                            self.state = "game"
                    self.idle_time = 0.0
                    self.idle_hint = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = getattr(event, "pos", None)
                    if pos is None:
                        continue
                    if self.state == "menu":
                        if self.handle_menu_click(pos) == "quit":
                            running = False
                    elif self.state == "pause":
                        self.handle_pause_click(pos)
                    else:
                        if (not self.won and not self.dead
                                and self.help_button.collidepoint(pos)):
                            if self.help_target > 0.5:
                                self.close_help()
                            else:
                                self.open_help()
                        elif (not self.won and not self.dead
                                and self.pause_button.collidepoint(pos)):
                            self.open_pause()
                        else:
                            self.handle_click(pos)
                    self.idle_time = 0.0
                    self.idle_hint = None

            if self.state == "menu":
                self.draw_field()
                self.draw_menu_screen()
            else:
                self.draw_field()
                self.draw_screen_effects()
                self.draw_hud()
                self.draw_bonus_icons()
                self.draw_shop()
                self.draw_help_panel()
                self.draw_tutorial()
                self.draw_idle_hint()
                if not self.won and not self.dead:
                    self.draw_help_button()
                    self.draw_pause_button()
                if self.state == "pause":
                    self.draw_pause_screen()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
'''

GAME_SAVE_SOURCE = r'''
# -*- coding: utf-8 -*-
# Сохранение прогресса: hay_save.json рядом с файлами игры

import json
import os

from game_config import *

SAVE_FILE = "hay_save.json"


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
            "free_bandage_used": self.free_bandage_used,
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
            self.free_bandage_used = bool(
                data.get("free_bandage_used", False))
        except (TypeError, ValueError):
            pass
'''

GAME_CORE_SOURCE = r'''
# -*- coding: utf-8 -*-
# Ядро игры: класс Game собирается из примесей.

import pygame

from game_config import *
from game_field import FieldMixin
from game_health import HealthMixin
from game_effects import EffectsMixin
from game_economy import EconomyMixin
from game_ui import UIMixin
from game_drawings import DrawingsMixin
from game_shop import ShopMixin
from game_help import HelpMixin
from game_screens import ScreensMixin
from game_digging import DiggingMixin
from game_loop import LoopMixin
from game_save import SaveMixin


class Game(SaveMixin, FieldMixin, HealthMixin, EffectsMixin, EconomyMixin,
           UIMixin, DrawingsMixin, ShopMixin, HelpMixin, ScreensMixin,
           DiggingMixin, LoopMixin):
    """Игра «Игла в стоге сена»."""

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Игла в стоге сена")
        self.screen = pygame.display.set_mode((720, 1280),
                                              pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.font_big = None
        self.font_mid = None
        self.font_small = None
        self.font_shop_head = None
        self.font_shop_desc = None
        self.make_fonts()

        self.level = 1
        self.field_rect = pygame.Rect(0, 0, 0, 0)
        self.cols = 0
        self.rows = 0
        self.cw = 0.0
        self.ch = 0.0
        self.cells = []
        self.needle_idx = -1
        self.won = False
        self.dead = False
        self.needle_found = False
        self.time = 0.0

        self.money = 0
        self.hay = 0
        self.hay_value = 0
        self.shovel = 1
        self.cap_lvl = 0
        self.regen_lvl = 0
        self.price_lvl = 0
        self.health_lvl = 0
        self.bnd_lvl = 0
        self.bandages = 0
        self.antidotes = 0
        self.poison_time = 0.0
        self.max_stamina = float(STAMINA_BASE)
        self.stamina = self.max_stamina
        self.max_health = float(HEALTH_BASE)
        self.health = self.max_health
        self.digs = 0

        # новые механики: редкие находки, серия, золотая игла
        self.compass_hint = None
        self.magnet_ready = False
        self.clover_time = 0.0
        self.streak = 0
        self.golden_needle = False

        # вспышки экрана: плотность 0..1, затухают со временем
        self.bite_flash = 0.0
        self.poison_flash = 0.0

        self.messages = []
        self.notice = None
        self.straws = []

        self.help_slide = 0.0
        self.help_target = 0.0
        self.help_surf = None
        self.help_panel_h = 0

        self.shop_slide = 0.0
        self.shop_target = 0.0
        self.shop_panel_h = 0
        self.shop_surf = None

        self.text_cache = {}
        self.icon_cache = {}
        self.field_surf = None
        self.field_dirty = True

        # состояния: меню, игра, пауза
        self.state = "menu"
        self.menu_buttons = {}
        self.pause_buttons = {}
        self.has_save = False

        # обучение и подсказки простоя
        self.tut_bandage_done = False
        self.tut_antidote_done = False
        self.tutorial = None
        self.idle_time = 0.0
        self.idle_hint = None
        self.free_bandage_used = False

        self.main_buttons = {}
        self.shop_buttons = {}
        self.win_buttons = {}
        self.death_buttons = {}
        self.build_field()
        self.build_ui()
        self.load_game()          # прогресс из hay_save.json
        self.stamina = self.max_stamina
        self.health = self.max_health



    def make_fonts(self):
        try:
            self.font_big = pygame.font.SysFont("arial", 52, bold=True)
            self.font_mid = pygame.font.SysFont("arial", 30)
            self.font_small = pygame.font.SysFont("arial", 24)
            self.font_shop_head = pygame.font.SysFont("arial", 34, bold=True)
            self.font_shop_desc = pygame.font.SysFont("arial", 24)
        except Exception:
            self.font_big = pygame.font.Font(None, 58)
            self.font_mid = pygame.font.Font(None, 34)
            self.font_small = pygame.font.Font(None, 28)
            self.font_shop_head = pygame.font.Font(None, 40)
            self.font_shop_desc = pygame.font.Font(None, 28)
        self.text_cache = {}
        self.help_surf = None
        self.shop_surf = None



    def txt(self, string, font, color=TEXT):
        key = (id(font), string, color)
        surf = self.text_cache.get(key)
        if surf is None:
            surf = font.render(string, True, color)
            self.text_cache[key] = surf
        return surf

    def start_new_game(self):
        """Полный сброс прогресса: уровень 1, кошелёк пуст."""
        self.level = 1
        self.money = 0
        self.hay = 0
        self.hay_value = 0
        self.shovel = 1
        self.cap_lvl = 0
        self.regen_lvl = 0
        self.price_lvl = 0
        self.health_lvl = 0
        self.bnd_lvl = 0
        self.bandages = 0
        self.antidotes = 0
        self.poison_time = 0.0
        self.max_stamina = float(STAMINA_BASE)
        self.stamina = self.max_stamina
        self.max_health = float(HEALTH_BASE)
        self.health = self.max_health
        self.compass_hint = None
        self.compass_quadrant = None
        self.magnet_ready = False
        self.clover_time = 0.0
        self.streak = 0
        self.won = False
        self.dead = False
        self.needle_found = False
        self.digs = 0
        self.bite_flash = 0.0
        self.poison_flash = 0.0
        self.messages = []
        self.notice = None
        self.straws = []
        self.tut_bandage_done = False
        self.tut_antidote_done = False
        self.tutorial = None
        self.idle_time = 0.0
        self.idle_hint = None
        self.free_bandage_used = False
        self.build_field()
        self.field_dirty = True
        self.save_game()

    # ---------- стог ----------
'''

game_config = _load_module("game_config", GAME_CONFIG_SOURCE)
game_field = _load_module("game_field", GAME_FIELD_SOURCE)
game_health = _load_module("game_health", GAME_HEALTH_SOURCE)
game_effects = _load_module("game_effects", GAME_EFFECTS_SOURCE)
game_economy = _load_module("game_economy", GAME_ECONOMY_SOURCE)
game_ui = _load_module("game_ui", GAME_UI_SOURCE)
game_drawings = _load_module("game_drawings", GAME_DRAWINGS_SOURCE)
game_shop = _load_module("game_shop", GAME_SHOP_SOURCE)
game_help = _load_module("game_help", GAME_HELP_SOURCE)
game_screens = _load_module("game_screens", GAME_SCREENS_SOURCE)
game_digging = _load_module("game_digging", GAME_DIGGING_SOURCE)
game_loop = _load_module("game_loop", GAME_LOOP_SOURCE)
game_save = _load_module("game_save", GAME_SAVE_SOURCE)
game_core = _load_module("game_core", GAME_CORE_SOURCE)

Game = game_core.Game

if __name__ == "__main__":
    Game().run()
