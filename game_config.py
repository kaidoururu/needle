# -*- coding: utf-8 -*-
# BUILD: v5-54 (r57: звуки событий копания — переделка звуковой части.
# Новые строители в SOUND_BUILDERS: dig (рывок копания: глухой удар
# лопаты и шелест выброшенного сена), stone (глухой стук, хруст и низкий
# металлический звон по камню), bite (щелчок и низкий рык укуса зверя),
# poison (два нисходящих «воя» и шипение отравления). Вызовы play() в
# game_digging.py переведены на новые звуки: рывок — dig вместо click,
# укус — bite вместо error; камень и растение озвучены впервые. Убран
# двойной error при ловушке (trigger_item + resolve_items) — один звук
# на событие. Движок дополнен шумовым и свип-синтезом: _sfx_noise
# (белый шум с огибающей и однополюсным фильтром) и _sfx_sweep (тон с
# линейной перестройкой частоты). Итого звуков в игре 14.
# ПРЕДЫДУЩИЕ ШАГИ: r56 — финальный проход: план звуков завершён,
# документация в релизном виде; r55 — звуки здоровья и лавки (bandage, antidote,
# open_panel, close_panel); r54 — фикс продолжения (build_field в
# __init__, туториал скрыт при «Продолжить»); r53 — мгновенные таблички;
# r52 — звуки экономики (sell, cash) и фикс array.array (с r41
# звуки молчали — TypeError глотался в _init_audio).


import array
import datetime
import json
import math
import os
import pygame
import random
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
# используются: game_field — HUD_H и CELL_*;
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


# r38: кэш полноэкранных затемнений — SRCALPHA-слой постоянного размера
# и цвета строится один раз, дальше только blit. Ноль пересозданий в кадре.
_screen_dark_cache = {}


def clear_dark_cache():
    """Публичная чистка кэша затемнений: подчёркнутые имена не проходят
    через from game_config import *, поэтому чистка — функцией (r39)."""
    _screen_dark_cache.clear()


def get_dark(w, h, color, tag=""):
    """Кэшированная поверхность-затемнение w×h цвета color (r, g, b, a).

    tag разводит одинаковые цвета разных слоёв по разным ключам.
    """
    key = (tag, w, h, tuple(color))
    surf = _screen_dark_cache.get(key)
    if surf is None:
        surf = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()
        surf.fill(color)
        _screen_dark_cache[key] = surf
    return surf


# ---------- звуки (пункт 1 плана по звукам) ----------
# Звуки не хранятся файлами: они синтезируются при старте из простых
# огибающих — архив и APK не раздуваются, пайплайн ассетов не нужен.
# 22050 Гц моно: для коротких SFX этого хватает на слух, память
# вдвое меньше, чем при 44100.
SOUND_RATE = 22050
SOUND_VOLUME = 0.8  # мастер-громкость всех SFX


def _sfx_tone(freq, dur, vol=1.0, shape="sine", decay=2.0):
    """Один тон с огибающей: фронт 3 мс, степенной спад decay.

    shape: sine — обычный тон; square — «жужжание» для отказов;
    noise — шорох (пригодится для шелеста сена). Возвращает
    array('h') — 16-bit mono в частоте SOUND_RATE.
    """
    n = int(SOUND_RATE * dur)
    arr = array.array("h", bytes(2 * n))
    step = 2.0 * math.pi * freq / SOUND_RATE
    attack = max(1, int(0.003 * SOUND_RATE))
    for i in range(n):
        env = min(1.0, i / attack) * (1.0 - i / n) ** decay
        if shape == "sine":
            v = math.sin(i * step)
        elif shape == "square":
            v = 1.0 if math.sin(i * step) > 0.0 else -1.0
        else:  # noise
            v = random.random() * 2.0 - 1.0
        arr[i] = int(v * env * vol * 32767)
    return arr


def _sfx_seq(*chunks):
    """Склейка тонов подряд: сложные звуки собираются из простых."""
    out = array.array("h")
    for chunk in chunks:
        out.extend(chunk)
    return out


def _sfx_noise(dur, vol=1.0, decay=2.0, lp=0.3):
    """Шумовой импульс: огибающая как у тона + однополюсный фильтр.

    lp — коэффициент сглаживания (0..1): чем меньше, тем гуще и
    «низкочастотнее» шум; 1.0 — чистый белый шорох.
    """
    n = int(SOUND_RATE * dur)
    arr = array.array("h", bytes(2 * n))
    attack = max(1, int(0.003 * SOUND_RATE))
    y = 0.0
    for i in range(n):
        env = min(1.0, i / attack) * (1.0 - i / n) ** decay
        y += lp * (random.random() * 2.0 - 1.0 - y)
        arr[i] = int(y * env * vol * 32767)
    return arr


