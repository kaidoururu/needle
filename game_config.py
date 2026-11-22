# -*- coding: utf-8 -*-
# BUILD: v5-61 (r66: звуки панелей из реальной записи бумаги —
# open_panel.wav и close_panel.wav заменены фрагментами mp3
# «шорох бумаги» (0,74 с нарастающий шорох и 0,48 с сухой щелчок,
# 22050 Гц моно 16 бит, фейды 25 мс, пики 0,82/0,78). Стало играть
# открытие/закрытие лавки и помощи (вызовы уже были) и паузы —
# добавлены play("open_panel") в open_pause() и play("close_panel")
# в «продолжить» и системную «Назад». План r61–r64 оставлен
# без изменений: П.4в пропущен по решению пользователя, П.4г не делан.)
# РАНЕЕ (r65): П.4б плана — update_straws без аллокаций:
# фильтрация соломинок на месте, self.straws сам себе буфер,
# выжившие уплотняются к началу, хвост отрезается; старый вариант
# создавал новый список каждый кадр.)
# РАНЕЕ (r64): П.4а плана — подогрев кэшей плашек: панели всех ширин
# заголовков, заголовки обоих цветов и иконки находок S(110) строятся
# prewarm_notices() после build_ui() до первого кадра; первое
# появление таблички — чистый blit. Константы NOTICE_TITLES/
# NOTICE_GREEN/NOTICE_ITEMS вынесены в game_effects.py, if/elif-
# цепочка иконок заменена getattr-диспетчером.)
# РАНЕЕ (r63): П.3 плана — звуковая оптимизация: poison.wav
# приведён к 22050 Гц моно 16 бит (был 44100/стерео — SDL
# ресемплировал его на лету при каждом проигрывании); после mixer.init
# явно set_num_channels(8). fanfare/poison в OGG НЕ конвертированы —
# по решению пользователя. Билдеры при старте не вызываются: у всех
# ключей SOUND_BUILDERS есть файлы в sounds/.)
# РАНЕЕ (r62): П.2 — свой звук подбора у каждого полезного предмета
# (pick_bandage/pick_antidote/energy/compass/clover); звуки click и
# coin удалены, ui_tick — тихий тик переключателя звука; cash.wav
# (дубликат sell.wav) удалён, покупка играет sell.
# РАНЕЕ (r60): укус — сочный «хрум» (мокрый щелчок челюстей,
# глухой стук закрытия, хлюп мякоти с падающим резонансом 900->310 Гц,
# трещинки, липкий шлепок губ); отравление — человеческий стон:
# голосовой источник 170->72 Гц с вибрато и дрожью через дрейфующие
# форманты «а»->«у» (_sfx_reson), грудной рокот ~27 Гц, хрип по
# толчкам источника, дыхание выдоха. Прошлые шумовые версии r59
# пользователь отклонил: хлюп был «тонким», рык/шум — не живыми.
# Фолбэк-синтез совпадает с WAV-файлами байт в байт.)
# РАНЕЕ (r58): звуки — реальные WAV-файлы + кнопка выключения.
# РАНЕЕ (r58): звуки — реальные WAV-файлы + кнопка выключения.
# 14 wav в папке sounds/ рядом с модулями: dig (рывок лопаты: глухой
# удар, хруст соломинок с отдельными трещинками, выброс сена с
# дрожью), stone (стук и звон металла о камень), bite (щелчок
# челюстей, рык 84 Гц с раскатом 24 Гц), bandage (три взмаха ткани),
# poison (вои с вибрато и тающее шипение), error (глухие «туда-туд»
# вместо писка). Загрузка — в новом модуле game_sounds.py: файл из
# sounds/, при недоступности — фолбэк на синтез SOUND_BUILDERS ниже
# (резерв для APK). Кнопка звука: значок динамика в HUD слева от «II»
# и пятая кнопка панели паузы; настройка sound_on живёт в
# hay_save.json, play() молчит при выключении, toggle_sound — в
# game_core.py.
# РАНЕЕ (r57): звуки событий копания — переделка звуковой части.
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
# ПРЕДЫДУЩИЕ ШАГИ: r57 — см. блок выше, r56 — финальный проход: план звуков завершён,
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








def _sfx_ui_tick():
    # сверхкороткий тихий тик: подтверждение включения звука в меню
    # (заменил «click» из r62: пользователь просил убрать неопределённые звуки)
    return _sfx_tone(1200, 0.06, 0.35, decay=3.0)


def _sfx_compass():
    # компас в кармане: металлический «дзынь» — два расстроенных
    # обертона с долгим затуханием, узнаваемая латунь
    return _sfx_seq(
        _sfx_tone(1568, 0.10, 0.55, decay=1.6),
        _sfx_tone(2093, 0.28, 0.45, decay=3.0),
        _sfx_tone(2794, 0.20, 0.20, decay=3.5),
    )


