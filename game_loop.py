# -*- coding: utf-8 -*-
# Главный цикл: события, клики, отрисовка кадра

import math
import random
import pygame

from game_config import *


class LoopMixin:
    """Главный цикл: события, клики, отрисовка кадра"""


    def handle_click(self, pos):
        if self.dead:
            for name, rect in self.death_buttons.items():
                if rect.collidepoint(pos):
                    if name == "continue":
                        lost = int(self.money * (1.0 - DEATH_MONEY_KEEP))
                        self.money = int(self.money * DEATH_MONEY_KEEP)
                        self.stamina = 0.0
                        self.health = self.max_health
                        self.poison_time = 0.0
                        self.clover_time = 0.0
                        self.compass_hint = None
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
                        self.save_game()
                        self.add_message(
                            "Вы возродились. Потеряно %d монет, сено "
                            "сохранилось. Уровень %d заново, силы на нуле"
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
                        val = self.hay_value
                        self.sell()
                        if DEBUG:
                            self.add_message("Сено продано: +%d монет" % val,
                                             GREEN_MSG)
                        else:
                            self.add_message("Сено продано", GREEN_MSG)
                elif name == "shop":
                    self.open_shop()
                elif name == "next":
                    if self.needle_found:
                        self.next_level()
                return
        self.dig_at(pos)

    # ---------- главный цикл ----------



    # ---------- главный цикл ----------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            self.time += dt

            if self.stamina < self.max_stamina:
                self.stamina = min(self.max_stamina,
                                   self.stamina + self.regen_rate() * dt)

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
            self.messages = [m for m in self.messages if m["life"] > 0]
            if self.notice:
                self.notice["life"] -= dt
                if self.notice["life"] <= 0:
                    self.notice = None

            if self.shop_slide < self.shop_target:
                self.shop_slide = min(self.shop_target,
                                      self.shop_slide + SLIDE_SPEED * dt)
            elif self.shop_slide > self.shop_target:
                self.shop_slide = max(self.shop_target,
                                      self.shop_slide - SLIDE_SPEED * dt)
            if self.help_slide < self.help_target:
                self.help_slide = min(self.help_target,
                                      self.help_slide + SLIDE_SPEED * dt)
            elif self.help_slide > self.help_target:
                self.help_slide = max(self.help_target,
                                      self.help_slide - SLIDE_SPEED * dt)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.save_game()
                    running = False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        event.size, pygame.RESIZABLE)
                    self.make_fonts()
                    self.build_field()
                    self.build_ui()
                    self.field_dirty = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = getattr(event, "pos", None)
                    if pos is None:
                        continue
                    if not self.won and not self.dead and \
                            self.help_button.collidepoint(pos):
                        if self.help_target > 0.5:
                            self.close_help()
                        else:
                            self.open_help()
                    else:
                        self.handle_click(pos)

            self.draw_field()
            self.draw_screen_effects()
            self.draw_hud()
            self.draw_shop()
            self.draw_help_panel()
            if not self.won and not self.dead:
                self.draw_help_button()
            pygame.display.flip()
        pygame.quit()


if __name__ == "__main__":
    Game().run()
