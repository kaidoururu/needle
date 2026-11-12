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
from game_help import HelpMixin, HELP_PAGES
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
        # пункт 11: на Android окно открывается на весь экран телефона,
        # на ПК — как раньше, окно 720x1280 с изменяемым размером
        if ON_ANDROID:
            self.display = pygame.display.set_mode((0, 0),
                                                   pygame.FULLSCREEN)
        else:
            self.display = pygame.display.set_mode(
                (CANVAS_W, CANVAS_H), pygame.RESIZABLE)
        # виртуальный холст: вся отрисовка идёт в него, в конце кадра
        # он растягивается на дисплей — интерфейс не мельчает на телефоне
        self.screen = pygame.Surface((CANVAS_W, CANVAS_H)).convert()
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
        self.energy_time = 0.0
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
        self.help_page = 0          # открытая страница справки
        self.help_pages = len(HELP_PAGES)
        self.help_nav = {}          # кнопки «НАЗАД»/«ВПЕРЁД» внизу панели

        self.shop_slide = 0.0
        self.shop_target = 0.0
        self.shop_panel_h = 0
        self.shop_surf = None

        self.text_cache = {}
        self.icon_cache = {}
        self.field_surf = None
        self.field_dirty = True
        self._dr_cache = {}
        self._compass_ov = None
        self._fx_cache = {}
        self._ring_cache = {}
        self._coin_cache = {}
        self._notice_panel = None
        self._scaled = None

        # состояния: меню, игра, пауза
        self.state = "menu"
        self.menu_buttons = {}
        self.pause_buttons = {}
        self.has_save = False

        # обучение и подсказки простоя
        self.tut_bandage_done = False
        self.tut_antidote_done = False
        self.tut_shop_done = False
        self.mercy_used = False      # милость судьбы: раз за уровень
        self.tutorial = None
        self.pending_tutorial = {}   # очередь отложенных уроков (п. 10)
        self.idle_time = 0.0
        self.idle_hint = None

        # приветствие «КАК ИГРАТЬ»: показывается при каждом входе из меню
        self.intro_open = False
        self.intro_button = pygame.Rect(0, 0, 0, 0)

        self.main_buttons = {}
        self.shop_buttons = {}
        self.win_buttons = {}
        self.death_buttons = {}
        # сохранение грузится ДО постройки поля (пункт 9): уровень,
        # уроки и улучшения берутся от hay_save.json, и стог сразу
        # собирается от сохранённого уровня, а не от первого
        self.load_game()
        self.build_field()
        self.build_ui()
        self.stamina = self.max_stamina
        self.health = self.max_health



    # ---------- холст и дисплей (пункт 11) ----------

    def canvas_transform(self):
        """Масштаб и смещение холста на реальном дисплее.

        Холст вписывается целиком, по центру, без искажений: всё поле и
        интерфейс остаются видимыми при любом размере экрана."""
        dw, dh = self.display.get_size()
        scale = min(dw / CANVAS_W, dh / CANVAS_H)
        return scale, (dw - CANVAS_W * scale) / 2.0, \
            (dh - CANVAS_H * scale) / 2.0

    def map_to_canvas(self, pos):
        """Точка реального экрана -> точка виртуального холста.

        Нужна, чтобы тапы и клики попадали в кнопки и клетки поля при
        любом масштабе вывода."""
        scale, off_x, off_y = self.canvas_transform()
        x = (pos[0] - off_x) / scale
        y = (pos[1] - off_y) / scale
        return (int(max(0, min(CANVAS_W, x))),
                int(max(0, min(CANVAS_H, y))))

    def draw_canvas(self):
        """Растянуть холст на реальный дисплей (конец кадра)."""
        scale, off_x, off_y = self.canvas_transform()
        size = (max(1, int(CANVAS_W * scale)),
                max(1, int(CANVAS_H * scale)))
        if size == self.screen.get_size():
            out = self.screen
        else:
            out = getattr(self, "_scaled", None)
            if out is None or out.get_size() != size:
                out = pygame.Surface(size).convert()
                self._scaled = out
            pygame.transform.smoothscale(self.screen, size, out)
        self.display.fill((0, 0, 0))
        self.display.blit(out, (int(off_x), int(off_y)))
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

    def start_new_game(self):
        """Полный сброс прогресса: уровень 1, кошелёк пуст."""
        self.level = 1
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
        self.compass_hint = None
        self.compass_quadrant = None
        self.energy_time = 0.0
        self.clover_time = 0.0
        self.streak = 0
        self.won = False
        self.dead = False
        self.needle_found = False
        self.digs = 0
        self.bite_flash = 0.0
        self.poison_flash = 0.0
        self.messages = []
        self.notice = None
        self.straws = []
        self.tut_bandage_done = False
        self.tut_antidote_done = False
        self.tut_shop_done = False
        self.mercy_used = False
        self.tutorial = None
        self.pending_tutorial = {}
        self.idle_time = 0.0
        self.idle_hint = None
        self.build_field()
        self.field_dirty = True
        self.save_game()

    # ---------- стог ----------
