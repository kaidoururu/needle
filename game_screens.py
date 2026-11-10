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
