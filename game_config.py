# -*- coding: utf-8 -*-
# BUILD: v5-37 (пункты 1–4 из 5 PLAN.md ЗАВЕРШЕНЫ + фикс безопасной
# зоны по снимку экрана с телефона; горячее исправление r18: SAFE_TOP,
# SAFE_BOTTOM и wrap_text добавлены фактически — в r17 они остались
# только в этом комментарии, ядро падало NameError при запуске:
# 1) виртуальный холст убран, вся геометрия через S();
# 2) FPS = 30, clock.tick(FPS) в цикле;
# 3) ПК-ветки вычищены: KEYDOWN удалён из цикла, main.py
#    проверяет ON_ANDROID;
# 4) кэш прозрачности: подсветка компаса и иконки с альфой
#    из готовых уровней, копий поверхностей в кадре нет.
# 5) безопасная зона: на Android self.screen — subsurface
#    внутри SAFE_TOP..h-SAFE_BOTTOM; плашки переносятся
#    wrap_text по ширине экрана.
# Горячее исправление r19: тапы приходят в координатах полного
# экрана, рисование — в subsurface со смещением SAFE_TOP; добавлен
# переводчик touch_pos в конфиге, применён во всех 5 местах чтения
# координат (цикл + 4 ховера).
# Следующий пункт — 5: развилка (проверка после запуска).
# Горячее исправление r20: игра закрывалась молча при «новой игре» без
# crash_log.txt. Причины: (1) в main.py сначала печатался traceback в
# stderr — на установленном APK stderr бывает закрыт, печать роняла
# игру до записи в лог; теперь лог пишется первым, печать — под
# страховкой; (2) log_crash мог упасть на закрытом stderr — оба шага
# под страховкой; (3) добавлен data_dir (cwd на APK недоступен —
# сохранение hay_save.json могло молча не работать) и log_trace —
# метки шагов в crash_log.txt: последняя метка показывает, где игра
# умерла даже при жёстком падении ниже Python.
# Горячее исправление r21: смещение тапов вернулось — фактическое
# соответствие координат события и рисования уточняется самой
# игрой (автокалибровка по попаданиям в кнопки, tap_calib.json),
# сырые тапы пишутся в crash_log.txt для точной подстройки.

import datetime
import json
import os
import sys

try:
    import pygame
except ImportError:
    print("Сначала установите pygame: pip install pygame")
    sys.exit(1)

# ---------- настройки ----------
# ---------- экран (пункт 1 оптимизации) ----------
# Виртуального холста больше нет: игра рисует сразу в разрешение
# реального экрана (см. пункт 1 PLAN.md). CANVAS_W/CANVAS_H остались
# только как база координат 720x1280 — в них заданы размеры интерфейса,
# а S()/Sf() переводят их в пиксели реального экрана.
CANVAS_W = 720
CANVAS_H = 1280

# Android определяется по системной папке /data/data: на телефонах она
# есть всегда, на компьютерах нет. Переменные окружения ненадёжны.
ON_ANDROID = os.path.isdir("/data/data")

# ---------- частота кадров (пункт 2 оптимизации) ----------
# Игра пошаговая, анимации не требуют 60 кадров в секунду: 30
# кадров вдвое снижают нагрузку на телефон без видимой разницы.
FPS = 30

# ---------- безопасная зона Android (фикс по снимку экрана) ----------
# Системные панели (статус-бар сверху, панель навигации снизу) на
# Android накладываются поверх поверхности экрана: set_mode(FULLSCREEN)
# возвращает всю физическую панель, но её часть скрыта. Игра рисует
# только в видимую область — по этим константам (базовые px, переводит
# S() при использовании в ядре). Первая прикидка по снимку с телефона;
# после проверки подкручиваются по факту.
SAFE_TOP = 105
SAFE_BOTTOM = 75

