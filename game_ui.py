# -*- coding: utf-8 -*-
# Интерфейс: HUD, кнопки, полосы здоровья и сил, монеты

import math
import random
import pygame

from game_config import *


class UIMixin:
    """Интерфейс: HUD, кнопки, полосы здоровья и сил, монеты"""


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
                # пульсирует ТОЛЬКО яркость — цвет не меняется
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

    # ---------- рисунки находок ----------



    def draw_hud(self):
        w, h = self.screen.get_size()
        hud_top = h - HUD_H
        pygame.draw.rect(self.screen, HUD_BG, (0, hud_top, w, HUD_H))
        pygame.draw.rect(self.screen, PANEL_EDGE, (0, hud_top, w, 4))

        if DEBUG:
            hud_text = ("Уровень: %d/%d   Деньги: %d   "
                        "Сено: %d пучков (%d монет)"
                        % (self.level, MAX_LEVEL, self.money,
                           self.hay, self.hay_value))
        else:
            hud_text = ("Уровень: %d/%d   Деньги: %d   Сено: %d пучков"
                        % (self.level, MAX_LEVEL, self.money, self.hay))
        self.screen.blit(self.txt(hud_text, self.font_small),
                         (10, hud_top + 10))

        # полоска сил — всегда синяя
        if DEBUG:
            stamina_label = ("Силы: %d/%d"
                             % (int(self.stamina), int(self.max_stamina)))
        else:
            stamina_label = "Силы"
        self.draw_bar(pygame.Rect(10, hud_top + 38, w - 20, 24),
                      self.stamina / self.max_stamina, pulse=True,
                      fixed_color=STAMINA_BLUE,
                      label_text=stamina_label)

        poisoned = self.poison_time > 0
        if poisoned:
            if DEBUG:
                health_label = (
                    "Здоровье: %d/%d   ОТРАВЛЕНИЕ %d сек (-%.1f/сек)"
                    % (int(max(0, self.health)), int(self.max_health),
                       int(self.poison_time) + 1, self.poison_rate()))
            else:
                health_label = "Здоровье: ОТРАВЛЕНИЕ!"
            self.draw_bar(pygame.Rect(10, hud_top + 70, w - 20, 24),
                          max(0.0, self.health) / self.max_health,
                          pulse=True, fixed_color=POISON_PURPLE,
                          label_text=health_label)
        else:
            if DEBUG:
                health_label = ("Здоровье: %d/%d   Укус зверя: -%d"
                                % (int(max(0, self.health)),
                                   int(self.max_health),
                                   self.animal_damage()))
            else:
                health_label = "Здоровье"
            self.draw_bar(pygame.Rect(10, hud_top + 70, w - 20, 24),
                          max(0.0, self.health) / self.max_health,
                          pulse=True, fixed_color=HEALTH_RED,
                          label_text=health_label)

        if DEBUG:
            hint = ("Лопата ур.%d (%d×%d)   Цена сена +%d%%"
                    % (self.shovel, self.dig_side(), self.dig_side(),
                       int((self.price_mult() - 1) * 100)))
        else:
            hint = "Продавайте сено и прокачивайтесь в лавке"
        self.screen.blit(self.txt(hint, self.font_small),
                         (10, hud_top + 104))

        sell_text = "Продать сено (+%d)" % self.hay_value
        self.draw_button(self.main_buttons["sell"], sell_text,
                         self.hay > 0)
        self.draw_button(self.main_buttons["shop"], "Лавка улучшений")

        if self.level >= MAX_LEVEL:
            next_text = "Макс. уровень"
            self.draw_button(self.main_buttons["next"], next_text,
                             enabled=False)
        elif self.needle_found:
            next_text = "Уровень %d ->" % (self.level + 1)
            self.draw_button(self.main_buttons["next"], next_text,
                             next_btn=True)
        else:
            self.draw_button(self.main_buttons["next"],
                             "Найдите иголку", enabled=False)

        # иконка бинтов
        rect = self.bandage_btn
        can_use = self.bandages > 0 and self.health < self.max_health
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = BTN_OK_HOVER if (hovered and can_use) else (
            BTN_OK if can_use else BTN_DISABLED)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (30, 20, 10), rect, 2,
                         border_radius=10)
        icon_d = rect.h - 10
        self.draw_bandage(self.screen,
                          rect.x + icon_d // 2 + 5,
                          rect.centery, icon_d)
        if DEBUG:
            count_text = "%d/%d" % (self.bandages, self.bandage_cap())
        else:
            count_text = "%d" % self.bandages
        count = self.txt(count_text, self.font_small, TEXT)
        self.screen.blit(count,
                         (rect.x + icon_d + 8,
                          rect.centery - count.get_height() // 2))

        # иконка противоядия
        rect = self.antidote_btn
        can_use = self.antidotes > 0 and self.poison_time > 0
        hovered = rect.collidepoint(pygame.mouse.get_pos())
        color = BTN_OK_HOVER if (hovered and can_use) else (
            BTN_OK if can_use else BTN_DISABLED)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, (30, 20, 10), rect, 2,
                         border_radius=10)
        icon_d = rect.h - 10
        self.draw_antidote(self.screen,
                           rect.x + icon_d // 2 + 5,
                           rect.centery, icon_d)
        if DEBUG:
            count_text = "%d/%d" % (self.antidotes, self.antidote_cap())
        else:
            count_text = "%d" % self.antidotes
        count = self.txt(count_text, self.font_small, TEXT)
        self.screen.blit(count,
                         (rect.x + icon_d + 8,
                          rect.centery - count.get_height() // 2))

    # ---------- выдвижная справка «?» ----------
