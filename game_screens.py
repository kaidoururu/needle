# -*- coding: utf-8 -*-
# Экраны победы и смерти

import math
import random
import pygame

from game_config import *


class ScreensMixin:
    """Экраны победы и смерти"""


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
        pygame.draw.line(self.screen, SILVER, (cx - 40, ny + 30),
                         (cx + 40, ny - 30), 5)
        pygame.draw.circle(self.screen, SILVER, (cx - 40, ny + 30), 8)

        if self.level < MAX_LEVEL:
            level_line = "Открыт уровень %d из %d" % (
                self.level + 1, MAX_LEVEL)
        else:
            level_line = "Бесконечный стог открыт! Дальше — без предела"
        if DEBUG:
            stats = [
                level_line,
                "Рывков лопатой: %d" % self.digs,
                "Монет в кармане: %d" % self.money,
                "Лопата: ур.%d (%d×%d)   Цена сена: +%d%%"
                % (self.shovel, self.dig_side(), self.dig_side(),
                   int((self.price_mult() - 1) * 100)),
                "Здоровье: ур.%d   Бинты: %d/%d   Противоядия: %d/%d"
                % (self.health_lvl, self.bandages, self.bandage_cap(),
                   self.antidotes, self.antidote_cap()),
                "Получен бонус: +%d монет" % self.needle_bonus(),
            ]
        else:
            stats = [
                level_line,
                "Монет в кармане: %d" % self.money,
                "Бинты: %d   Противоядия: %d" % (self.bandages,
                                                 self.antidotes),
            ]
        for i, line in enumerate(stats):
            self.draw_centered(line, self.font_mid,
                               int(h * 0.24) + 110 + i * 42)

        if self.golden_needle:
            self.draw_centered(
                "ЗОЛОТАЯ ИГЛА! Бонус x%d" % GOLD_NEEDLE_BONUS_MULT,
                self.font_mid, int(h * 0.24) + 110 + len(stats) * 42,
                GOLD)

        bw, bh = 300, 60
        y0 = int(h * 0.68)
        r1 = pygame.Rect(cx - bw - 12, y0, bw, bh)
        r2 = pygame.Rect(cx + 12, y0, bw, bh)
        self.win_buttons = {"again": r1, "keep": r2}
        self.draw_button(r1, "Играть снова")
        self.draw_button(r2, "Остаться в стоге")
        if self.level < MAX_LEVEL:
            r3 = pygame.Rect(cx - bw // 2, y0 + bh + 14, bw, bh)
            self.win_buttons["next"] = r3
            self.draw_button(r3, "Следующий уровень ->",
                             next_btn=True)
        else:
            r3 = pygame.Rect(cx - bw // 2, y0 + bh + 14, bw, bh)
            self.win_buttons["next"] = r3
            self.draw_button(r3, "Бесконечный стог ->",
                             next_btn=True)

    # ---------- экран смерти ----------



    # ---------- экран смерти ----------
    def draw_death_screen(self):
        w, h = self.screen.get_size()
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((60, 10, 10, 225))
        self.screen.blit(overlay, (0, 0))

        cx = w // 2
        self.draw_centered("ВЫ УМЕРЛИ",
                           self.font_big, int(h * 0.28), RED)
        lost = int(self.money * (1.0 - DEATH_MONEY_KEEP))
        if DEBUG:
            lines = [
                "Уровень %d: укус сносит %d, яд капает %.1f/сек"
                % (self.level, self.animal_damage(), self.poison_rate()),
                "Потеряно %d%% монет (%d). Сено сохранено."
                % (int((1.0 - DEATH_MONEY_KEEP) * 100), lost),
                "Силы обнулены — придётся ждать восстановления.",
                "Уровень начнётся заново — стог перевёрнут.",
                "Улучшения и сено сохраняются.",
            ]
        else:
            lines = [
                "Потеряно 40% монет. Сено сохранено.",
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

    # ---------- ловушки ----------
