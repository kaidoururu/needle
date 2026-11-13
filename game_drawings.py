# -*- coding: utf-8 -*-
# Рисунки: находки и иконки лавки

import math
import random
import pygame

from game_config import *


class DrawingsMixin:
    """Рисунки: находки и иконки лавки"""


    # ---------- рисунки находок ----------
    def _cached_draw(self, name, surf, cx, cy, d, alpha, builder):
        cache = getattr(self, "_dr_cache", None)
        if cache is None:
            cache = self._dr_cache = {}
        key = (name, d)
        img = cache.get(key)
        if img is None:
            img = pygame.Surface((d, d), pygame.SRCALPHA)
            builder(img, d // 2, d // 2, d, None)
            cache[key] = img
        px, py = int(cx - d // 2), int(cy - d // 2)
        if alpha is None:
            surf.blit(img, (px, py))
        else:
            surf.blit(self._alpha_copy(name, img, alpha), (px, py))

    # ---------- общий кэш прозрачности (пункт 4) ----------
    def _alpha_index(self, alpha):
        return max(0, min(7, int(alpha) * 8 // 256))

    def _alpha_copy(self, name, img, alpha):
        cache = getattr(self, "_alpha_cache", None)
        if cache is None:
            cache = self._alpha_cache = {}
        idx = self._alpha_index(alpha)
        key = (name, idx)
        cp = cache.get(key)
        if cp is None:
            cp = img.copy()
            cp.set_alpha(int(255 * (idx + 1) / 8))
            cache[key] = cp
        return cp

    def draw_stone(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_stone", surf, cx, cy, d, alpha, self._build_draw_stone)

    def _build_draw_stone(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        rock = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(rock, (60, 60, 66), (r, r + r // 6), r)
        pygame.draw.circle(rock, STONE_GRAY, (r, r - r // 10),
                           int(r * 0.88))
        pygame.draw.circle(rock, (185, 185, 190),
                           (r - r // 3, r - r // 3), int(r * 0.28))
        pygame.draw.arc(rock, (90, 90, 96), (r // 4, r // 4,
                                             d - r // 2, d - r // 2),
                        2.6, 4.6, max(2, r // 8))
        if alpha is not None:
            rock.set_alpha(alpha)
        surf.blit(rock, (int(cx - r), int(cy - r)))



    def draw_plant(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_plant", surf, cx, cy, d, alpha, self._build_draw_plant)

    def _build_draw_plant(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        pl = pygame.Surface((d, d), pygame.SRCALPHA)
        cxx, cyy = int(r), int(r)
        pygame.draw.line(pl, PLANT_GREEN,
                         (cxx, int(cyy + r * 0.9)), (cxx, int(cyy - r * 0.2)),
                         max(3, r // 6))
        pygame.draw.line(pl, PLANT_GREEN,
                         (cxx, int(cyy + r * 0.3)),
                         (int(cxx - r * 0.6), int(cyy + r * 0.05)),
                         max(3, r // 8))
        pygame.draw.line(pl, PLANT_GREEN,
                         (cxx, int(cyy + r * 0.5)),
                         (int(cxx + r * 0.6), int(cyy + r * 0.25)),
                         max(3, r // 8))
        for k in (-0.1, 0.2):
            pygame.draw.line(pl, PLANT_GREEN,
                             (cxx, int(cyy + r * k)),
                             (int(cxx - r * 0.18), int(cyy + r * (k - 0.12))),
                             max(2, r // 10))
        fr = int(r * 0.42)
        for ang in range(0, 360, 60):
            rad = math.radians(ang)
            fx = cxx + int(math.cos(rad) * fr)
            fy = cyy - int(r * 0.35) + int(math.sin(rad) * fr)
            pygame.draw.circle(pl, PLANT_FLOWER, (fx, fy), max(3, fr // 2))
        pygame.draw.circle(pl, (255, 220, 90),
                           (cxx, cyy - int(r * 0.35)), max(2, fr // 3))
        if alpha is not None:
            pl.set_alpha(alpha)
        surf.blit(pl, (int(cx - r), int(cy - r)))



    def draw_animal(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_animal", surf, cx, cy, d, alpha, self._build_draw_animal)

    def _build_draw_animal(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        an = pygame.Surface((d, d), pygame.SRCALPHA)
        cxx, cyy = int(r), int(r)
        pad_w, pad_h = int(r * 0.9), int(r * 0.7)
        pygame.draw.ellipse(an, ANIMAL_BROWN,
                            (cxx - pad_w // 2, cyy, pad_w, pad_h))
        toe_r = max(3, r // 5)
        for tx, ty in ((-0.55, -0.45), (0, -0.62), (0.55, -0.45)):
            pygame.draw.circle(an, ANIMAL_BROWN,
                               (int(cxx + tx * r), int(cyy + ty * r)), toe_r)
        for k in (-1, 0, 1):
            pygame.draw.line(an, (230, 70, 70),
                             (int(cxx + k * r * 0.5), int(cyy - r * 0.8)),
                             (int(cxx + k * r * 0.4), int(cyy + r * 0.9)),
                             max(2, r // 10))
        if alpha is not None:
            an.set_alpha(alpha)
        surf.blit(an, (int(cx - r), int(cy - r)))



    def draw_bandage(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_bandage", surf, cx, cy, d, alpha, self._build_draw_bandage)

    def _build_draw_bandage(self, surf, cx, cy, d, alpha=None):
        """Рулон бинта: белый цилиндр, торец со спиралью,
        свисающий хвостик и красный крест."""
        r = d // 2
        bd = pygame.Surface((d, d), pygame.SRCALPHA)

        body_h = int(d * 0.56)
        body_w = int(d * 0.66)
        bx = int(d * 0.06)
        by = (d - body_h) // 2
        corner = max(3, body_h // 4)

        tail = pygame.Rect(bx + body_w - body_h // 3,
                           by + body_h - 4,
                           int(d * 0.30), int(d * 0.20))
        pygame.draw.rect(bd, (238, 235, 228), tail,
                         border_radius=max(3, d // 16))
        pygame.draw.rect(bd, (196, 192, 184), tail, max(2, d // 30),
                         border_radius=max(3, d // 16))

        body = pygame.Rect(bx, by, body_w, body_h)
        pygame.draw.rect(bd, (252, 250, 245), body, border_radius=corner)
        pygame.draw.rect(bd, (192, 188, 180), body, max(2, d // 26),
                         border_radius=corner)
        shade = pygame.Rect(bx + 4, by + body_h - max(3, d // 16),
                            body_w - 8, max(3, d // 16))
        pygame.draw.rect(bd, (226, 222, 214), shade,
                         border_radius=max(2, corner // 2))

        er = body_h // 2
        ecx = bx + er
        ecy = by + body_h // 2
        pygame.draw.circle(bd, (226, 222, 214), (ecx, ecy), er - 1)
        pygame.draw.circle(bd, (188, 184, 176), (ecx, ecy), er - 1,
                           max(2, d // 26))
        pygame.draw.circle(bd, (200, 196, 188), (ecx, ecy),
                           max(2, int(er * 0.62)), max(2, d // 30))
        pygame.draw.circle(bd, (200, 196, 188), (ecx, ecy),
                           max(2, int(er * 0.30)), max(2, d // 30))

        ccx = bx + int(body_w * 0.60)
        ccy = by + body_h // 2
        arm = max(3, d // 9)
        pygame.draw.rect(bd, (206, 58, 58),
                         (ccx - arm // 2, ccy - arm * 2, arm, arm * 4),
                         border_radius=arm // 3)
        pygame.draw.rect(bd, (206, 58, 58),
                         (ccx - arm * 2, ccy - arm // 2, arm * 4, arm),
                         border_radius=arm // 3)

        if alpha is not None:
            bd.set_alpha(alpha)
        surf.blit(bd, (int(cx - r), int(cy - r)))



    def draw_antidote(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_antidote", surf, cx, cy, d, alpha, self._build_draw_antidote)

    def _build_draw_antidote(self, surf, cx, cy, d, alpha=None):
        """Флакон противоядия: стеклянная колба с зелёной жидкостью,
        пробка и белая этикетка с крестом."""
        r = d // 2
        ad = pygame.Surface((d, d), pygame.SRCALPHA)

        cork_w = int(d * 0.30)
        cork_h = int(d * 0.16)
        cork = pygame.Rect(int(d * 0.35), int(d * 0.06), cork_w, cork_h)
        pygame.draw.rect(ad, ANTIDOTE_CORK, cork,
                         border_radius=max(2, d // 14))
        pygame.draw.rect(ad, (130, 90, 42), cork, max(2, d // 30),
                         border_radius=max(2, d // 14))

        neck = pygame.Rect(int(d * 0.40), int(d * 0.20),
                           int(d * 0.20), int(d * 0.12))
        pygame.draw.rect(ad, ANTIDOTE_GLASS, neck)

        flask_r = int(d * 0.28)
        fcx, fcy = d // 2, int(d * 0.60)
        pygame.draw.circle(ad, ANTIDOTE_GLASS, (fcx, fcy), flask_r)
        pygame.draw.circle(ad, (150, 175, 165), (fcx, fcy), flask_r,
                           max(2, d // 26))
        liquid_r = int(flask_r * 0.78)
        pygame.draw.circle(ad, ANTIDOTE_LIQUID,
                           (fcx, fcy + int(d * 0.03)), liquid_r)
        pygame.draw.circle(ad, (245, 252, 248),
                           (fcx - liquid_r // 3, fcy - liquid_r // 3),
                           max(2, liquid_r // 4))

        lbl = pygame.Rect(fcx - int(d * 0.17), fcy - int(d * 0.10),
                          int(d * 0.34), int(d * 0.20))
        pygame.draw.rect(ad, (250, 248, 240), lbl,
                         border_radius=max(2, d // 20))
        arm = max(2, d // 16)
        pygame.draw.rect(ad, ANTIDOTE_LIQUID,
                         (lbl.centerx - arm // 2, lbl.centery - arm,
                          arm, arm * 2))
        pygame.draw.rect(ad, ANTIDOTE_LIQUID,
                         (lbl.centerx - arm, lbl.centery - arm // 2,
                          arm * 2, arm))

        if alpha is not None:
            ad.set_alpha(alpha)
        surf.blit(ad, (int(cx - r), int(cy - r)))

    # ---------- пучок сена для плашки HUD ----------

    def draw_hay_bunch(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_hay_bunch", surf, cx, cy, d, alpha, self._build_draw_hay_bunch)

    def _build_draw_hay_bunch(self, surf, cx, cy, d, alpha=None):
        """Пучок сена: охапка соломинок, перевязанная жгутом."""
        r = d // 2
        hb = pygame.Surface((d, d), pygame.SRCALPHA)

        body_w = int(d * 0.68)
        body_h = int(d * 0.62)
        bx = (d - body_w) // 2
        by = int(d * 0.20)
        corner = max(3, d // 10)

        # торчащие кончики соломинок сверху и снизу
        n = 5
        for i in range(n):
            fx = bx + (body_w - max(2, d // 20)) * i // max(1, n - 1)
            pygame.draw.line(hb, (200, 152, 42),
                             (fx + d // 40, by + body_h // 3),
                             (fx, by - int(d * 0.06)), max(2, d // 22))
            pygame.draw.line(hb, (200, 152, 42),
                             (fx + d // 40, by + body_h - body_h // 4),
                             (fx, by + body_h + int(d * 0.06)),
                             max(2, d // 22))

        body = pygame.Rect(bx, by, body_w, body_h)
        pygame.draw.rect(hb, (205, 155, 45), body, border_radius=corner)
        # соломинки внутри пучка
        step = max(4, d // 12)
        for x in range(bx + step // 2, bx + body_w - 2, step):
            pygame.draw.line(hb, ICON_HAY, (x, by + 2),
                             (x - max(1, d // 30), by + body_h - 2),
                             max(2, d // 24))
        pygame.draw.rect(hb, (150, 105, 30), body, max(2, d // 26),
                         border_radius=corner)

        # жгут-перевязь
        tie_h = max(4, d // 8)
        tie = pygame.Rect(bx - max(1, d // 24),
                          by + body_h // 2 - tie_h // 2,
                          body_w + max(2, d // 12), tie_h)
        pygame.draw.rect(hb, (150, 100, 40), tie,
                         border_radius=max(2, d // 24))
        pygame.draw.rect(hb, (110, 72, 26), tie, max(2, d // 28),
                         border_radius=max(2, d // 24))

        if alpha is not None:
            hb.set_alpha(alpha)
        surf.blit(hb, (int(cx - r), int(cy - r)))

    # ---------- иконки лавки ----------



    # ---------- иконки лавки ----------
    def shop_icon(self, key, size=110):
        cache_key = (key, size)
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2
        s = size

        if key == "shovel":
            handle = pygame.Rect(int(s * 0.28), int(s * 0.07),
                                 int(s * 0.44), int(s * 0.09))
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD, handle,
                             border_radius=max(3, s // 20))
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD_DARK, handle,
                             max(2, s // 30), border_radius=max(3, s // 20))
            shaft = pygame.Rect(int(s * 0.47), int(s * 0.13),
                                int(s * 0.07), int(s * 0.37))
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD, shaft)
            pygame.draw.rect(surf, ICON_SHOVEL_WOOD_DARK, shaft,
                             max(2, s // 30))
            pygame.draw.line(surf, (200, 150, 90),
                             (int(s * 0.485), int(s * 0.15)),
                             (int(s * 0.485), int(s * 0.47)),
                             max(2, s // 40))
            collar = pygame.Rect(int(s * 0.42), int(s * 0.48),
                                 int(s * 0.16), int(s * 0.08))
            pygame.draw.rect(surf, (112, 114, 124), collar,
                             border_radius=max(2, s // 30))
            blade_pts = [(int(s * 0.35), int(s * 0.55)),
                         (int(s * 0.65), int(s * 0.55)),
                         (int(s * 0.63), int(s * 0.80)),
                         (int(s * 0.50), int(s * 0.93)),
                         (int(s * 0.37), int(s * 0.80))]
            pygame.draw.polygon(surf, ICON_SHOVEL_METAL, blade_pts)
            pygame.draw.polygon(surf, ICON_SHOVEL_METAL_DARK, blade_pts,
                                max(2, s // 28))
            pygame.draw.line(surf, ICON_SHOVEL_SHINE,
                             (int(s * 0.41), int(s * 0.59)),
                             (int(s * 0.44), int(s * 0.78)),
                             max(2, s // 26))
        elif key == "cap":
            body = pygame.Rect(int(size * 0.22), int(size * 0.30),
                               int(size * 0.56), int(size * 0.46))
            pygame.draw.rect(surf, (90, 90, 96), body,
                             border_radius=max(3, size // 16))
            pygame.draw.rect(surf, (90, 90, 96),
                             (int(size * 0.42), int(size * 0.22),
                              int(size * 0.16), int(size * 0.08)))
            seg_w = int(body.w // 3) - 4
            for i in range(2):
                seg = pygame.Rect(body.x + 4 + i * (seg_w + 4),
                                  body.y + 4, seg_w, body.h - 8)
                pygame.draw.rect(surf, ICON_BATTERY, seg,
                                 border_radius=max(2, size // 22))
        elif key == "regen":
            pts = [(int(size * 0.56), int(size * 0.10)),
                   (int(size * 0.28), int(size * 0.56)),
                   (int(size * 0.48), int(size * 0.56)),
                   (int(size * 0.40), int(size * 0.92)),
                   (int(size * 0.72), int(size * 0.42)),
                   (int(size * 0.52), int(size * 0.42))]
            pygame.draw.polygon(surf, ICON_BOLT, pts)
            pygame.draw.lines(surf, (200, 160, 30), False, pts,
                              max(2, size // 40))
        elif key == "price":
            pygame.draw.circle(surf, (150, 100, 40),
                               (c, int(size * 0.60)), int(size * 0.30))
            pygame.draw.circle(surf, (180, 130, 55),
                               (c, int(size * 0.60)), int(size * 0.30),
                               max(2, size // 30))
            pygame.draw.ellipse(surf, (170, 120, 50),
                                (int(c - size * 0.14), int(size * 0.22),
                                 int(size * 0.28), int(size * 0.14)))
            a = max(3, size // 14)
            pygame.draw.line(surf, ICON_COIN,
                             (int(c - size * 0.13), int(size * 0.56)),
                             (int(c + size * 0.13), int(size * 0.56)), a)
            pygame.draw.line(surf, ICON_COIN,
                             (int(c - size * 0.13), int(size * 0.68)),
                             (int(c + size * 0.13), int(size * 0.68)), a)
            pygame.draw.line(surf, ICON_COIN,
                             (c, int(size * 0.46)),
                             (c, int(size * 0.78)), a)
        elif key == "health":
            r = int(size * 0.22)
            surf_h = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(surf_h, ICON_HEART,
                               (int(c - r * 0.9), int(size * 0.42)), r)
            pygame.draw.circle(surf_h, ICON_HEART,
                               (int(c + r * 0.9), int(size * 0.42)), r)
            pygame.draw.polygon(
                surf_h, ICON_HEART,
                [(int(c - r * 1.85), int(size * 0.50)),
                 (int(c + r * 1.85), int(size * 0.50)),
                 (int(c), int(size * 0.88))])
            arm = max(3, size // 14)
            pygame.draw.rect(surf_h, (250, 245, 240),
                             (c - arm // 2, int(size * 0.40),
                              arm, int(size * 0.26)),
                             border_radius=arm // 3)
            pygame.draw.rect(surf_h, (250, 245, 240),
                             (int(c - size * 0.10), int(size * 0.50),
                              int(size * 0.20), arm),
                             border_radius=arm // 3)
            surf.blit(surf_h, (0, 0))
        elif key == "bnd":
            self.draw_bandage(surf, int(s * 0.38), c, int(s * 0.66))
            self.draw_antidote(surf, int(s * 0.74), int(s * 0.62),
                               int(s * 0.52))
        elif key == "compass":
            self.draw_compass(surf, c, c, s)
        elif key == "energy":
            self.draw_energy(surf, c, c, s)
        elif key == "clover":
            self.draw_clover(surf, c, c, s)

        self.icon_cache[cache_key] = surf
        return surf

    # ---------- кэш картинки стога ----------


    def draw_compass(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_compass", surf, cx, cy, d, alpha, self._build_draw_compass)

    def _build_draw_compass(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        cp = pygame.Surface((d, d), pygame.SRCALPHA)
        pygame.draw.circle(cp, (70, 60, 40), (r, r), r)
        pygame.draw.circle(cp, (235, 220, 185), (r, r), int(r * 0.86))
        pygame.draw.circle(cp, (70, 60, 40), (r, r), int(r * 0.62))
        pygame.draw.line(cp, (60, 70, 190),
                         (r, r - int(r * 0.55)), (r, r + int(r * 0.1)),
                         max(3, r // 5))
        pygame.draw.line(cp, (200, 60, 50),
                         (r, r + int(r * 0.55)), (r, r - int(r * 0.1)),
                         max(3, r // 5))
        pygame.draw.circle(cp, (240, 230, 200), (r, r), max(2, r // 5))
        if alpha is not None:
            cp.set_alpha(alpha)
        surf.blit(cp, (int(cx - r), int(cy - r)))



    def draw_energy(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_energy", surf, cx, cy, d, alpha, self._build_draw_energy)

    def _build_draw_energy(self, surf, cx, cy, d, alpha=None):
        """Энергетик: банка с молнией. Во время действия рывки не
        тратят силу (ENERGY_TIME секунд)."""
        r = d // 2
        en = pygame.Surface((d, d), pygame.SRCALPHA)
        # корпус банки: скруглённый прямоугольник с тёмной окантовкой
        cw, ch = int(r * 0.9), int(r * 1.5)
        x0, y0 = r - cw // 2, r - ch // 2
        pygame.draw.rect(en, ENERGY_CAN, (x0, y0, cw, ch),
                         border_radius=max(3, cw // 4))
        pygame.draw.rect(en, ENERGY_EDGE, (x0, y0, cw, ch),
                         max(2, r // 14), border_radius=max(3, cw // 4))
        # светлые полоски крышки сверху и донышка снизу
        stripe = max(3, ch // 14)
        pygame.draw.rect(en, (240, 232, 210),
                         (x0 + 2, y0 + stripe // 2 + 2, cw - 4, stripe))
        pygame.draw.rect(en, (240, 232, 210),
                         (x0 + 2, y0 + ch - stripe // 2 - 2 - stripe,
                          cw - 4, stripe))
        # молния по центру банки
        pts = [(r + int(cw * 0.20), y0 + int(ch * 0.24)),
               (r - int(cw * 0.30), y0 + int(ch * 0.54)),
               (r - int(cw * 0.06), y0 + int(ch * 0.56)),
               (r - int(cw * 0.20), y0 + int(ch * 0.78)),
               (r + int(cw * 0.30), y0 + int(ch * 0.44)),
               (r + int(cw * 0.06), y0 + int(ch * 0.42))]
        pygame.draw.polygon(en, ICON_BOLT, pts)
        pygame.draw.lines(en, ENERGY_EDGE, False, pts,
                          max(2, r // 16))
        if alpha is not None:
            en.set_alpha(alpha)
        surf.blit(en, (int(cx - r), int(cy - r)))



    def draw_clover(self, surf, cx, cy, d, alpha=None):
        return self._cached_draw("draw_clover", surf, cx, cy, d, alpha, self._build_draw_clover)

    def _build_draw_clover(self, surf, cx, cy, d, alpha=None):
        r = d // 2
        cl = pygame.Surface((d, d), pygame.SRCALPHA)
        lr = int(r * 0.42)
        for dx, dy in ((-lr, -lr // 3), (lr, -lr // 3), (0, lr // 2)):
            pygame.draw.circle(cl, (60, 150, 70), (r + dx, r + dy), lr)
        pygame.draw.line(cl, (40, 110, 50),
                         (r, r + lr), (r, r + r - 2), max(3, r // 8))
        if alpha is not None:
            cl.set_alpha(alpha)
        surf.blit(cl, (int(cx - r), int(cy - r)))
