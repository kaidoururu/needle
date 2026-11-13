# -*- coding: utf-8 -*-
# Игра "Игла в стоге сена" — точка входа.
# Запуск: python main.py
#
# Любой сбой не закрывает игру молча: сначала отчёт дописывается в
# crash_log.txt (на APK — в Downloads или во внутренней папке), затем
# traceback печатается в консоль. Порядок важен: на APK консоли нет.

import sys
import traceback

from game_config import log_crash, log_trace, ON_ANDROID


if __name__ == "__main__":
    # целевая платформа — только Android: на ПК объясняем и выходим
    if not ON_ANDROID:
        print("Игра только для Android")
        sys.exit(0)
    try:
        log_trace("старт игры")
        from game_core import Game
        Game().run()
    except SystemExit:
        raise                     # штатный выход — не сбой, не логируем
    except KeyboardInterrupt:
        pass                      # Ctrl+C — тоже не сбой
    except BaseException:
        # сначала след на телефоне, потом консоль: на установленном APK
        # stderr бывает закрыт — печать роняла игру до записи в лог,
        # и закрытие оставалось молчаливым без crash_log.txt (r20)
        try:
            log_crash(traceback.format_exc())
        except Exception:
            pass
        try:
            traceback.print_exc()
        except Exception:
            pass
