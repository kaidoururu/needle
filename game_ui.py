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
