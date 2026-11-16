# -*- coding: utf-8 -*-
# Интерфейс: HUD, кнопки, полосы здоровья и сил, монеты,
# крутящиеся значки бонусов, подсказка простоя (обучение)

import math
import random
import pygame

from game_config import *


class UIMixin:
    """Интерфейс: HUD, кнопки, полосы, значки бонусов, подсказки"""


    # ---------- геометрия интерфейса ----------
    def build_ui(self):
        w, h = self.screen.get_size()
        hud_top = h - S(HUD_H)
        bw = (w - S(32)) // 3
        self.main_buttons = {
            "sell": pygame.Rect(S(8), hud_top + S(196), bw, S(60)),
            "shop": pygame.Rect(bw + S(16), hud_top + S(196), bw, S(60)),
            "next": pygame.Rect(2 * bw + S(24), hud_top + S(196), bw, S(60)),
        }
        self.bandage_btn = pygame.Rect(w - S(134), hud_top + S(98),
                                       S(92), S(56))
        self.antidote_btn = pygame.Rect(w - S(234), hud_top + S(98),
                                        S(92), S(56))
        self.help_button = pygame.Rect(w - S(300), hud_top + S(96),
                                       S(58), S(58))
        self.pause_button = pygame.Rect(w - S(370), hud_top + S(96),
                                        S(58), S(58))
        self.intro_button = pygame.Rect(0, 0, 0, 0)

        self.shop_panel_h = min(S(SHOP_H), h)
        self.shop_panels = []
        self.shop_buttons = {}
        keys = ("shovel", "cap", "regen", "price", "health", "bnd")
        for i, key in enumerate(keys):
            panel = pygame.Rect(
                S(12), S(SHOP_TOP) + i * (S(SHOP_PANEL_H) + S(SHOP_GAP)),
                w - S(24), S(SHOP_PANEL_H))
            if panel.bottom > self.shop_panel_h - S(84):
                break
            self.shop_panels.append((key, panel))
            self.shop_buttons["buy_" + key] = pygame.Rect(
                panel.right - S(210), panel.y + S(34), S(196), S(52))
        self.shop_buttons["close"] = pygame.Rect(
            w // 2 - S(180), self.shop_panel_h - S(72), S(360), S(58))

        self.help_panel_h = min(S(HELP_H), h)
        self.help_surf = None



    def shop_offset(self):
        return int(self.shop_panel_h * self.shop_slide)



    def help_offset(self):
        return int(self.help_panel_h * self.help_slide)

    # ---------- вспомогательная отрисовка ----------



    def draw_button(self, rect, text, enabled=True, ok=False, next_btn=False):
        hovered = rect.collidepoint(touch_pos(pygame.mouse.get_pos()))
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



    def draw_bar(self, bar, ratio, label_text="", fixed_color=None):
        # r30: параметр pulse и sin-переливание удалены (план r28, точка a):
        # полоска рисуется постоянным цветом, при низком значении не мигает
        fill_w = int(bar.w * ratio)

        if fixed_color is not None:
            r, g, b = fixed_color
        else:
            if ratio > 0.5:
                t = (1.0 - ratio) * 2.0
                r, g, b = int(80 + 175 * t), int(200 - 30 * t), 60
            else:
                t = ratio * 2.0
                r, g, b = 255, int(60 + 140 * t), 60

        pygame.draw.rect(self.screen, (70, 55, 35), bar, border_radius=5)
        if fill_w > 0:
            fill = pygame.Rect(bar.x + S(2), bar.y + S(2),
                               max(S(4), fill_w - S(4)), bar.h - S(4))
            pygame.draw.rect(self.screen, (r, g, b), fill,
                             border_radius=5)
            shine = pygame.Rect(fill.x, fill.y, fill.w,
                                max(S(2), fill.h // 3))
            pygame.draw.rect(self.screen,
                             (min(255, r + 60), min(255, g + 50),
                              min(255, b + 40)), shine, border_radius=4)
        pygame.draw.rect(self.screen, (30, 20, 10), bar, 2,
                         border_radius=5)
        label = self.txt(label_text, self.font_small)
        self.screen.blit(label, label.get_rect(center=bar.center))



    def draw_coin(self, surf, cx, cy, d, alpha=None):
        cache = getattr(self, "_coin_cache", None)
        if cache is None:
            cache = self._coin_cache = {}
        img = cache.get(d)
        if img is None:
            img = pygame.Surface((d, d), pygame.SRCALPHA)
            self._build_coin(img, d // 2, d // 2, d, None)
            img = img.convert_alpha()
            cache[d] = img
        px, py = int(cx - d // 2), int(cy - d // 2)
        if alpha is None:
            surf.blit(img, (px, py))
        else:
            surf.blit(self._alpha_copy("coin", img, alpha), (px, py))

    def _build_coin(self, surf, cx, cy, d, alpha=None):
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
        hovered = rect.collidepoint(touch_pos(pygame.mouse.get_pos()))
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
        hud_top = h - S(HUD_H)
        pygame.draw.rect(self.screen, HUD_BG, (0, hud_top, w, S(HUD_H)))
        pygame.draw.rect(self.screen, PANEL_EDGE, (0, hud_top, w, S(4)))

        hud_text = "Уровень: %d" % self.level
        self.screen.blit(self.txt(hud_text, self.font_small),
                         (S(10), hud_top + S(10)))

        self.draw_bar(pygame.Rect(S(10), hud_top + S(38), w - S(20),
                                  S(24)),
                      self.stamina / self.max_stamina,
                      fixed_color=STAMINA_BLUE, label_text="Силы")

        if self.poison_time > 0:
            health_label = "Здоровье: ОТРАВЛЕНИЕ!"
            color = POISON_PURPLE
        else:
            health_label = "Здоровье"
            color = HEALTH_RED
        self.draw_bar(pygame.Rect(S(10), hud_top + S(70), w - S(20),
                                  S(24)),
                      max(0.0, self.health) / self.max_health,
                      fixed_color=color,
                      label_text=health_label)

        self.draw_button(self.main_buttons["sell"],
                         "Продать сено (+%d)" % self.hay_value,
                         self.hay > 0)
        shop_rect = self.main_buttons["shop"]
        self.draw_button(shop_rect, "Лавка улучшений")
        # подсветка лавки (пункт 8): когда денег хватает хотя бы на одно
        # улучшение, кнопка подсвечивается золотой рамкой — тем же
        # языком, что и подсказка простоя. Под открытой лавкой и на
        # экранах победы/смерти подсветка не нужна.
        if (self.state == "game" and not self.won and not self.dead
                and self.shop_slide <= 0.5
                and self.any_upgrade_affordable()):
            # r36: постоянная рамка вместо мигания — без анимации
            self._alpha_frame(shop_rect.inflate(S(12), S(12)), 12, S(4),
                              SHOP_BTN_ALPHA)

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
        self.draw_hud_chips()

    # ---------- плашки HUD: монеты и сено ----------

    def draw_hud_chips(self):
        """Плашки с рисунками: монета и пучок сена слева от паузы «II»
        (значки бонусов из шага 7 стоят у самой паузы — плашки встанут
        левее них). На узких экранах прячутся."""
        w = self.screen.get_width()
        if w < S(HUD_CHIP_MIN_W):
            return
        pb = self.pause_button
        cy = pb.centery
        chip_h = S(44)
        pad = S(8)
        gap = S(8)
        icon_d = S(28)
        # запас под значки бонусов из шага 7 (до 3 штук при d=52):
        # те же константы, что и в draw_bonus_icons, — через S()
        reserve = S(34 + 2 * (52 + 12) + 26 + 10)
        right_edge = pb.left - reserve

        chips = []
        for kind, num in (("coin", str(self.money)), ("hay", str(self.hay))):
            num_surf = self.txt(num, self.font_small)
            cw = pad + icon_d + 6 + num_surf.get_width() + pad
            chips.append((kind, num_surf, cw))
        total = sum(c[2] for c in chips) + gap * (len(chips) - 1)
        x = max(S(10), right_edge - total)

        for kind, num_surf, cw in chips:
            rect = pygame.Rect(int(x), int(cy - chip_h // 2),
                               int(cw), chip_h)
            pygame.draw.rect(self.screen, (25, 18, 10), rect,
                             border_radius=10)
            pygame.draw.rect(self.screen, (255, 200, 60), rect, 2,
                             border_radius=10)
            icx = rect.x + pad + icon_d // 2
            if kind == "coin":
                self.draw_coin(self.screen, icx, rect.centery, icon_d)
            else:
                self.draw_hay_bunch(self.screen, icx, rect.centery, icon_d)
            self.screen.blit(
                num_surf,
                (rect.x + pad + icon_d + 6,
                 rect.centery - num_surf.get_height() // 2))
            x += cw + gap

    # ---------- кнопка паузы ----------

    def draw_pause_button(self):
        rect = self.pause_button
        hovered = rect.collidepoint(touch_pos(pygame.mouse.get_pos()))
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
        if self.energy_time > 0:
            icons.append(("energy", self.energy_time / ENERGY_TIME))
        if self.clover_time > 0:
            icons.append(("clover", self.clover_time / CLOVER_TIME))
        if not icons:
            return
        # значки в HUD: слева от кнопки паузы «II», по центру ряда кнопок
        pb = self.pause_button
        d = S(52)
        # если слева от паузы не хватает места — уменьшаем значки
        while d > S(28):
            need = S(34) + (len(icons) - 1) * (d + S(12)) + d // 2
            if pb.left - need >= S(10):
                break
            d -= S(4)
        for k, (name, frac) in enumerate(icons):
            cx = pb.left - S(34) - k * (d + S(12))
            cy = pb.centery
            ring = getattr(self, "_ring_cache", {}).get(d)
            if ring is None:
                ring = pygame.Surface((d + 16, d + 16), pygame.SRCALPHA)
                pygame.draw.circle(ring, (25, 18, 10, 205),
                                   ((d + 16) // 2, (d + 16) // 2),
                                   (d + 16) // 2)
                pygame.draw.circle(ring, (255, 200, 60, 235),
                                   ((d + 16) // 2, (d + 16) // 2),
                                   (d + 16) // 2, 3)
                if not hasattr(self, "_ring_cache"):
                    self._ring_cache = {}
                ring = ring.convert_alpha()
                self._ring_cache[d] = ring
            self.screen.blit(ring, (int(cx - (d + 16) / 2),
                                    int(cy - (d + 16) / 2)))
            icon = self.icon_cache.get((name, d))
            if icon is None:
                icon = self.shop_icon(name, d)
            # r37: поворот кэшируется по ступеням 15 градусов —
            # transform.rotate больше не создаёт поверхность каждый кадр,
            # повторный угол той же иконки берётся готовым из кэша.
            step = int(round((-self.time * 90.0) / 15.0)) % 24
            key = (id(icon), step)
            rot = getattr(self, "_rot_cache", {}).get(key)
            if rot is None:
                rot = pygame.transform.rotate(icon, step * 15.0)
                if not hasattr(self, "_rot_cache"):
                    self._rot_cache = {}
                self._rot_cache[key] = rot
            self.screen.blit(rot, rot.get_rect(center=(int(cx), int(cy))))
            if frac is not None:
                # П.3 r46: дуга прогресса дискретна — 16 ступеней,
                # готовые поверхности лежат в _arc_cache, в кадре один
                # blit. pygame.draw.arc — самый медленный примитив
                # pygame, в кадре он больше не вызывается; при нуле
                # прогресса дуга не блитится вовсе.
                rr = d // 2 + S(7)
                step = int(round(frac * 16.0))
                if step > 0:
                    step = min(step, 16)
                    key = (rr, step)
                    arc = self._arc_cache.get(key)
                    if arc is None:
                        pad = S(3) + 2
                        size = 2 * rr + 2 * pad
                        arc = pygame.Surface((size, size),
                                             pygame.SRCALPHA)
                        pygame.draw.arc(
                            arc, (110, 230, 110),
                            pygame.Rect(pad, pad, 2 * rr, 2 * rr),
                            math.pi / 2,
                            math.pi / 2 + 2 * math.pi * step / 16.0, S(4))
                        arc = arc.convert_alpha()
                        self._arc_cache[key] = arc
                    arc_pos = arc.get_rect(center=(int(cx), int(cy)))
                    self.screen.blit(arc, arc_pos)

    # ---------- обучение простоями (v5-48) ----------
    # Спотлайт-обучение удалено: тьма с вырезом, перерисовка
    # кнопки поверх тьмы и стрелка ушли вместе с полноэкранными
    # заливками. Обучение теперь рисует draw_idle_hint: золотая
    # рамка вокруг цели и плашка с текстом из _gold_pill. Шаги и
    # их порядок — TUT_STEPS в game_config.py, цикл —
    # update_idle_hint в game_loop.py.

    def _gold_pill(self, text):
        """П.1 r44: плашка с золотым текстом собирается один раз
        на пару (текст, ширина экрана) и живёт в кэше _pill_cache.
        В кадре остаётся один blit — без SRCALPHA и рендеров строк."""
        w = self.screen.get_width()
        key = (text, w)
        cache = getattr(self, "_pill_cache", None)
        if cache is None:
            cache = self._pill_cache = {}
        pill = cache.get(key)
        if pill is None:
            lines = wrap_text(text, self.font_mid, w - S(40))
            lh = self.font_mid.get_linesize()
            pill_w = max(self.font_mid.size(ln)[0] for ln in lines) + S(26)
            pill_h = lh * len(lines) + S(16)
            pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pygame.draw.rect(pill, MSG_BG + (230,), pill.get_rect(),
                             border_radius=12)
            pygame.draw.rect(pill, GOLD + (230,), pill.get_rect(), S(2),
                             border_radius=12)
            ty = S(8)
            for ln in lines:
                surf = self.font_mid.render(ln, True, GOLD)
                pill.blit(surf,
                          surf.get_rect(center=(pill_w // 2, ty + lh // 2)))
                ty += lh
            pill = pill.convert_alpha()
            cache[key] = pill
        return pill

    def _alpha_frame(self, rect, radius, width, alpha):
        # r36: рамка с постоянной альфой из кэша поверхностей —
        # ни одного выделения памяти в кадре
        key = (rect.w, rect.h, radius, width)
        cache = getattr(self, "_frame_cache", None)
        if cache is None:
            cache = self._frame_cache = {}
        surf = cache.get(key)
        if surf is None:
            surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            pygame.draw.rect(surf, GOLD, surf.get_rect(), width,
                             border_radius=radius)
            surf = surf.convert_alpha()
            cache[key] = surf
        surf.set_alpha(alpha)
        self.screen.blit(surf, rect)

    # ---------- подсказка простоя ----------

    def draw_idle_hint(self):
        hint = self.idle_hint
        if not hint or self.won or self.dead:
            return
        w = self.screen.get_width()
        # П.1 r44: плашка подсказки из кэша _gold_pill — один blit в кадре
        pill = self._gold_pill(hint["text"])
        y = self.field_rect.top + S(60)
        self.screen.blit(pill, pill.get_rect(center=(w // 2, y)))
        # две дискретные фазы вместо sin-пульсации (r36)
        alpha = HINT_RING_ALPHA[int(self.time * 2.0) % 2]
        target = hint.get("target")
        if target is not None:
            self._alpha_frame(target.inflate(S(16), S(16)), 10, S(4), alpha)
        cell = hint.get("cell")
        if cell is not None:
            x = self.field_rect.x + (cell % self.cols) * self.cw
            yy = self.field_rect.y + (cell // self.cols) * self.ch
            r = pygame.Rect(int(x), int(yy), int(self.cw), int(self.ch))
            self._alpha_frame(r.inflate(S(16), S(16)), 4, S(3), alpha)

    # ---------- приветствие «КАК ИГРАТЬ» ----------

    def _intro_panel(self, w, h):
        """П.2 r45: панель «КАК ИГРАТЬ» целиком — фон, рамка, заголовок
        и строки текста — строится один раз на размер экрана и живёт
        в кэше _intro_cache (чистится в make_fonts). Заголовок и строки
        блитятся внутрь при построении. В кадре остаётся один blit
        панели; кнопка «Понятно!» рисуется поверх отдельно — у неё есть
        наведение."""
        cache = getattr(self, "_intro_cache", None)
        if cache is None:
            cache = self._intro_cache = {}
        panel = cache.get((w, h))
        if panel is not None:
            return panel

        # Брифинг по плану п.20: четыре короткие строки вместо шести.
        # Каждая строка короче ширины панели (~48 знаков) — не переносится.
        texts = [
            "Копайте клетки: в стоге спрятана игла.",
            "Бинт лечит, противоядие снимает отравление.",
            "Сено продавайте, монеты тратьте в лавке.",
            "Нашли иглу — идите дальше. Детали — «?».",
        ]
        pad = S(26)
        line_h = S(40)
        pw = min(S(700), w - S(32))
        max_w = pw - 2 * pad
        rows = []
        for t in texts:
            cur = ""
            for wd in t.split():
                test = (cur + " " + wd).strip()
                if self.font_small.size(test)[0] <= max_w:
                    cur = test
                else:
                    if cur:
                        rows.append(cur)
                    cur = wd
            if cur:
                rows.append(cur)

        ph = S(92) + len(rows) * line_h + S(86)
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (25, 18, 10, 245), panel.get_rect(),
                         border_radius=18)
        pygame.draw.rect(panel, (255, 210, 80, 230), panel.get_rect(),
                         S(4), border_radius=18)
        head = self.txt("КАК ИГРАТЬ", self.font_shop_head, GOLD)
        panel.blit(head, head.get_rect(center=(pw // 2, S(44))))
        for i, row in enumerate(rows):
            row_surf = self.txt(row, self.font_small)
            panel.blit(row_surf, row_surf.get_rect(
                center=(pw // 2, S(92) + i * line_h)))
        panel = panel.convert_alpha()
        cache[(w, h)] = panel
        return panel

    def draw_intro(self):
        """Панель приветствия при каждом входе из меню: суть игры и
        кнопка «Понятно!». Игра на паузе (обновления пропускаются в
        game_loop.run), клики мимо панели блокированы.
        П.2 r45: панель целиком из кэша _intro_panel — в кадре один
        blit и живая кнопка «Понятно!»."""
        if not self.intro_open:
            return
        w, h = self.screen.get_size()
        self.screen.blit(get_dark(w, h, (20, 14, 8, 175)), (0, 0))
        panel = self._intro_panel(w, h)
        pw, ph = panel.get_size()
        px, py = (w - pw) // 2, (h - ph) // 2
        self.screen.blit(panel, (px, py))
        bw, bh = S(300), S(58)
        self.intro_button = pygame.Rect((w - bw) // 2,
                                        py + ph - bh - S(20), bw, bh)
        self.draw_button(self.intro_button, "Понятно!", ok=True)
