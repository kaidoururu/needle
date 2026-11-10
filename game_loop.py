# -*- coding: utf-8 -*-
# Главный цикл: меню/игра/пауза, события, клики, отрисовка кадра

import math
import random
import pygame

from game_config import *


class LoopMixin:
    """Главный цикл: состояния меню/игры/паузы, события, клики"""


    # ---------- меню и пауза ----------
    def handle_menu_click(self, pos):
        for name, rect in self.menu_buttons.items():
            if rect.collidepoint(pos):
                if name == "continue":
                    self.state = "game"
                    return None
                if name == "new":
                    self.start_new_game()
                    self.state = "game"
                    return None
                if name == "quit":
                    return "quit"
        return None



    def open_pause(self):
        if self.won or self.dead:
            return
        self.state = "pause"
        self.shop_target = 0.0
        self.help_target = 0.0
        self.tutorial = None
        self.idle_hint = None



    def handle_pause_click(self, pos):
        for name, rect in self.pause_buttons.items():
            if rect.collidepoint(pos):
                if name == "continue":
                    self.state = "game"
                elif name == "restart":
                    self.restart()
                    self.state = "game"
                elif name == "new":
                    self.start_new_game()
                    self.state = "game"
                elif name == "menu":
                    self.save_game()
                    self.tutorial = None
                    self.idle_hint = None
                    self.state = "menu"

    # ---------- обработка кликов в игре ----------
    def handle_click(self, pos):
        if self.dead:
            for name, rect in self.death_buttons.items():
                if rect.collidepoint(pos):
                    if name == "continue":
                        lost = int(self.money * (1.0 - DEATH_MONEY_KEEP))
                        self.money = int(self.money * DEATH_MONEY_KEEP)
                        self.hay = 0
                        self.hay_value = 0
                        self.stamina = 0.0
                        self.health = self.max_health
                        self.poison_time = 0.0
                        self.clover_time = 0.0
                        self.compass_hint = None
                        self.compass_quadrant = None
                        self.magnet_ready = False
                        self.streak = 0
                        self.bandages = min(self.bandages,
                                            self.bandage_cap())
                        self.antidotes = min(self.antidotes,
                                             self.antidote_cap())
                        self.build_field()
                        self.won = False
                        self.needle_found = False
                        self.digs = 0
                        self.straws = []
                        self.dead = False
                        self.bite_flash = 0.0
                        self.poison_flash = 0.0
                        self.tutorial = None
                        self.save_game()
                        self.add_message(
                            "Вы возродились. Потеряно %d монет, сено "
                            "сгорело. Уровень %d заново, силы на нуле"
                            % (lost, self.level), RED)
                    return
            return

        if self.help_slide > 0.95:
            h = self.screen.get_height()
            top = h - self.help_offset()
            visible = pygame.Rect(0, max(0, top), self.screen.get_width(),
                                  self.help_offset())
            if not visible.collidepoint(pos):
                self.close_help()
            return

        if self.won:
            for name, rect in self.win_buttons.items():
                if rect.collidepoint(pos):
                    if name == "again":
                        self.restart()
                    elif name == "keep":
                        self.won = False
                        self.field_dirty = True
                    elif name == "next":
                        self.next_level()
                    return
            return

        if self.shop_slide > 0.95:
            h = self.screen.get_height()
            top = h - self.shop_offset()
            visible = pygame.Rect(0, max(0, top), self.screen.get_width(),
                                  self.shop_offset())
            if not visible.collidepoint(pos):
                self.close_shop()
                return
            for name, rect in self.shop_buttons.items():
                if rect.move(0, top).collidepoint(pos):
                    if name == "close":
                        self.close_shop()
                    elif name.startswith("buy_"):
                        self.buy(name[4:])
                    return
            return

        if self.bandage_btn.collidepoint(pos):
            self.use_bandage()
            return
        if self.antidote_btn.collidepoint(pos):
            self.use_antidote()
            return

        for name, rect in self.main_buttons.items():
            if rect.collidepoint(pos):
                if name == "sell":
                    if self.hay > 0:
                        self.sell()
                        self.add_message("Сено продано", GREEN_MSG)
                elif name == "shop":
                    self.open_shop()
                elif name == "next":
                    if self.needle_found:
                        self.next_level()
                return
        self.dig_at(pos)

    # ---------- подсказка простоя ----------
    def update_idle_hint(self):
        if self.idle_time < IDLE_HINT_AFTER:
            return
        if self.idle_hint is not None:
            return
        if self.won or self.dead or self.tutorial:
            return
        if self.shop_slide > 0.5 or self.help_slide > 0.5:
            return
        if self.needle_found:
            self.idle_hint = {
                "text": "Нажмите «Уровень %d», чтобы идти дальше"
                        % (self.level + 1),
                "target": self.main_buttons["next"].copy(),
                "cell": None}
        elif self.poison_time > 0 and self.antidotes > 0:
            self.idle_hint = {
                "text": "Вы отравлены! Нажмите на флакон",
                "target": self.antidote_btn.copy(), "cell": None}
        elif self.health < self.max_health * 0.4 and self.bandages > 0:
            self.idle_hint = {
                "text": "Мало здоровья! Нажмите на бинт",
                "target": self.bandage_btn.copy(), "cell": None}
        elif self.hay_value > 0:
            self.idle_hint = {
                "text": "Продайте сено, чтобы получить монеты",
                "target": self.main_buttons["sell"].copy(),
                "cell": None}
        else:
            undug = [i for i, c in enumerate(self.cells) if not c["dug"]]
            if undug:
                i = random.choice(undug)
                self.idle_hint = {"text": "Копайте здесь!",
                                  "target": None, "cell": i}

    # ---------- главный цикл ----------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            self.time += dt

            if self.state == "game":
                if self.stamina < self.max_stamina:
                    self.stamina = min(self.max_stamina,
                                       self.stamina +
                                       self.regen_rate() * dt)

                if self.clover_time > 0:
                    self.clover_time = max(0.0, self.clover_time - dt)
                    if self.clover_time == 0.0:
                        self.add_message("Клевер больше не действует",
                                         GREEN_MSG)

                if self.poison_time > 0:
                    self.poison_time -= dt
                    if self.poison_time <= 0:
                        self.poison_time = 0.0
                        self.add_message("Отравление прошло", GREEN_MSG)
                    else:
                        self.health -= self.poison_rate() * dt
                        if self.health <= 0:
                            self.health = 0
                            self.dead = True

                self.update_flashes(dt)
                self.update_straws(dt)

                for m in self.messages:
                    m["life"] -= dt
                self.messages = [m for m in self.messages
                                 if m["life"] > 0]
                if self.notice:
                    self.notice["life"] -= dt
                    if self.notice["life"] <= 0:
                        self.notice = None

                if self.shop_slide < self.shop_target:
                    self.shop_slide = min(self.shop_target,
                                          self.shop_slide +
                                          SLIDE_SPEED * dt)
                elif self.shop_slide > self.shop_target:
                    self.shop_slide = max(self.shop_target,
                                          self.shop_slide -
                                          SLIDE_SPEED * dt)
                if self.help_slide < self.help_target:
                    self.help_slide = min(self.help_target,
                                          self.help_slide +
                                          SLIDE_SPEED * dt)
                elif self.help_slide > self.help_target:
                    self.help_slide = max(self.help_target,
                                          self.help_slide -
                                          SLIDE_SPEED * dt)

                self.idle_time += dt
                self.update_idle_hint()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    if self.state != "menu":
                        self.save_game()
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        event.size, pygame.RESIZABLE)
                    self.make_fonts()
                    self.build_field()
                    self.build_ui()
                    self.field_dirty = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "game":
                            self.open_pause()
                        elif self.state == "pause":
                            self.state = "game"
                    self.idle_time = 0.0
                    self.idle_hint = None
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = getattr(event, "pos", None)
                    if pos is None:
                        continue
                    if self.state == "menu":
                        if self.handle_menu_click(pos) == "quit":
                            running = False
                    elif self.state == "pause":
                        self.handle_pause_click(pos)
                    else:
                        if (not self.won and not self.dead
                                and self.help_button.collidepoint(pos)):
                            if self.help_target > 0.5:
                                self.close_help()
                            else:
                                self.open_help()
                        elif (not self.won and not self.dead
                                and self.pause_button.collidepoint(pos)):
                            self.open_pause()
                        else:
                            self.handle_click(pos)
                    self.idle_time = 0.0
                    self.idle_hint = None

            if self.state == "menu":
                self.draw_field()
                self.draw_menu_screen()
            else:
                self.draw_field()
                self.draw_screen_effects()
                self.draw_hud()
                self.draw_bonus_icons()
                self.draw_shop()
                self.draw_help_panel()
                self.draw_tutorial()
                self.draw_idle_hint()
                if not self.won and not self.dead:
                    self.draw_help_button()
                    self.draw_pause_button()
                if self.state == "pause":
                    self.draw_pause_screen()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
