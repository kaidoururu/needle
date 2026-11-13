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
        self.shop_panel_h = min(S(SHOP_H), h)
        ph = self.shop_panel_h
        surf = pygame.Surface((w, ph)).convert()
        surf.fill(SHOP_BG)
        pygame.draw.rect(surf, PANEL_EDGE, (0, 0, w, 4))

        title = self.font_big.render("ЛАВКА УЛУЧШЕНИЙ", True, GOLD)
        surf.blit(title, title.get_rect(center=(w // 2, S(40))))

        for key, panel in self.shop_panels:
            if panel.bottom > ph - S(84):
                continue
            it_title, it_desc = self.shop_item_info(key)
            lvl = {"shovel": self.shovel, "cap": self.cap_lvl,
                   "regen": self.regen_lvl, "price": self.price_lvl,
                   "health": self.health_lvl, "bnd": self.bnd_lvl}[key]
            pygame.draw.rect(surf, PANEL_BG, panel, border_radius=14)
            pygame.draw.rect(surf, PANEL_EDGE, panel, 3, border_radius=14)

            icon = self.shop_icon(key, S(80))
            surf.blit(icon, (panel.x + S(12), panel.y + S(20)))

            heading = "%s   ур. %d" % (it_title, lvl)
            if key == "bnd":
                # у аптеки сразу видно, сколько лечит бинт на этом уровне
                heading += "   лечит %d" % self.bandage_heal()
            surf.blit(self.font_shop_head.render(heading, True, GOLD),
                      (panel.x + S(104), panel.y + S(10)))
            surf.blit(self.font_shop_desc.render(it_desc, True, TEXT),
                      (panel.x + S(104), panel.y + S(58)))

        self.shop_surf = surf
        self.shop_buttons["close"] = pygame.Rect(
            w // 2 - S(180), ph - S(72), S(360), S(58))



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
        row_cy = top + S(SHOP_TOP) - S(46)
        self.draw_coin(self.screen, S(34), row_cy, S(36))
        money_text = self.font_mid.render("Монет: %d" % self.money,
                                          True, GOLD)
        self.screen.blit(money_text,
                         (S(60), row_cy - money_text.get_height() // 2))

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
