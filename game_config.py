# -*- coding: utf-8 -*-
# BUILD: v5-34 (сделан пункт 11 списка PLAN.md: виртуальный холст
# 720x1280 — интерфейс рисуется в него и растягивается на весь экран
# Android, кнопки и шрифты не мельчают; см. PLAN.md)
# Игра "Игла в стоге сена" на pygame.
# Справка по игре — кнопка «?» в панели внизу, всплывает как лавка.

import datetime
import os
import datetime
import os
import sys

try:
    import pygame
except ImportError:
    print("Сначала установите pygame: pip install pygame")
    sys.exit(1)

# ---------- настройки ----------
# ---------- экран (пункт 11) ----------
# Виртуальный холст: игра всегда рисует в него, а на реальный дисплей
# выводится растянутая копия. На ПК холст совпадает с окном, на Android
# поле и интерфейс занимают ту же долю экрана, что и на компьютере, —
# кнопки, плашки и шрифты не мельчают.
CANVAS_W = 720
CANVAS_H = 1280

# Android определяется по системной папке /data/data: на телефонах она
# есть всегда, на компьютерах нет. Переменные окружения ненадёжны.
ON_ANDROID = os.path.isdir("/data/data")

STAMINA_BASE = 20
STAMINA_STEP = 4
REGEN_BASE = 1.2
REGEN_STEP = 1.0
MAX_LEVEL = 10
NEEDLE_BONUS_BASE = 300
SHOP_H = 970           # высота лавки: 6 панелей + шапка
HELP_H = 1000   # высота справки: две страницы + кнопки навигации
SLIDE_SPEED = 4.0
SHOP_PANEL_H = 120
SHOP_GAP = 10
SHOP_TOP = 140

# плашки HUD (монеты и сено): на экранах уже этого — прячутся
HUD_CHIP_MIN_W = 690

# спотлайт-обучение: плотность тьмы, порог монет для урока «Лавка»
# и задержка перед уроком после ловушки (пункт 10: игрок сначала видит
# плашку «Укус зверя!» / «Отравление!», затем открывается подсветка)
TUT_DARK_ALPHA = 185
TUT_SHOP_MIN_MONEY = 100
TUT_DELAY = 1.0

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
# прокачка бинтов (уровень аптеки): растёт и объём лечения одного бинта,
# и сколько бинтов влезает в карман (BANDAGE_CAP_*). Укус и яд с уровнем
# становятся сильнее — бинты должны поспевать за ними: шаг лечения
# подобран так, что к середине игры бинт перекрывает укус зверя.
BANDAGE_HEAL_BASE = 25
BANDAGE_HEAL_STEP = 15
# здоровье само НЕ восстанавливается — только бинты

# милость судьбы: раз за уровень бесплатный бинт, если здоровья мало,
# а бинтов в кармане нет
LOW_HEALTH_FREE = 30

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

# цены сена растут с уровнем: x(1 + 0.1 x (уровень-1))
HAY_PRICE_LEVEL_STEP = 0.1
# множитель апгрейда «ЦЕНА СЕНА» из лавки: +25% за уровень
PRICE_UPGRADE_STEP = 0.25

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

# ---------- области затемнения ----------
# Тёмные клетки собраны в очаги: количество зависит от размера поля,
# самый тёмный оттенок получает клетка, ближайшая к центру очага,
# светлые уходят к краям от очагов. Набор оттенков не меняется, так что
# баланс ловушек и находок остаётся прежним — меняется только раскладка.
DARK_SPOT_MIN = 2            # минимум очагов на поле
DARK_SPOT_PER_CELLS = 90     # один очаг примерно на столько клеток
DARK_SPOT_MAX = 10           # максимум очагов на поле

STONE_PENALTY = 1
STONE_IMMUNE_LVL = 4     # с этой лопаты камень не откатывает уровень
STONE_MONEY_PENALTY = 10 # на максимальной лопате камень бьёт по кошельку

# приоритет находок за один рывок: чем меньше число, тем «хуже».
# За рывок срабатывает ровно одна ловушка — самая «плохая» по этому
# приоритету (камень, потом зверь, потом растение), остальные игнорируются
ITEM_PRIORITY = {"stone": 0, "animal": 1, "plant": 2,
                 "bandage": 3, "antidote": 4,
                 "compass": 5, "energy": 5, "clover": 5}
RARE_ITEMS = ("compass", "energy", "clover")

# ---------- редкие находки ----------
P_COMPASS = 0.004
P_ENERGY = 0.003
P_CLOVER = 0.004
CLOVER_TIME = 30.0         # сколько секунд действует клевер
CLOVER_SAVE_CHANCE = 0.35  # шанс спастись от сработавшей ловушки
ENERGY_TIME = 10.0         # сколько секунд действует энергетик

# ---------- золотая игла ----------
GOLD_NEEDLE_ONE_IN = 15    # каждый N-й стог
GOLD_NEEDLE_BONUS_MULT = 5

# ---------- награда за уровень ----------
LEVEL_REWARD_BASE = 15     # x уровень монет за пройденный уровень

# ---------- круг большой лопаты ----------
# Сторона рывка от DIG_CIRCLE_MIN_SIDE и больше копается кругом: клетка
# попадает, если её центр лежит в радиусе DIG_CIRCLE_K x сторона от точки
# клика. K = 0.564 (= 1/sqrt(pi)) — площадь круга как у квадрата той же
# стороны, так что добыча за рывок не меняется.
DIG_CIRCLE_MIN_SIDE = 3
DIG_CIRCLE_K = 0.564

# ---------- серии рывков ----------
STREAK_GOAL = 10
STREAK_BONUS_BASE = 50     # x уровень монет за каждые 10 чистых рывков

# ---------- бесконечный стог ----------
ENDLESS_TRAP_GROWTH = 0.05  # +5% ловушек за уровень после MAX_LEVEL
ENDLESS_BONUS_MULT = 1.25   # бонус за иглу растёт в степенной прогрессии

# ---------- смерть ----------
DEATH_MONEY_KEEP = 0.5      # после смерти остаётся 50% монет

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
ENERGY_CAN = (235, 145, 60)  # корпус банки энергетика
ENERGY_EDGE = (140, 75, 25)  # тёмная окантовка банки

# ---------- лог ошибок (crash_log.txt) ----------
# Файл нужен, чтобы игра не закрывалась молча: после внезапного закрытия
# можно открыть лог и прислать текст ошибки.
LOG_FILE = "crash_log.txt"
LOG_MAX_BYTES = 64 * 1024   # старые записи обрезаем, лог не разрастается


def log_crash(text):
    """Дописать отчёт о сбое в crash_log.txt (с датой и временем).

    Место ищем так: на Android сначала пробуем папку Downloads — файл
    оттуда видно в файловом менеджере и удобно переслать; не получилось —
    пишем рядом с файлами игры (там же, где hay_save.json). Ничего не
    открылось — печатаем в stderr.
    """
    stamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    block = "===== {} =====\n{}\n\n".format(stamp, text.rstrip())
    places = []
    downloads = "/storage/emulated/0/Download"
    if os.path.isdir(downloads):
        places.append(downloads)
    places.append(os.getcwd())
    for place in places:
        path = os.path.join(place, LOG_FILE)
        try:
            old = ""
            try:
                with open(path, "r", encoding="utf-8") as f:
                    old = f.read()
            except OSError:
                pass
            if len(old) > LOG_MAX_BYTES:
                old = old[-LOG_MAX_BYTES // 2:]
            with open(path, "w", encoding="utf-8") as f:
                f.write(old + block)
            return
        except OSError:
            continue
    sys.stderr.write(block)
