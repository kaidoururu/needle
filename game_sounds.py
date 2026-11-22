# -*- coding: utf-8 -*-
# r58: звуки — реальные WAV-файлы из папки sounds/, лежащей рядом с
# модулями игры. Файлы делали звук копания/бинта/укуса без «пиканья»:
# шумовой синтез с фильтрами, записанный заранее, а не собираемый при
# старте. Если файла нет или микшер его не принял (APK может прятать
# ресурсы) — фолбэк на старый синтез SOUND_BUILDERS из game_config.py.
# r62: грузим ВСЕ *.wav из sounds/ по именам файлов — так energy.wav
# (лежал в sounds/, но не загружался: ключа "energy" в SOUND_BUILDERS
# не было) и любые будущие файлы подхватываются без правок загрузчика.
# Порядок: сначала файлы, потом синтез только для имён без файла;
# не нашлось ни то ни другое — звук просто отсутствует, play() это
# переживает.

import os

import pygame

from game_config import SOUND_BUILDERS

SOUND_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "sounds")


def load_sounds():
    """Загрузить все звуки: все WAV из sounds/ по именам файлов;
    для имён без файла — фолбэк-синтез из SOUND_BUILDERS."""
    sounds = {}
    # 1) реальные файлы: имя без расширения = ключ звука
    try:
        for fname in os.listdir(SOUND_DIR):
            stem, ext = os.path.splitext(fname)
            if ext.lower() != ".wav" or not stem or stem in sounds:
                continue
            try:
                sounds[stem] = pygame.mixer.Sound(
                    os.path.join(SOUND_DIR, fname))
            except Exception:
                pass
    except Exception:
        pass  # папка не видна (APK) — остаётся фолбэк-синтез
    # 2) фолбэк-синтез: только для имён, у которых файла нет
    for name, builder in SOUND_BUILDERS.items():
        if name in sounds:
            continue
        try:
            snd = pygame.mixer.Sound(buffer=bytes(builder()))
        except Exception:
            snd = None
        if snd is not None:
            sounds[name] = snd
    return sounds