# ---------- масштаб интерфейса (пункт 1 оптимизации) ----------
# Игра рисует сразу в разрешение реального экрана, без холста. Чтобы
# кнопки, панели и шрифты не мельчали на больших экранах, размеры,
# заданные в базовых координатах 720x1280, в местах использования
# умножаются на масштаб: S() для целых размеров (высоты панелей,
# кнопки, шрифты), Sf() для дробных (скорости анимаций). set_scale()
# вызывается один раз из game_core до построения шрифтов и поля.
#
# ВАЖНО: модули подключают конфиг через `from game_config import *`,
# поэтому масштабируемые константы (HUD_H, SHOP_H, ...) при старте
# НЕ перезаписываются — импортированные копии остались бы старыми.
# Они остаются базовыми значениями, а через S() проводятся там, где
# используются: game_field — HUD_H и CELL_*; game_loop — SLIDE_SPEED;
# game_shop — SHOP_*; game_help — HELP_H; game_ui — HUD_CHIP_MIN_W.
UI_SCALE = 1.0


def set_scale(dw, dh):
    """Посчитать масштаб интерфейса по размеру реального экрана.

    Берётся минимум по осям, чтобы интерфейс гарантированно влез и по
    ширине, и по высоте: телефонный экран выше базового 1280/720, так
    что масштаб обычно упирается в ширину, а лишняя высота достаётся
    полю — клеток становится больше, баланс не меняется.
    """
    global UI_SCALE
    UI_SCALE = min(dw / float(CANVAS_W), dh / float(CANVAS_H))


def S(v):
    """Целое число пикселей реального экрана из базовых координат."""
    return int(round(v * UI_SCALE))


def Sf(v):
    """Дробное значение (скорости и т.п.) в масштабе экрана."""
    return v * UI_SCALE


def wrap_text(text, font, max_w):
    """Разбить строку на строки, влезающие в max_w пикселей.

    Перенос по словам; одиночное слово шире лимита остаётся целиком.
    Возвращает список строк (без переноса, если текст короткий).
    """
    if not text:
        return [""]
    lines = []
    for chunk in text.split("\n"):
        cur = ""
        # страховка от аномально длинного текста (чтобы не поймать ANR):
        # больше 4000 слов в одной строке интерфейса не бывает
        for word in chunk.split(" ")[:4000]:
            test = (cur + " " + word).strip()
            if cur and font.size(test)[0] > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = test
        if cur:
            lines.append(cur)
    return lines or [""]


def touch_pos(pos):
    """Перевести координаты события из полного экрана в видимую область.

    Рисование идёт в subsurface со смещением SAFE_TOP, а тапы и мышь
    приходят в координатах физического экрана — на Android вычитаем
    SAFE_TOP из вертикали. На ПК координаты совпадают один в один.
    """
    off = TAP_OFFSET if TAP_OFFSET is not None else SAFE_TOP
    if ON_ANDROID:
        return (pos[0], int(pos[1] - off))
    return pos

# --- автокалибровка тапов (r21) ---
# Фактическое соответствие между координатами события и рисования на
# телефоне заранее неизвестно (SDL может отдавать координаты окна,
# а не полного экрана), поэтому игра уточняет смещение сама: каждое
# попадание в кнопку задаёт интервал возможных значений, интервалы
# пересекаются, середина сохраняется в tap_calib.json и переживает
# перезапуск. Несколько тапов по кнопкам — и попадание точное.
TAP_LO = 0.0
TAP_HI = 300.0
TAP_OFFSET = None  # вычитаемая величина; пока не измерена — SAFE_TOP
_TAP_LOGGED = 0


def calib_load():
    """Восстановить калибровку тапов из tap_calib.json (если есть)."""
    global TAP_OFFSET, TAP_LO, TAP_HI
    if not ON_ANDROID:
        return
    try:
        path = os.path.join(data_dir(), "tap_calib.json")
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        TAP_LO, TAP_HI = float(d["lo"]), float(d["hi"])
        if TAP_HI - TAP_LO <= 300.0:
            TAP_OFFSET = (TAP_LO + TAP_HI) / 2.0
            log_trace("калибровка тапов загружена: "
                      "{:.1f}".format(TAP_OFFSET))
    except Exception:
        pass