def _sfx_clover():
    # клевер: мягкий шелест листа и тихий щелчок стебля
    return _sfx_seq(
        _sfx_noise(0.08, 0.35, decay=1.5, lp=0.50),
        _sfx_noise(0.12, 0.25, decay=2.2, lp=0.35),
        _sfx_tone(523, 0.06, 0.20, decay=2.8),
    )


def _sfx_pick_bandage():
    # подбор бинта: лёгкий «шьхп» ткани (звук применения — bandage.wav —
    # остаётся на лечении в game_health.py)
    return _sfx_seq(
        _sfx_tone(0, 0.04, 0.30, shape="noise", decay=1.2),
        _sfx_tone(520, 0.08, 0.25, decay=2.5),
    )


def _sfx_pick_antidote():
    # подбор противоядия: лёгкий стеклянный клин — пузырёк о горлышко
    return _sfx_seq(
        _sfx_tone(1245, 0.05, 0.40, decay=2.0),
        _sfx_tone(1867, 0.10, 0.30, decay=3.0),
    )

def _sfx_sell():
    # шуршание горсти монет при продаже: каскад коротких динь-нот
    # с чуть убывающей громкостью — «монеты сыплются в копилку»
    parts = []
    for i, freq in enumerate((1568, 1319, 1760, 1245, 1568, 1047)):
        parts.append(_sfx_tone(freq, 0.05, 0.65 - i * 0.05, decay=2.5))
    return _sfx_seq(*parts)




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


def _sfx_reson(x, f0, f1, bw):
    """Двухполюсный резонатор: пропускает источник через полосу с
    центром, дрейфующим от f0 к f1 Гц (bw — ширина полосы).
    Возвращает list[float] — строители ниже сводят это в array('h')."""
    n = len(x)
    r = math.exp(-math.pi * bw / SOUND_RATE)
    out = [0.0] * n
    y1 = y2 = 0.0
    for i in range(n):
        f = f0 + (f1 - f0) * i / n
        a1 = 2.0 * r * math.cos(2.0 * math.pi * f / SOUND_RATE)
        y = x[i] + a1 * y1 - r * r * y2
        out[i] = y
        y2 = y1
        y1 = y
    return out


def _sfx_bite():
    # укус (r60): сочный «хрум» — резкий мокрый щелчок сомкнувшихся
    # челюстей, глухой стук закрытия, хлюп мякоти пятью кусками с
    # падающим резонансом 900->310 Гц (так звучит сжимаемая ткань),
    # россыпь трещинок пережёвываемого и липкий шлепок губ с низким
    # «чоком» разлипания. Только шумовая фактура, тонов нет.
    rng = random.Random(601)
    sr = SOUND_RATE
    total = int(0.80 * sr)
    buf = [0.0] * total

    def burst(at, ln, vol, lp, decay=5.0):
        # шумовой всплеск с экспоненциальным спадом в общий буфер
        y = 0.0
        for i in range(ln):
            j = at + i
            if j >= total:
                break
            y += lp * (rng.random() * 2.0 - 1.0 - y)
            buf[j] += y * vol * math.exp(-decay * i / ln)

    # 1) мокрый щелчок челюстей: два ярких широкополосных всплеска
    #    почти без атаки — сразу на громкость
    burst(int(0.004 * sr), int(0.005 * sr), 1.6, 0.95, 6.0)
    burst(int(0.016 * sr), int(0.006 * sr), 1.4, 0.85, 5.0)
    # 2) глухой стук закрытия челюстей: густой низкочастотный удар
    burst(int(0.030 * sr), int(0.045 * sr), 1.5, 0.10, 7.0)
    # 3) хлюп мякоти: пять кусков с падающим резонансом 900->310 Гц
    pos = 0.10
    for k in range(5):
        f = 900.0 - (900.0 - 310.0) * k / 4.0
        dur = 0.09 + 0.02 * (k % 2)
        at = int(pos * sr)
        ln = int(dur * sr)
        x = [rng.random() * 2.0 - 1.0 for _ in range(ln)]
        seg = _sfx_reson(x, f, f * 0.9, 260.0)
        for i in range(ln):
            j = at + i
            if j < total:
                env = math.sin(math.pi * i / ln) ** 1.5 * (1.0 - 0.15 * k)
                buf[j] += seg[i] * env * 0.9
        pos += dur + rng.uniform(0.02, 0.05)
    # 4) трещинки пережёвываемого поверх хлюпа: случайные щелчки шума
    for _ in range(20):
        at = int(rng.uniform(0.10, 0.62) * sr)
        ln = rng.randint(int(0.002 * sr), int(0.008 * sr))
        burst(at, ln, rng.uniform(0.3, 0.8), rng.uniform(0.15, 0.8), 5.0)
    # 5) липкий шлепок губ с низким «чоком» разлипания
    burst(int(0.66 * sr), int(0.02 * sr), 1.2, 0.60, 5.0)
    burst(int(0.68 * sr), int(0.05 * sr), 0.9, 0.08, 6.0)
    # мягкие края 5 мс против щелчков на стыках
    edge = int(0.005 * sr)
    for i in range(edge):
        buf[i] *= i / edge
        buf[total - 1 - i] *= i / edge
    # нормировка: RMS 0.13 (уровень dig), пик не выше 0.95
    rms = math.sqrt(sum(v * v for v in buf) / total)
    g = 0.13 / max(rms, 1e-9)
    peak = max(abs(v) for v in buf)
    if peak * g > 0.95:
        g = 0.95 / peak
    out = array.array("h")
    for v in buf:
        out.append(int(max(-1.0, min(1.0, v * g)) * 32767))
    return out


