# -*- coding: utf-8 -*-
# Эффекты: сообщения, таблички находок, вспышки, соломинки

import math
import random
import pygame

from game_config import *


class EffectsMixin:
    """Эффекты: сообщения, таблички находок, вспышки, соломинки"""


    # ---------- сообщения и таблички ----------
    def add_message(self, text, color):
        self.messages.append({"text": text, "color": color, "life": 2.6})



    def show_notice(self, item):
        titles = {
            "stone": "КАМЕНЬ!",
            "plant": "ЯДОВИТОЕ РАСТЕНИЕ!",
            "animal": "УКУС ЗВЕРЯ!",
            "bandage": "БИНТ!",
            "antidote": "ПРОТИВОЯДИЕ!",
            "compass": "КОМПАС!",
            "energy": "ЭНЕРГЕТИК!",
            "clover": "КЛЕВЕР!",
        }
        self.notice = {"item": item, "title": titles.get(item, item),
                       "sub": "", "life": NOTICE_TIME}



    def draw_notice(self):
        n = self.notice
        if not n:
            return
        alpha = max(0, min(255, int(255 * min(1.0, n["life"] / 0.5))))
        w, h = self.screen.get_size()
        pw, ph = 460, 260
        px = (w - pw) // 2
        py = self.field_rect.top + (self.field_rect.h - ph) // 2 - 40

        panel = getattr(self, "_notice_panel", None)
        if panel is None:
            panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pygame.draw.rect(panel, (25, 18, 10, 235),
                             (0, 0, pw, ph), border_radius=18)
            pygame.draw.rect(panel, (255, 210, 80, 200),
                             (0, 0, pw, ph), 4, border_radius=18)
            self._notice_panel = panel
        panel.set_alpha(alpha)
        self.screen.blit(panel, (px, py))

        icon_cx = px + pw // 2
        icon_cy = py + 92
        if n["item"] == "stone":
            self.draw_stone(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "plant":
            self.draw_plant(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "animal":
            self.draw_animal(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "bandage":
            self.draw_bandage(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "antidote":
            self.draw_antidote(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "compass":
            self.draw_compass(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "energy":
            self.draw_energy(self.screen, icon_cx, icon_cy, 110, alpha)
        elif n["item"] == "clover":
            self.draw_clover(self.screen, icon_cx, icon_cy, 110, alpha)

        color = GREEN_MSG if n["item"] in ("bandage", "antidote",
                                           "compass", "energy",
                                           "clover") else RED
        t1 = self.font_big.render(n["title"], True, color)
        t1.set_alpha(alpha)
        self.screen.blit(t1, t1.get_rect(center=(w // 2, py + 178)))
        if n["sub"]:
            t2 = self.font_mid.render(n["sub"], True, TEXT)
            t2.set_alpha(alpha)
            self.screen.blit(t2, t2.get_rect(center=(w // 2, py + 226)))



    def draw_messages(self):
        """Сообщения на тёмной плашке — читаются на любом фоне стога."""
        y = self.field_rect.top + 14
        for m in self.messages:
            alpha = max(0, min(255, int(255 * m["life"] / 1.2)))
            surf = self.font_mid.render(m["text"], True, m["color"])
            pad = 10
            pill_w = surf.get_width() + pad * 2
            pill_h = surf.get_height() + pad * 2
            pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
            pygame.draw.rect(pill, MSG_BG + (int(215 * alpha / 255),),
                             (0, 0, pill_w, pill_h), border_radius=10)
            px = self.field_rect.centerx - pill_w // 2
            self.screen.blit(pill, (px, y))
            surf.set_alpha(alpha)
            self.screen.blit(surf, (px + pad, y + pad))
            y += pill_h + 4

    # ---------- экранные вспышки ----------



    # ---------- экранные вспышки ----------
    def draw_screen_effects(self):
        w, h = self.screen.get_size()
        cache = getattr(self, "_fx_cache", None)
        if cache is None:
            cache = self._fx_cache = {}
        def ov_for(rgb):
            key = (w, h, rgb)
            ov = cache.get(key)
            if ov is None:
                ov = pygame.Surface((w, h))
                ov.fill(rgb)
                cache[key] = ov
            return ov
        if self.bite_flash > 0:
            alpha = int(BITE_FLASH_ALPHA * self.bite_flash)
            if alpha > 0:
                ov = ov_for(BITE_RED)
                ov.set_alpha(alpha)
                self.screen.blit(ov, (0, 0))
        if self.poison_flash > 0:
            alpha = int(POISON_FLASH_ALPHA * self.poison_flash)
            if alpha > 0:
                ov = ov_for(POISON_FLASH)
                ov.set_alpha(alpha)
                self.screen.blit(ov, (0, 0))
        elif self.poison_time > 0:
            ov = ov_for(POISON_FLASH)
            ov.set_alpha(POISON_TINT_ALPHA)
            self.screen.blit(ov, (0, 0))
    def update_flashes(self, dt):
        if self.bite_flash > 0:
            self.bite_flash = max(0.0, self.bite_flash - FLASH_FADE * dt)
        if self.poison_flash > 0:
            self.poison_flash = max(0.0, self.poison_flash - FLASH_FADE * dt)

    # ---------- соломинки от копания ----------



    # ---------- соломинки от копания ----------
    def spawn_straws(self, cell_indices):
        for i in cell_indices:
            x = self.field_rect.x + (i % self.cols) * self.cw + self.cw / 2
            y = self.field_rect.y + (i // self.cols) * self.ch + self.ch / 2
            count = random.randint(STRAW_MIN, STRAW_MAX)
            for _ in range(count):
                ang = random.uniform(0, 2 * math.pi)
                speed = STRAW_SPEED * random.uniform(0.4, 1.2)
                self.straws.append({
                    "x": x + random.uniform(-self.cw / 3, self.cw / 3),
                    "y": y + random.uniform(-self.ch / 3, self.ch / 3),
                    "vx": math.cos(ang) * speed,
                    "vy": math.sin(ang) * speed - 70,
                    "ang": random.uniform(0, math.pi),
                    "spin": random.uniform(-9, 9),
                    "len": random.uniform(0.4, 0.8) * min(self.cw, self.ch),
                    "life": STRAW_LIFE * random.uniform(0.7, 1.2),
                    "color": random.choice([(235, 191, 64), (250, 214, 96),
                                            (210, 165, 50)]),
                })



    def update_straws(self, dt):
        alive = []
        for s in self.straws:
            s["life"] -= dt
            if s["life"] <= 0:
                continue
            s["vy"] += STRAW_GRAVITY * dt
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            s["ang"] += s["spin"] * dt
            alive.append(s)
        self.straws = alive



    def draw_straws(self):
        for s in self.straws:
            alpha = max(0, min(255,
                               int(255 * s["life"] / (STRAW_LIFE * 0.6))))
            half = s["len"] / 2
            dx = math.cos(s["ang"]) * half
            dy = math.sin(s["ang"]) * half
            color = s["color"]
            if alpha < 255:
                surf = pygame.Surface(
                    (int(abs(dx) * 2) + 4, int(abs(dy) * 2) + 4),
                    pygame.SRCALPHA)
                cxx = surf.get_width() // 2
                cyy = surf.get_height() // 2
                pygame.draw.line(surf, color,
                                 (cxx - dx, cyy - dy), (cxx + dx, cyy + dy), 3)
                surf.set_alpha(alpha)
                self.screen.blit(surf,
                                 (int(s["x"] - cxx), int(s["y"] - cyy)))
            else:
                pygame.draw.line(self.screen, color,
                                 (s["x"] - dx, s["y"] - dy),
                                 (s["x"] + dx, s["y"] + dy), 3)

    # ---------- экономика ----------
