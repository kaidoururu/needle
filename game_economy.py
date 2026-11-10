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
        bonus = NEEDLE_BONUS_BASE * self.level
        if self.level > MAX_LEVEL:
            bonus *= ENDLESS_BONUS_MULT ** (self.level - MAX_LEVEL)
        if getattr(self, "golden_needle", False):
            bonus *= GOLD_NEEDLE_BONUS_MULT
        return int(bonus)

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
            self.save_game()



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
            self.save_game()

    # ---------- геометрия интерфейса ----------



    # ---------- описания веток лавки ----------
    def shop_item_info(self, key):
        if key == "shovel":
            return "ЛОПАТА", "Копает больше клеток за рывок"
        if key == "cap":
            return "ЗАПАС СИЛ", "Больше сил на рывки"
        if key == "regen":
            return "СКОРОСТЬ СИЛ", "Силы восстанавливаются быстрее"
        if key == "price":
            return "ЦЕНА СЕНА", "Сено продается дороже"
        if key == "health":
            return "ЗДОРОВЬЕ", "Больше запас здоровья"
        if key == "bnd":
            return "АПТЕЧКА", ("Бинтов: %d/%d   Противоядий: %d/%d"
                               % (self.bandages, self.bandage_cap(),
                                  self.antidotes, self.antidote_cap()))
        return "", ""
