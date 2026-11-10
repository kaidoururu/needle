# Карта проекта «Игла в стоге сена»

## Файлы

| Файл | Примесь | Ответственность |
|---|---|---|
| main.py | — | Точка входа: `Game().run()` |
| game_core.py | — | Класс `Game`: собирает примеси, `__init__`, шрифты, кэш текста |
| game_field.py | FieldMixin | Поле клеток, цены, иголка, рестарт, уровни |
| game_health.py | HealthMixin | Укусы, отравление, бинты и противоядия |
| game_effects.py | EffectsMixin | Сообщения, таблички находок, вспышки, соломинки |
| game_economy.py | EconomyMixin | Цены улучшений, продажа сена, покупки |
| game_ui.py | UIMixin | HUD: кнопки, полосы здоровья и сил, монеты |
| game_drawings.py | DrawingsMixin | Рисунки находок и иконки лавки |
| game_shop.py | ShopMixin | Выдвижная лавка улучшений |
| game_help.py | HelpMixin | Выдвижная справка «?» |
| game_screens.py | ScreensMixin | Экраны победы и смерти |
| game_digging.py | DiggingMixin | Ловушки, находки, копание клетки |
| game_save.py | SaveMixin | Сохранение/загрузка прогресса (hay_save.json) |
| game_loop.py | LoopMixin | Обработка событий, клики, главный цикл |

## Зависимости

```
main.py -> game_core.py (Game)
             |
             +-- game_config.py   (константы, импортирует все)
             +-- game_loop.py     (LoopMixin: run, handle_click)
             +-- game_save.py     (SaveMixin: сохранение прогресса)
             +-- game_digging.py  (DiggingMixin: копание, ловушки)
             +-- game_screens.py  (ScreensMixin: победа/смерть)
             +-- game_help.py     (HelpMixin: справка «?»)
             +-- game_shop.py     (ShopMixin: лавка)
             +-- game_drawings.py (DrawingsMixin: рисунки)
             +-- game_ui.py       (UIMixin: HUD)
             +-- game_economy.py  (EconomyMixin: экономика)
             +-- game_effects.py  (EffectsMixin: эффекты)
             +-- game_health.py   (HealthMixin: здоровье)
             +-- game_field.py    (FieldMixin: стог)
```

## Поток игры

1. `main.py` -> `Game.__init__` (game_core) -> `build_field` (game_field) -> `build_ui` (game_ui)
2. `run` (game_loop) крутит цикл: события -> `handle_click` -> `dig_at` (game_digging)
3. `dig_at` -> `resolve_items` -> `trigger_item`: укусы/отравление (game_health),
   вспышки и соломинки (game_effects), находки рисует game_drawings
4. Продажа и покупки: game_economy + game_shop; подсказки: game_help
5. Уровни: `next_level` (game_field); финалы: game_screens

## Отладка

