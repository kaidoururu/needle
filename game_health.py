# -*- coding: utf-8 -*-
# Здоровье: укусы, отравление, бинты и противоядия

import math
import random
import pygame

from game_config import *


class HealthMixin:
    """Здоровье: укусы, отравление, бинты и противоядия"""


    # ---------- аптека ----------
    def bandage_cap(self):
        return BANDAGE_CAP_BASE + BANDAGE_CAP_STEP * self.bnd_lvl



    def antidote_cap(self):
        return ANTIDOTE_CAP_BASE + ANTIDOTE_CAP_STEP * self.bnd_lvl



    def animal_damage(self):
        return ANIMAL_DAMAGE_BASE + ANIMAL_DAMAGE_STEP * self.level



    def poison_rate(self):
        return POISON_RATE_BASE + POISON_RATE_STEP * self.level



    def poison_duration(self):
        return POISON_DUR_BASE + POISON_DUR_STEP * self.level



    def use_bandage(self):
        if self.bandages <= 0:
            self.add_message("Бинтов нет — ищите в стоге", RED)
            return
        if self.health >= self.max_health:
            self.add_message("Здоровье полное — бинт не нужен", GREEN_MSG)
            return
        self.bandages -= 1
        self.health = min(self.max_health, self.health + BANDAGE_HEAL)
        if DEBUG:
            self.add_message("Бинт использован: +%d здоровья"
                             % BANDAGE_HEAL, GREEN_MSG)
        else:
            self.add_message("Бинт использован", GREEN_MSG)



    def use_antidote(self):
        if self.antidotes <= 0:
            self.add_message("Противоядий нет — ищите в стоге", RED)
            return
        if self.poison_time <= 0:
            self.add_message("Вы не отравлены — противоядие не нужно",
                             GREEN_MSG)
            return
        self.antidotes -= 1
        self.poison_time = 0.0
        self.add_message("Противоядие выпито — отравление снято!",
                         GREEN_MSG)

    # ---------- сообщения и таблички ----------
