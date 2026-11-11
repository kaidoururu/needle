# -*- coding: utf-8 -*-
# Игра "Игла в стоге сена" — точка входа.
# Запуск: python main.py
#
# Любой сбой не закрывает игру молча: traceback печатается в консоль
# (на компе) и дописывается в crash_log.txt (на компе — рядом с игрой,
# на APK — в Downloads или во внутренней папке приложения).

import sys
import traceback

from game_config import log_crash


if __name__ == "__main__":
    try:
        from game_core import Game
        Game().run()
    except SystemExit:
        raise                     # штатный выход — не сбой, не логируем
    except KeyboardInterrupt:
        pass                      # Ctrl+C — тоже не сбой
    except BaseException:
        traceback.print_exc()     # видно в консоли, если она есть
        log_crash(traceback.format_exc())  # а это след на телефоне
