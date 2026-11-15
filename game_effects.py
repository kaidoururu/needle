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
        ph = S(260)
        # ширина по заголовку: длинные плашки ("ЯДОВИТОЕ РАСТЕНИЕ!")
        # не режутся, узкие остаются прежними
        tw = self.font_big.size(n["title"])[0]
        pw = max(S(460), tw + 2 * S(24))
        px = (w - pw) // 2
        py = self.field_rect.top + (self.field_rect.h - ph) // 2 - 40

        cache = getattr(self, "_notice_panel_w", None)
        if cache is None:
            cache = self._notice_panel_w = {}
        panel = cache.get(pw)
        if panel is None:
            panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pygame.draw.rect(panel, (25, 18, 10, 235),
                             (0, 0, pw, ph), border_radius=18)
            pygame.draw.rect(panel, (255, 210, 80, 200),
                             (0, 0, pw, ph), 4, border_radius=18)
            panel = panel.convert_alpha()
            cache[pw] = panel
        panel.set_alpha(alpha)
        self.screen.blit(panel, (px, py))

        icon_cx = px + pw // 2
        icon_cy = py + S(92)
        if n["item"] == "stone":
            self.draw_stone(self.screen, icon_cx, icon_cy, S(110), alpha)
        elif n["item"] == "plant":
            self.draw_plant(self.screen, icon_cx, icon_cy, S(110), alpha)
        elif n["item"] == "animal":
            self.draw_animal(self.screen, icon_cx, icon_cy, S(110), alpha)
        elif n["item"] == "bandage":
            self.draw_bandage(self.screen, icon_cx, icon_cy, S(110), alpha)
        elif n["item"] == "antidote":
            self.draw_antidote(self.screen, icon_cx, icon_cy, S(110), alpha)
        elif n["item"] == "compass":
            self.draw_compass(self.screen, icon_cx, icon_cy, S(110), alpha)
        elif n["item"] == "energy":
            self.draw_energy(self.screen, icon_cx, icon_cy, S(110), alpha)
        elif n["item"] == "clover":
            self.draw_clover(self.screen, icon_cx, icon_cy, S(110), alpha)

        color = GREEN_MSG if n["item"] in ("bandage", "antidote",
                                           "compass", "energy",
                                           "clover") else RED
        # r34: заголовок и подпись рендерятся ОДИН раз на уведомление,
        # дальше каждый кадр — только set_alpha + blit (как у сообщений
        # в r33). Текст за жизнь уведомления не меняется, dict новый на
        # каждое show_notice — кэш инвалидируется сам.
        t1 = n.get("_t1")
        if t1 is None or n.get("_font1") != id(self.font_big):
            t1 = self.font_big.render(n["title"], True, color)
            n["_t1"], n["_font1"] = t1, id(self.font_big)
        t1.set_alpha(alpha)
        self.screen.blit(t1, t1.get_rect(center=(w // 2, py + S(178))))
        if n["sub"]:
            t2 = n.get("_t2")
            if t2 is None or n.get("_font2") != id(self.font_mid):
                t2 = self.font_mid.render(n["sub"], True, TEXT)
                n["_t2"], n["_font2"] = t2, id(self.font_mid)
            t2.set_alpha(alpha)
            self.screen.blit(t2, t2.get_rect(center=(w // 2, py + S(226))))



    def draw_messages(self):
        """Сообщения на тёмной плашке — читаются на любом фоне стога."""
        y = self.field_rect.top + S(14)
        for m in self.messages:
            alpha = max(0, min(255, int(255 * m["life"] / 1.2)))
            # r33: плашка с текстом собирается ОДИН раз при появлении
            # сообщения, дальше каждый кадр — только set_alpha + blit.
            # Прозрачность работает через set_alpha поверх пер-пиксельной:
            # 215 * alpha / 255 — как в прежней версии, картинка та же.
            surf = m.get("_surf")
            if surf is None or m.get("_surf_font") != id(self.font_mid):
                # длинное сообщение переносится по ширине поля
                lines = wrap_text(m["text"], self.font_mid,
                                  self.field_rect.width - S(40))
                pad = S(10)
                lh = self.font_mid.get_linesize()
                pill_w = max(self.font_mid.size(ln)[0]
                             for ln in lines) + pad * 2
                pill_h = lh * len(lines) + pad * 2
                surf = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(surf, MSG_BG + (215,),
                                 (0, 0, pill_w, pill_h), border_radius=10)
                ty = pad
                for ln in lines:
                    ts = self.font_mid.render(ln, True, m["color"])
                    surf.blit(ts, (pad, ty))
                    ty += lh
                surf = surf.convert_alpha()
                m["_surf"] = surf
                m["_surf_font"] = id(self.font_mid)
            surf.set_alpha(alpha)
            px = self.field_rect.centerx - surf.get_width() // 2
            self.screen.blit(surf, (px, y))
            y += surf.get_height() + S(4)

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
        # r30 (план r28, точки b и c): плавное затухание убрано —
        # укус: полная плотность, пока идёт таймер, затем мгновенно ноль;
        # растение: две фазы — яркая вспышка на время таймера, затем
        # стабильная пелена POISON_TINT_ALPHA без переходов
        if self.bite_flash > 0:
            ov = ov_for(BITE_RED)
            ov.set_alpha(BITE_FLASH_ALPHA)
            self.screen.blit(ov, (0, 0))
        if self.poison_flash > 0:
            ov = ov_for(POISON_FLASH)
            ov.set_alpha(POISON_FLASH_ALPHA)
            self.screen.blit(ov, (0, 0))
        elif self.poison_time > 0:
            ov = ov_for(POISON_FLASH)
            ov.set_alpha(POISON_TINT_ALPHA)
            self.screen.blit(ov, (0, 0))
        # энергетик: жёлтая тонировка поля — та же техника,
        # отдельной веткой, чтобы обе заливки накладывались
        if self.energy_time > 0:
            ov = ov_for(ENERGY_TINT)
            ov.set_alpha(ENERGY_TINT_ALPHA)
            self.screen.blit(ov, (0, 0))
    def update_flashes(self, dt):
        # таймеры только отсчитывают длительность фазы яркой вспышки,
        # сама яркость в draw_flashes теперь постоянная (r30)
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
        # r35: план r31, п.1 — ноль выделений памяти в кадре. Вместо
        # SRCALPHA-поверхности на каждую соломинку — затухание цветом:
        # линия рисуется прямо в screen, цвет интерполируется к усреднённому
        # фону стога STRAW_FADE_TO (мгновение начала затухания совпадает
        # со старой альфой 255 * life / (STRAW_LIFE * 0.6)).
        bg = STRAW_FADE_TO
        for s in self.straws:
            t = max(0.0, min(1.0,
                             s["life"] / (STRAW_LIFE * 0.6)))
            half = s["len"] / 2
            dx = math.cos(s["ang"]) * half
            dy = math.sin(s["ang"]) * half
            c = s["color"]
            if t < 1.0:
                k = 1.0 - t
                color = (int(c[0] + (bg[0] - c[0]) * k),
                         int(c[1] + (bg[1] - c[1]) * k),
                         int(c[2] + (bg[2] - c[2]) * k))
            else:
                color = c
            pygame.draw.line(self.screen, color,
                             (s["x"] - dx, s["y"] - dy),
                             (s["x"] + dx, s["y"] + dy), 3)

    # ---------- экономика ----------