def _sfx_sweep(f0, f1, dur, vol=1.0, shape="sine", decay=2.0):
    """Тон с линейной перестройкой частоты от f0 к f1 за dur секунд."""
    n = int(SOUND_RATE * dur)
    arr = array.array("h", bytes(2 * n))
    attack = max(1, int(0.003 * SOUND_RATE))
    phase = 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * i / n
        phase += 2.0 * math.pi * f / SOUND_RATE
        env = min(1.0, i / attack) * (1.0 - i / n) ** decay
        if shape == "sine":
            v = math.sin(phase)
        else:
            v = 1.0 if math.sin(phase) > 0.0 else -1.0
        arr[i] = int(v * env * vol * 32767)
    return arr


def _sfx_click():
    return _sfx_tone(880, 0.05, 0.7, decay=3.0)


def _sfx_coin():
    # классическая «двухнотная» игровая монета: B5 -> E6
    return _sfx_seq(
        _sfx_tone(988, 0.07, 0.8),
        _sfx_tone(1319, 0.14, 0.8, decay=1.5),
    )


def _sfx_sell():
    # шуршание горсти монет при продаже: каскад коротких динь-нот
    # с чуть убывающей громкостью — «монеты сыплются в копилку»
    parts = []
    for i, freq in enumerate((1568, 1319, 1760, 1245, 1568, 1047)):
        parts.append(_sfx_tone(freq, 0.05, 0.65 - i * 0.05, decay=2.5))
    return _sfx_seq(*parts)


def _sfx_cash():
    # кассовый звон при покупке: яркий двойной «динь» колокольчика
    # и короткий глухой удар выдвижного ящика в конце
    return _sfx_seq(
        _sfx_tone(1568, 0.09, 0.7, decay=1.8),
        _sfx_tone(2093, 0.15, 0.7, decay=2.0),
        _sfx_tone(140, 0.08, 0.5, shape="square", decay=2.5),
    )


def _sfx_error():
    # глухой писк при отказе: денег не хватает, бинтов нет и т. п.
    return _sfx_seq(
        _sfx_tone(160, 0.09, 0.8, shape="square"),
        _sfx_tone(120, 0.14, 0.7, shape="square", decay=1.5),
    )

def _sfx_bandage():
    # мягкий шелест перевязки: короткий шумовой свист + затихающий шорох
    return _sfx_seq(
        _sfx_tone(0, 0.10, 0.45, shape="noise", decay=1.6),
        _sfx_tone(0, 0.18, 0.30, shape="noise", decay=2.6),
    )


def _sfx_antidote():
    # булькание противоядия: два восходящих «блюпа» с водяной окраской
    return _sfx_seq(
        _sfx_tone(220, 0.10, 0.65, decay=1.2),
        _sfx_tone(330, 0.09, 0.55, decay=1.2),
        _sfx_tone(440, 0.16, 0.60, decay=2.2),
    )


def _sfx_open_panel():
    # «вжух» выдвижения панели лавки/справки: восходящий шорох
    return _sfx_seq(
        _sfx_tone(0, 0.07, 0.35, shape="noise", decay=1.2),
        _sfx_tone(660, 0.07, 0.30, decay=2.0),
    )


def _sfx_close_panel():
    # обратный «вжух» пониже: закрытие панели
    return _sfx_seq(
        _sfx_tone(440, 0.06, 0.30, decay=2.0),
        _sfx_tone(0, 0.07, 0.30, shape="noise", decay=1.2),
    )


def _sfx_fanfare():
    # торжественное арпеджио C5-E5-G5-C6: победа, золотая игла
    return _sfx_seq(*[
        _sfx_tone(f, 0.16, 0.75, decay=1.2)
        for f in (523, 659, 784, 1047)
    ])


def _sfx_dig():
    # рывок копания: глухой удар лопаты и короткий шелест выброшенного
    # сена — вместо прежнего безликого «пика»
    return _sfx_seq(
        _sfx_tone(75, 0.06, 0.8, shape="square", decay=2.2),
        _sfx_noise(0.05, 0.35, decay=1.8, lp=0.6),
        _sfx_noise(0.12, 0.25, decay=2.6, lp=0.25),
    )


