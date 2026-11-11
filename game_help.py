# -*- coding: utf-8 -*-
# Справка «?»: поверхность и выдвижная панель

import math
import random
import pygame

from game_config import *


class HelpMixin:
    """Справка «?»: поверхность и выдвижная панель"""


    # ---------- выдвижная справка «?» ----------
    def make_help_surface(self):
        w, h = self.screen.get_size()
        self.help_panel_h = min(HELP_H, h)
        ph = self.help_panel_h
        surf = pygame.Surface((w, ph)).convert()
        surf.fill(SHOP_BG)
        pygame.draw.rect(surf, PANEL_EDGE, (0, 0, w, 4))

        title = self.font_big.render("СПРАВКА ПО ИГРЕ", True, GOLD)
        surf.blit(title, title.get_rect(center=(w // 2, 44)))

        lines = [
            ("ЦЕЛЬ", GOLD),
            ("Найти иголку в стоге сена и продать остальное.", TEXT),
            ("Тап — рывок лопатой: каждая вскрытая клетка", TEXT),
            ("стоит 1 силу. Большая лопата копает больше клеток,", TEXT),
            ("но и рискует сильнее — ловушки срабатывают все!", TEXT),
            ("", TEXT),
            ("МЕНЮ И ПАУЗА", GOLD),
            ("Кнопка «II» или Esc — пауза: продолжить,", TEXT),
            ("рестарт уровня, новая игра, выход в меню.", TEXT),
            ("Если долго ничего не делать, появится", TEXT),
            ("подсказка: куда нажать или где копать.", TEXT),
            ("", TEXT),
            ("ТОРГОВЛЯ", GOLD),
            ("Копите сено и продавайте кнопкой «Продать сено»", TEXT),
            ("внизу — она показывает, сколько монет дадут.", TEXT),
            ("Закрыть справку — «?» или тап по стогу.", TEXT),
            ("", TEXT),
            ("ЦЕНА СЕНА", GOLD),
            ("Чем желтее клетка, тем дешевле сено, чем коричневее —", TEXT),
            ("тем дороже, но тем реже оно встречается", TEXT),
            ("и тем вероятнее в нём ловушка!", RED),
            ("", TEXT),
            ("ЛОВУШКИ И НАХОДКИ", GOLD),
            ("Камень — лопата откатывается на 1 уровень.", RED),
            ("Укус зверя — бьёт всё сильнее с каждым уровнем", RED),
            ("и окаймляет экран красным.", RED),
            ("Ядовитое растение — ОТРАВЛЯЕТ: здоровье тает", PURPLE_MSG),
            ("каждую секунду, экран мутит фиолетовым, а яд", PURPLE_MSG),
            ("крепчает и действует дольше на дальних уровнях.", PURPLE_MSG),
            ("", TEXT),
            ("ЗДОРОВЬЕ НЕ ВОССТАНАВЛИВАЕТСЯ САМО", GOLD),
            ("Лечить можно только бинтами. Ноль здоровья", RED),
            ("— вы УМИРАЕТЕ: теряете 50% монет, сено", RED),
            ("сгорает, уровень заново, силы обнуляются.", RED),
            ("", TEXT),
            ("АПТЕЧКА ВНИЗУ", GOLD),
            ("Бинт — тап по белому рулону: лечит.", GREEN_MSG),
            ("Противоядие — тап по флакону: снимает отравление.", GREEN_MSG),
            ("Если карман полон — лишнее теряется!", RED),
            ("При первом укусе или отравлении игра", TEXT),
            ("подсветит нужное лекарство — просто нажмите.", TEXT),
            ("", TEXT),
            ("ЛОВУШКИ В РЫВКЕ", GOLD),
            ("Срабатывают ВСЕ ловушки в накопанных клетках.", RED),
            ("Бинты и противоядия теряются, если", RED),
            ("в рывке сработала хоть одна ловушка.", RED),
            ("", TEXT),
            ("РЕДКИЕ НАХОДКИ", GOLD),
            ("Компас — подсвечивает часть стога с иглой.", GREEN_MSG),
            ("Магнит — следующий рывок копает вдвое больше.", GREEN_MSG),
            ("Клевер — 30 секунд: шанс 35% спастись от ловушки.",
             GREEN_MSG),
            ("Редкие находки не теряются от ловушек.", GREEN_MSG),
            ("", TEXT),
            ("СЕРИЯ РЫВКОВ", GOLD),
            ("Каждые 10 рывков без ловушек — бонус монетами.", GOLD),
            ("Ловушка рвёт серию.", TEXT),
            ("", TEXT),
            ("БЕСКОНЕЧНЫЙ СТОГ И ЗОЛОТАЯ ИГЛА", GOLD),
            ("Уровней нет — стог бесконечен: ловушки", GOLD),
            ("злее, а бонус за иглу растёт. Золотая игла", GOLD),
            ("(1 из 15 стогов) даёт бонус x5.", GOLD),
            ("", TEXT),
            ("ЛАВКА УЛУЧШЕНИЙ", GOLD),
            ("Шесть веток: лопата, запас и скорость сил,", TEXT),
            ("цена сена, здоровье, аптека. Всё быстро дорожает.", TEXT),
        ]
        step = max(22, min(30, (ph - 160) // max(1, len(lines))))
        y = 88
        for text, color in lines:
            if text:
                surf.blit(self.font_shop_desc.render(text, True, color),
                          (30, y))
            y += step

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
        hovered = rect.collidepoint(pygame.mouse.get_pos())
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



    def close_help(self):
        self.help_target = 0.0
