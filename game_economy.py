# -*- coding: utf-8 -*-
# Экономика: цены улучшений, продажа сена, покупки

import math
import random
import pygame

from game_config import *


class EconomyMixin:
    """Экономика: цены улучшений, продажа сена, покупки"""


    # ---------- экономика ----------
    def dig_side(self):
        return min(7, 1 + (self.shovel - 1) // 2)



    def regen_rate(self):
        return REGEN_BASE + REGEN_STEP * self.regen_lvl



    def needle_bonus(self):
        return NEEDLE_BONUS_BASE * self.level

    # --- цены улучшений ---


    def shovel_cost(self):
        return int(40 * 1.9 ** (self.shovel - 1))



    def cap_cost(self):
        return int(100 * 1.6 ** self.cap_lvl)



    def regen_cost(self):
        return int(80 * 1.6 ** self.regen_lvl)



    def price_cost(self):
        return int(400 * 2.0 ** self.price_lvl)



    def health_cost(self):
        return int(150 * 1.7 ** self.health_lvl)



    def bnd_cost(self):
        return int(250 * 1.7 ** self.bnd_lvl)



    def sell(self):
        if self.hay > 0:
            self.money += self.hay_value
            self.hay = 0
            self.hay_value = 0



    def buy(self, kind):
        bought = False
        if kind == "shovel":
            cost = self.shovel_cost()
            if self.money >= cost:
                self.money -= cost
                self.shovel += 1
                bought = True
        elif kind == "cap":
            cost = self.cap_cost()
            if self.money >= cost:
                self.money -= cost
                self.cap_lvl += 1
                self.max_stamina += STAMINA_STEP
                self.stamina += STAMINA_STEP
                bought = True
        elif kind == "regen":
            cost = self.regen_cost()
            if self.money >= cost:
                self.money -= cost
                self.regen_lvl += 1
                bought = True
        elif kind == "price":
            cost = self.price_cost()
            if self.money >= cost:
                self.money -= cost
                self.price_lvl += 1
                bought = True
        elif kind == "health":
            cost = self.health_cost()
            if self.money >= cost:
                self.money -= cost
                self.health_lvl += 1
                self.max_health += HEALTH_STEP
                self.health += HEALTH_STEP
                bought = True
        elif kind == "bnd":
            cost = self.bnd_cost()
            if self.money >= cost:
                self.money -= cost
                self.bnd_lvl += 1
                bought = True
        if bought:
            self.shop_surf = None

    # ---------- геометрия интерфейса ----------



    # ---------- описания веток лавки (с цифрами или без) ----------
    def shop_item_info(self, key):
        if key == "shovel":
            title = "ЛОПАТА"
            if DEBUG:
                desc = ("Копает область %d×%d — но каждая клетка = 1 сила"
                        % (self.dig_side(), self.dig_side()))
            else:
                desc = "Копает больше клеток за рывок"
            return title, desc
        if key == "cap":
            title = "ЗАПАС СИЛ"
            if DEBUG:
                desc = ("Максимум сил: %d (+%d за уровень)"
                        % (int(self.max_stamina), STAMINA_STEP))
            else:
                desc = "Больше сил на рывки"
            return title, desc
        if key == "regen":
            title = "СКОРОСТЬ СИЛ"
            if DEBUG:
                desc = ("Восстановление: %.1f/сек (+%.1f за уровень)"
                        % (self.regen_rate(), REGEN_STEP))
            else:
                desc = "Силы восстанавливаются быстрее"
            return title, desc
        if key == "price":
            title = "ЦЕНА СЕНА"
            if DEBUG:
                desc = ("+%d%% к цене пучков (x%.2f -> x%.2f)"
                        % (int((self.price_mult() - 1) * 100 + 25),
                           self.price_mult(),
                           self.price_mult() + 0.25))
            else:
                desc = "Сено продается дороже"
            return title, desc
        if key == "health":
            title = "ЗДОРОВЬЕ"
            if DEBUG:
                desc = ("Максимум здоровья: %d (+%d за уровень)"
                        % (int(self.max_health), HEALTH_STEP))
            else:
                desc = "Больше запас здоровья"
            return title, desc
        if key == "bnd":
            title = "АПТЕЧКА"
            if DEBUG:
                desc = ("Бинты %d/%d, противоядия %d/%d"
                        % (self.bandages, self.bandage_cap(),
                           self.antidotes, self.antidote_cap()))
            else:
                desc = ("Бинтов: %d   Противоядий: %d"
                        % (self.bandages, self.antidotes))
            return title, desc
        return "", ""