def _sfx_stone():
    # камень в стоге: глухой стук, короткий хруст и низкий «дзыньк»
    # металла о камень с затухающим звоном
    return _sfx_seq(
        _sfx_tone(90, 0.10, 0.85, shape="square", decay=2.4),
        _sfx_noise(0.05, 0.30, decay=2.0, lp=0.7),
        _sfx_tone(1150, 0.22, 0.30, decay=3.5),
        _sfx_tone(1710, 0.14, 0.18, decay=3.5),
    )


def _sfx_bite():
    # укус зверя: резкий щелчок челюстей и низкий рык с раскатом
    return _sfx_seq(
        _sfx_noise(0.03, 0.70, decay=3.0, lp=0.8),
        _sfx_sweep(130, 70, 0.22, 0.75, shape="square", decay=1.4),
        _sfx_noise(0.10, 0.25, decay=2.0, lp=0.15),
    )


def _sfx_poison():
    # отравление: два нисходящих «воя» и шипение, тающее в тишину
    return _sfx_seq(
        _sfx_sweep(660, 290, 0.28, 0.55, decay=1.3),
        _sfx_sweep(480, 210, 0.30, 0.45, decay=1.5),
        _sfx_noise(0.22, 0.30, decay=2.4, lp=0.5),
    )


# имя звука -> функция-сборщик буфера. Новые звуки (пп. 2–5 плана)
# добавляются сюда одной строкой: builder в словарь, play("имя") в коде.
SOUND_BUILDERS = {
    "click": _sfx_click,
    "coin": _sfx_coin,
    "sell": _sfx_sell,
    "cash": _sfx_cash,
    "error": _sfx_error,
    "bandage": _sfx_bandage,
    "antidote": _sfx_antidote,
    "open_panel": _sfx_open_panel,
    "close_panel": _sfx_close_panel,
    "fanfare": _sfx_fanfare,
    "dig": _sfx_dig,
    "stone": _sfx_stone,
    "bite": _sfx_bite,
    "poison": _sfx_poison,
}


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
        try:
            with open(os.path.join(data_dir(), "tap_calib.json"),
                      "w", encoding="utf-8") as f:
                json.dump({"lo": lo, "hi": hi}, f)
        except Exception:
            pass


STAMINA_BASE = 20
STAMINA_STEP = 4
REGEN_BASE = 1.2
REGEN_STEP = 1.0
MAX_LEVEL = 10
NEEDLE_BONUS_BASE = 300
SHOP_H = 1000          # высота лавки: 6 панелей + шапка
                       # (1000: панель АПТЕЧКА имеет низ 910, предел 916 — влезает)
HELP_H = 1000   # высота справки: две страницы + кнопки навигации
SHOP_PANEL_H = 120
SHOP_GAP = 10
SHOP_TOP = 140

# плашки HUD (монеты и сено): на экранах уже этого — прячутся
HUD_CHIP_MIN_W = 690

# анимация копания: разлетающиеся соломинки
STRAW_MIN = 3
STRAW_MAX = 6
STRAW_LIFE = 0.7
# усреднённый фон стога (между выкопанной клеткой и недуганной):
# к нему соломинки растворяются цветом вместо прозрачности (r35)
STRAW_FADE_TO = (160, 122, 44)
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
IDLE_HINT_AFTER = 6.0       # сек бездействия до шага обучения

# ---------- обучение простоями (v5-48) ----------
# Шаги обучения: (текст, цель). Цель "cell" — случайная
# некопанная клетка сена; "sell"/"shop" — кнопки main_buttons;
# "bandage"/"antidote" — кнопки-иконки в HUD. Шаги показываются
# строго по очереди, цикл повторяется.
TUT_STEPS = (
    ("В стоге спрятана игла. Копайте клетки!", "cell"),
    ("Продайте сено — получите монеты.", "sell"),
    ("Бинт лечит здоровье. Тап по рулону.", "bandage"),
    ("В лавке покупайте улучшения за монеты.", "shop"),
    ("Противоядие снимает отравление. Тап по флакону.", "antidote"),
)

# подсветка компаса и кнопки лавки (r30/r36)
COMPASS_GLOW_ALPHA = 40
SHOP_BTN_ALPHA = 180
HINT_RING_ALPHA = (200, 90)  # две фазы пульса рамки подсказки

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
