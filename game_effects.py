# -*- coding: utf-8 -*-
# Эффекты: сообщения, таблички находок, соломинки

import math
import random
import pygame

from game_config import *


# r64 (П.4а): константы плашек вынесены из show_notice/draw_notice,
# чтобы prewarm_notices строил все кэши заранее по одному списку
# заголовков и одному списку предметов.
NOTICE_TITLES = {
    "stone": "КАМЕНЬ!",
    "plant": "ЯДОВИТОЕ РАСТЕНИЕ!",
    "animal": "УКУС ЗВЕРЯ!",
    "bandage": "БИНТ!",
    "antidote": "ПРОТИВОЯДИЕ!",
    "compass": "КОМПАС!",
    "energy": "ЭНЕРГЕТИК!",
    "clover": "КЛЕВЕР!",
}
NOTICE_GREEN = ("bandage", "antidote", "compass", "energy", "clover")
NOTICE_ITEMS = ("stone", "plant", "animal", "bandage", "antidote",
                "compass", "energy", "clover")


class EffectsMixin:
    """Эффекты: сообщения, таблички находок, соломинки"""


    # ---------- сообщения и таблички ----------
    def add_message(self, text, color):
        self.messages.append({"text": text, "color": color, "life": 2.6})



    def show_notice(self, item):
        self.notice = {"item": item,
                       "title": NOTICE_TITLES.get(item, item),
                       "sub": "", "life": NOTICE_TIME}



    def draw_notice(self):
        n = self.notice
        if not n:
            return
        w, h = self.screen.get_size()
        ph = S(260)
        # ширина по заголовку: длинные плашки ("ЯДОВИТОЕ РАСТЕНИЕ!")
        # не режутся, узкие остаются прежними
        tw = self.font_big.size(n["title"])[0]
        pw = max(S(460), tw + 2 * S(24))
        px = (w - pw) // 2
        py = self.field_rect.top + (self.field_rect.h - ph) // 2 - 40

        # r64 (П.4а): панель из кэша, построение — в
        # _get_notice_panel (заполняется prewarm_notices заранее)
        panel = self._get_notice_panel(pw)
        self.screen.blit(panel, (px, py))

        icon_cx = px + pw // 2
        icon_cy = py + S(92)
        # r64 (П.4а): диспетчер по имени предмета вместо цепочки
        # if/elif — одна строка на все восемь находок, иконка из кэша
        getattr(self, "draw_" + n["item"])(self.screen,
                                           icon_cx, icon_cy, S(110), None)

        color = GREEN_MSG if n["item"] in NOTICE_GREEN else RED
        # r34+r53: заголовок и подпись рендерятся ОДИН раз на
        # уведомление, дальше каждый кадр — только blit. r53: плавная
        # альфа убрана (срочная правка производительности) — плашка
        # и иконка появляются и исчезают мгновенно, пер-кадровой
        # установки альфы больше нет. Текст за жизнь уведомления не
        # меняется, dict новый на каждое show_notice — кэш
        # инвалидируется сам.
        # r64 (П.4а): заголовок из общего кэша _notice_title_cache
        # (наполняется prewarm_notices до первого кадра), ключ
        # (текст, цвет) — рендера в кадре копания больше нет
        cache = getattr(self, "_notice_title_cache", None)
        if cache is None:
            cache = self._notice_title_cache = {}
        t1 = cache.get((n["title"], color))
        if t1 is None:
            t1 = self.font_big.render(n["title"], True, color)
            cache[(n["title"], color)] = t1
        self.screen.blit(t1, t1.get_rect(center=(w // 2, py + S(178))))
        if n["sub"]:
            t2 = n.get("_t2")
            if t2 is None or n.get("_font2") != id(self.font_mid):
                t2 = self.font_mid.render(n["sub"], True, TEXT)
                n["_t2"], n["_font2"] = t2, id(self.font_mid)
            self.screen.blit(t2, t2.get_rect(center=(w // 2, py + S(226))))



    def _get_notice_panel(self, pw):
        """r64 (П.4а): панель плашки — из кэша по ширине; построение
        вынесено из draw_notice, кэш заполняет prewarm_notices."""
        ph = S(260)
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
        return panel

    def prewarm_notices(self):
        """r64 (П.4а): подогрев кэшей плашек до первого кадра —
        панели всех ширин заголовков, заголовки обоих цветов и иконки
        всех находок размера плашки S(110). Первое появление плашки —
        чистый blit вместо построения панели, рендера заголовка и
        иконки в кадре копания."""
        # панели всех ширин заголовков
        for title in NOTICE_TITLES.values():
            tw = self.font_big.size(title)[0]
            pw = max(S(460), tw + 2 * S(24))
            self._get_notice_panel(pw)
        # заголовки обоих цветов в общий кэш
        cache = getattr(self, "_notice_title_cache", None)
        if cache is None:
            cache = self._notice_title_cache = {}
        for title in NOTICE_TITLES.values():
            for color in (RED, GREEN_MSG):
                key = (title, color)
                if key not in cache:
                    cache[key] = self.font_big.render(title, True, color)
        # иконки всех находок в кэш _cached_draw (размер плашки)
        scratch = pygame.Surface((S(110), S(110)), pygame.SRCALPHA)
        for item in NOTICE_ITEMS:
            getattr(self, "draw_" + item)(scratch,
                                          S(110) // 2, S(110) // 2,
                                          S(110), None)

    def draw_messages(self):
        """Сообщения на тёмной плашке — читаются на любом фоне стога."""
        y = self.field_rect.top + S(14)
        for m in self.messages:
            # r33+r53: плашка с текстом собирается ОДИН раз при
            # появлении сообщения, дальше каждый кадр — только blit.
            # r53: плавная альфа убрана (срочная правка
            # производительности) — сообщения появляются и исчезают
            # мгновенно, пер-кадровой установки альфы больше нет.
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
            px = self.field_rect.centerx - surf.get_width() // 2
            self.screen.blit(surf, (px, y))
            y += surf.get_height() + S(4)

    # ---------- экранные вспышки ----------
    # r51 (v5-48): полноэкранные пелены удалены по просьбе
    # пользователя: красная вспышка укуса, фиолетовые вспышка и
    # пелена яда, заодно жёлтая тонировка энергетика — они были
    # главным источником тормозов при эффектах. Сигналы остаются:
    # плашки «Укус зверя!» / «Отравление!» и цветные сообщения.
    # Обе функции эффектов заливок больше не существуют, вызовы в
    # game_loop/game_field сняты.

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
        # r65 (П.4б): ноль аллокаций списков в кадре — фильтрация на
        # месте: сам self.straws и есть буфер, выжившие уплотняются к
        # началу (индекс n не обгоняет текущий, перезапись безопасна),
        # хвост отрезается. Старый вариант создавал новый список alive
        # каждый кадр.
        straws = self.straws
        n = 0
        for s in straws:
            s["life"] -= dt
            if s["life"] <= 0:
                continue
            s["vy"] += STRAW_GRAVITY * dt
            s["x"] += s["vx"] * dt
            s["y"] += s["vy"] * dt
            s["ang"] += s["spin"] * dt
            straws[n] = s
            n += 1
        del straws[n:]



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