def _sfx_poison():
    # отравление (r60): человеческий стон — голосовой источник (пила)
    # с падающей высотой 170->72 Гц, вибрато 5 Гц и дрожью высоты,
    # через два дрейфующих формантных резонатора: гласная оседает от
    # «а» к «у». Сверху грудной рокот ~27 Гц, хрип, синхронный с
    # голосовыми толчками, и глухое дыхание выдоха в самом конце.
    # Это не мелодичный тон: источник модулирован и оседает в хрип.
    rng = random.Random(602)
    sr = SOUND_RATE
    dur = 1.5
    total = int(dur * sr)
    # 1) голосовой источник: пила с падающей высотой, вибрато и дрожью
    src = [0.0] * total
    ph = 0.0
    for i in range(total):
        t = i / total
        f0 = 170.0 + (72.0 - 170.0) * (t ** 0.9)
        f0 *= 1.0 + 0.035 * math.sin(2.0 * math.pi * 5.0 * i / sr)
        f0 *= 1.0 + rng.uniform(-0.012, 0.012)
        ph += f0 / sr
        if ph >= 1.0:
            ph -= 1.0
        src[i] = ph * 2.0 - 1.0
    # 2) формантный дрейф «а» -> «у»: две полосы, широкие — голос
    #    живой, а не «звоночный»
    f1 = _sfx_reson(src, 750.0, 330.0, 190.0)
    f2 = _sfx_reson(src, 1250.0, 650.0, 260.0)
    voice = [f1[i] + 0.45 * f2[i] for i in range(total)]
    # 3) огибающая стона: нарастание 0.25 с, спад к концу; грудной
    #    рокот ~27 Гц с медленным дрейфом фазы
    out = [0.0] * total
    for i in range(total):
        t = i / total
        a = min(1.0, t / 0.18) * (1.0 - t) ** 0.55
        rumble = 1.0 + 0.35 * math.sin(
            2.0 * math.pi * 27.0 * i / sr
            + 2.0 * math.sin(2.0 * math.pi * 1.3 * i / sr))
        out[i] = voice[i] * a * rumble * 0.8
    # 4) хрип: шум, отпертый голосовыми толчками (пила высокая на скачке)
    for i in range(total):
        out[i] += (rng.random() * 2.0 - 1.0) * max(0.0, src[i]) * 0.30
    # 5) дыхание выдоха в самом конце: густой шум, затухающий за 0.45 с
    y = 0.0
    for i in range(int(0.45 * sr)):
        j = total - int(0.45 * sr) + i
        y += 0.12 * (rng.random() * 2.0 - 1.0 - y)
        out[j] += y * (1.0 - i / int(0.45 * sr)) * 1.4
    # мягкие края 10 мс
    edge = int(0.010 * sr)
    for i in range(edge):
        out[i] *= i / edge
        out[total - 1 - i] *= i / edge
    # нормировка: RMS 0.11, пик не выше 0.95
    rms = math.sqrt(sum(v * v for v in out) / total)
    g = 0.11 / max(rms, 1e-9)
    peak = max(abs(v) for v in out)
    if peak * g > 0.95:
        g = 0.95 / peak
    res = array.array("h")
    for v in out:
        res.append(int(max(-1.0, min(1.0, v * g)) * 32767))
    return res

# имя звука -> функция-сборщик буфера. Новые звуки (пп. 2–5 плана)
# добавляются сюда одной строкой: builder в словарь, play("имя") в коде.
SOUND_BUILDERS = {
    # фолбэк-синтез: используется, только если WAV-файла в sounds/ нет
    "sell": _sfx_sell,
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
    "ui_tick": _sfx_ui_tick,
    "compass": _sfx_compass,
    "clover": _sfx_clover,
    "pick_bandage": _sfx_pick_bandage,
    "pick_antidote": _sfx_pick_antidote,
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
