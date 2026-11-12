# -*- coding: utf-8 -*-
# Справка «?»: поверхность на две страницы и выдвижная панель

import pygame

from game_config import *


# страницы справки: (текст, цвет); переносы сделаны заранее,
# каждая строка гарантированно в одну строку панели
HELP_PAGE_1 = [
    ("ЦЕЛЬ", GOLD),
    ("Найти иголку в стоге сена и продать остальное.", TEXT),
    ("Тап — рывок лопатой: каждая вскрытая клетка", TEXT),
    ("стоит 1 силу. Большая лопата копает больше,", TEXT),
    ("но рискует сильнее — ловушки срабатывают все!", TEXT),
    ("", TEXT),
    ("МЕНЮ И ПАУЗА", GOLD),
    ("Кнопка «II» или Esc — пауза: продолжить,", TEXT),
    ("рестарт уровня, новая игра, выход в меню.", TEXT),
    ("", TEXT),
    ("ПЛАШКИ И СПРАВКА", GOLD),
    ("Монеты и сено — в плашках слева от паузы «II»", GREEN_MSG),
    ("(на узких экранах прячутся). Кнопка «?»", GREEN_MSG),
    ("открывает эту справку.", GREEN_MSG),
    ("", TEXT),
    ("ТОРГОВЛЯ", GOLD),
    ("Копите сено и продавайте кнопкой «Продать сено»", TEXT),
    ("внизу — она показывает, сколько монет дадут.", TEXT),
    ("Закрыть справку — «?» или тап по стогу.", TEXT),
    ("", TEXT),
    ("ЦЕНА СЕНА", GOLD),
    ("Чем желтее клетка, тем дешевле сено, чем", TEXT),
    ("коричневее — тем дороже, но тем реже оно", TEXT),
    ("встречается и тем вероятнее в нём ловушка!", RED),
    ("", TEXT),
    ("ЛОВУШКИ И НАХОДКИ", GOLD),
    ("Камень — лопата откатывается на 1 уровень.", RED),
    ("Укус зверя — бьёт всё сильнее с каждым уровнем", RED),
    ("и окаймляет экран красным.", RED),
    ("Ядовитое растение — ОТРАВЛЯЕТ: здоровье тает", PURPLE_MSG),
    ("каждую секунду, экран мутит фиолетовым, а яд", PURPLE_MSG),
    ("крепчает и действует дольше на дальних уровнях.", PURPLE_MSG),
]

HELP_PAGE_2 = [
    ("ЗДОРОВЬЕ НЕ ВОССТАНАВЛИВАЕТСЯ", GOLD),
    ("Лечить можно только бинтами. Ноль здоровья", RED),
    ("— вы УМИРАЕТЕ: минус 50% монет, сено сгорает,", RED),
    ("уровень заново, силы обнуляются.", RED),
    ("", TEXT),
    ("АПТЕЧКА ВНИЗУ", GOLD),
    ("Бинт — тап по рулону: лечит. Противоядие —", GREEN_MSG),
    ("тап по флакону: снимает яд. Полный карман —", GREEN_MSG),
    ("лишнее теряется!", RED),
    ("", TEXT),
    ("ОБУЧЕНИЕ ПОДСВЕТКОЙ", GOLD),
    ("Первый укус, первое отравление и первый", BLUE_MSG),
    ("заслуженный поход в лавку — игра подсветит", BLUE_MSG),
    ("нужную кнопку золотой рамкой. Просто", BLUE_MSG),
    ("нажмите на неё.", BLUE_MSG),
    ("", TEXT),
    ("ЛОВУШКИ В РЫВКЕ И СЕРИИ", GOLD),
    ("В рывке срабатывают ВСЕ ловушки накопанных", RED),
    ("клеток, а бинты и противоядия теряются, если", RED),
    ("сработала хоть одна. Зато каждые 10 рывков", GOLD),
    ("без ловушек — бонус монетами.", GOLD),
    ("", TEXT),
    ("РЕДКИЕ НАХОДКИ", GOLD),
    ("Компас — подсвечивает часть стога с иглой.", GREEN_MSG),
    ("Энергетик — 10 секунд рывки не тратят силы:", GREEN_MSG),
    ("копайте без остановки и пауз на восстановление.", GREEN_MSG),
    ("Клевер — 30 секунд: шанс 35% спастись", GREEN_MSG),
    ("от ловушки. Находки не теряются от ловушек.", GREEN_MSG),
    ("", TEXT),
    ("БЕСКОНЕЧНЫЙ СТОГ", GOLD),
    ("Ловушки злее с каждым уровнем, а бонус за", GOLD),
    ("иглу растёт. Золотая игла (1 из 15 стогов)", GOLD),
    ("даёт бонус x5.", GOLD),
    ("", TEXT),
    ("ЛАВКА УЛУЧШЕНИЙ", GOLD),
    ("Шесть веток: лопата, запас и скорость сил,", TEXT),
    ("цена сена, здоровье, аптека. Всё дорожает.", TEXT),
]

