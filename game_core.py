# -*- coding: utf-8 -*-
# Ядро игры: класс Game собирается из примесей.

import pygame

from game_config import *
from game_field import FieldMixin
from game_health import HealthMixin
from game_effects import EffectsMixin
from game_economy import EconomyMixin
from game_ui import UIMixin
from game_drawings import DrawingsMixin
from game_shop import ShopMixin
from game_help import HelpMixin
from game_screens import ScreensMixin
from game_digging import DiggingMixin
from game_loop import LoopMixin
from game_save import SaveMixin


class Game(SaveMixin, FieldMixin, HealthMixin, EffectsMixin, EconomyMixin,
           UIMixin, DrawingsMixin, ShopMixin, HelpMixin, ScreensMixin,
           DiggingMixin, LoopMixin):
    """Игра «Игла в стоге сена»."""

    def __init__(self):
        pygame.init()
        pygame.font.init()
        pygame.display.set_caption("Игла в стоге сена")
        self.screen = pygame.display.set_mode((720, 1280),
                                              pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.font_big = None
        self.font_mid = None
        self.font_small = None
        self.font_shop_head = None
        self.font_shop_desc = None
        self.make_fonts()

        self.level = 1
        self.field_rect = pygame.Rect(0, 0, 0, 0)
        self.cols = 0
        self.rows = 0
        self.cw = 0.0
        self.ch = 0.0
        self.cells = []
        self.needle_idx = -1
        self.won = False
        self.dead = False
        self.needle_found = False
        self.time = 0.0

        self.money = 0
        self.hay = 0
        self.hay_value = 0
        self.shovel = 1
        self.cap_lvl = 0
        self.regen_lvl = 0
        self.price_lvl = 0
        self.health_lvl = 0
        self.bnd_lvl = 0
        self.bandages = 0
        self.antidotes = 0
        self.poison_time = 0.0
        self.max_stamina = float(STAMINA_BASE)
        self.stamina = self.max_stamina
        self.max_health = float(HEALTH_BASE)
        self.health = self.max_health
        self.digs = 0

        # новые механики: редкие находки, серия, золотая игла
        self.compass_hint = None
        self.magnet_ready = False
        self.clover_time = 0.0
        self.streak = 0
        self.golden_needle = False

        # вспышки экрана: плотность 0..1, затухают со временем
        self.bite_flash = 0.0
        self.poison_flash = 0.0

        self.messages = []
        self.notice = None
        self.straws = []

        self.help_slide = 0.0
        self.help_target = 0.0
        self.help_surf = None
        self.help_panel_h = 0

        self.shop_slide = 0.0
        self.shop_target = 0.0
        self.shop_panel_h = 0
        self.shop_surf = None

        self.text_cache = {}
        self.icon_cache = {}
        self.field_surf = None
        self.field_dirty = True

        self.main_buttons = {}
        self.shop_buttons = {}
        self.win_buttons = {}
        self.death_buttons = {}
        self.build_field()
        self.build_ui()
        self.load_game()          # прогресс из hay_save.json
        self.stamina = self.max_stamina
        self.health = self.max_health



    def make_fonts(self):
        try:
            self.font_big = pygame.font.SysFont("arial", 52, bold=True)
            self.font_mid = pygame.font.SysFont("arial", 30)
            self.font_small = pygame.font.SysFont("arial", 24)
            self.font_shop_head = pygame.font.SysFont("arial", 34, bold=True)
            self.font_shop_desc = pygame.font.SysFont("arial", 24)
        except Exception:
            self.font_big = pygame.font.Font(None, 58)
            self.font_mid = pygame.font.Font(None, 34)
            self.font_small = pygame.font.Font(None, 28)
            self.font_shop_head = pygame.font.Font(None, 40)
            self.font_shop_desc = pygame.font.Font(None, 28)
        self.text_cache = {}
        self.help_surf = None
        self.shop_surf = None



    def txt(self, string, font, color=TEXT):
        key = (id(font), string, color)
        surf = self.text_cache.get(key)
        if surf is None:
            surf = font.render(string, True, color)
            self.text_cache[key] = surf
        return surf

    # ---------- стог ----------