def calib_hit(rect, raw_y):
    """Уточнить смещение тапов по факту попадания в кнопку.

    Попадание значит, что raw_y - TAP_OFFSET лежит внутри rect, то есть
    TAP_OFFSET ∈ [raw_y - rect.bottom, raw_y - rect.top]. Интервал
    сужается с каждым попаданием, середина становится оценкой.
    """
    global TAP_OFFSET, TAP_LO, TAP_HI
    if not ON_ANDROID:
        return
    lo = max(TAP_LO, raw_y - rect.bottom)
    hi = min(TAP_HI, raw_y - rect.top)
    if lo > hi:
        return  # противоречивый тап — игнорируем
    TAP_LO, TAP_HI = lo, hi
    est = (lo + hi) / 2.0
    if TAP_OFFSET is None or abs(est - TAP_OFFSET) >= 1.0:
        TAP_OFFSET = est
        log_trace("калибровка тапов: [{:.1f}; {:.1f}], сдвиг {:.1f}"
                  .format(lo, hi, est))
        try:
            with open(os.path.join(data_dir(), "tap_calib.json"),
                      "w", encoding="utf-8") as f:
                json.dump({"lo": lo, "hi": hi}, f)
        except Exception:
            pass


def log_tap(raw_y):
    """Диагностика первых тапов: сырая вертикаль события в лог."""
    global _TAP_LOGGED
    if _TAP_LOGGED >= 40:
        return
    _TAP_LOGGED += 1
    log_trace("тап {}: y={}".format(_TAP_LOGGED, raw_y))


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


def data_dir():
    """Папка, в которую на этом устройстве реально можно писать.

    На установленном APK текущий каталог бывает недоступен (обычно это
    "/") — сохранение и лог могли молча не работать. Пробуем по очереди:
    cwd, папку рядом с файлами игры, домашнюю папку; первый каталог,
    куда удалось записать и удалить пробный файл, запоминаем.
    """
    global _DATA_DIR
    if _DATA_DIR is None:
        for cand in (os.getcwd(),
                     os.path.dirname(os.path.abspath(__file__)),
                     os.path.expanduser("~")):
            try:
                probe = os.path.join(cand, ".hay_probe")
                with open(probe, "w", encoding="utf-8") as f:
                    f.write("ok")
                os.remove(probe)
                _DATA_DIR = cand
                break
            except OSError:
                continue
        if _DATA_DIR is None:
            _DATA_DIR = os.getcwd()
    return _DATA_DIR


_DATA_DIR = None


def _log_places():
    """Список папок для записи лога: Downloads (видно в файловом
    менеджере — удобно переслать), затем data_dir()."""
    places = []
    downloads = "/storage/emulated/0/Download"
    if os.path.isdir(downloads):
        places.append(downloads)
    places.append(data_dir())
    return places


def log_trace(step):
    """Метка прогресса в crash_log.txt: последняя метка показывает, на
    каком шаге игра умерла, даже если падение случилось ниже Python
    (segfault в SDL/pygame в лог не попадает). Пишется немного:
    старт, меню-клик, первый игровой кадр."""
    block = "[trace] {} {}\n".format(
        datetime.datetime.now().strftime("%H:%M:%S"), step)
    for place in _log_places():
        path = os.path.join(place, LOG_FILE)
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(block)
            return
        except OSError:
            continue
    try:
        sys.stderr.write(block)
    except Exception:
        pass


def log_crash(text):
    """Дописать отчёт о сбое в crash_log.txt (с датой и временем).

    Место ищем так: на Android сначала пробуем папку Downloads — файл
    оттуда видно в файловом менеджере и удобно переслать; не получилось —
    пишем рядом с файлами игры (там же, где hay_save.json). Ничего не
    открылось — печатаем в stderr.
    """
    stamp = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    block = "===== {} =====\n{}\n\n".format(stamp, text.rstrip())
    places = _log_places()
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
    try:
        sys.stderr.write(block)  # на APK stderr бывает закрыт — страховка
    except Exception:
        pass