HELP_PAGES = (HELP_PAGE_1, HELP_PAGE_2)


class HelpMixin:
    """Справка «?»: две страницы, кнопки навигации внизу панели."""

    # ---------- сборка страницы ----------
    def make_help_surface(self):
        w, h = self.screen.get_size()
        self.help_panel_h = min(HELP_H, h)
        ph = self.help_panel_h
        surf = pygame.Surface((w, ph)).convert()
        surf.fill(SHOP_BG)
        pygame.draw.rect(surf, PANEL_EDGE, (0, 0, w, 4))

        title = self.font_big.render("СПРАВКА ПО ИГРЕ", True, GOLD)
        surf.blit(title, title.get_rect(center=(w // 2, 40)))
        page_lbl = self.txt("стр. %d из %d" % (self.help_page + 1,
                                               len(HELP_PAGES)),
                            self.font_small, SILVER)
        surf.blit(page_lbl, page_lbl.get_rect(center=(w // 2, 74)))

        lines = HELP_PAGES[self.help_page]
        # ниже 78 px — зона кнопок навигации
        avail = (ph - 78) - 96
        step = max(14, min(30, avail // max(1, len(lines))))
        # шрифт подстраивается под шаг: текст не обрезается на
        # невысоких экранах
        fsize = max(13, min(24, step - 3))
        try:
            font = pygame.font.SysFont("arial", fsize)
        except Exception:
            font = pygame.font.Font(None, int(fsize * 1.7))
        y = 96
        for text, color in lines:
            if text:
                surf.blit(self.txt(text, font, color), (30, y))
            y += step

        # ---------- кнопки страниц ----------
        self.help_nav = {
            "prev": pygame.Rect(w // 2 - 260, ph - 64, 200, 48),
            "next": pygame.Rect(w // 2 + 60, ph - 64, 200, 48),
        }
        for name, rect in self.help_nav.items():
            active = ((name == "prev" and self.help_page > 0)
                      or (name == "next"
                          and self.help_page < len(HELP_PAGES) - 1))
            color = BTN if active else BTN_DISABLED
            pygame.draw.rect(surf, color, rect, border_radius=12)
            pygame.draw.rect(surf, PANEL_EDGE, rect, 2, border_radius=12)
            label = self.font_mid.render(
                "← НАЗАД" if name == "prev" else "ВПЕРЁД →", True,
                TEXT if active else (160, 140, 110))
            surf.blit(label, label.get_rect(center=rect.center))

        self.help_surf = surf

    def draw_help_panel(self):
        if self.help_slide <= 0.0:
            return
        if self.help_surf is None:
            self.make_help_surface()
        w, h = self.screen.get_size()
        dy = self.help_offset()
        top = h - dy

        if top > 0:
            shade = pygame.Surface((w, top), pygame.SRCALPHA)
            shade.fill((0, 0, 0, min(140, int(140 * self.help_slide))))
            self.screen.blit(shade, (0, 0))

        self.screen.blit(self.help_surf, (0, top))
        # кнопки закрытия нет: «?» или тап по стогу

    def draw_help_button(self):
        rect = self.help_button
        hovered = rect.collidepoint(self.mouse_pos())
        color = BTN_HOVER if hovered else BTN
        pygame.draw.circle(self.screen, color, rect.center, rect.w // 2)
        pygame.draw.circle(self.screen, (30, 20, 10), rect.center,
                           rect.w // 2, 3)
        label = self.font_shop_head.render("?", True, TEXT)
        self.screen.blit(label, label.get_rect(center=rect.center))

    # ---------- выдвижная лавка ----------

    def open_help(self):
        self.help_target = 1.0
        self.shop_target = 0.0
        self.help_page = 0        # справка всегда открывается с первой
        self.help_surf = None

    def close_help(self):
        self.help_target = 0.0
