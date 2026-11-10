[app]

# Название игры, которое видно под иконкой
title = Игла в стоге сена

# Имя пакета: только латиница, без пробелов
package.name = NeedleInHaystack
package.domain = org.yourname

source.dir = .
source.include_exts = py,png,jpg,kv,md

# Версия: для релиза меняйте вручную
version = 1.0

# Зависимости: p4a соберёт pygame из своего рецепта
requirements = python3,pygame

# Портретный режим, полноэкранный, без статуса-бара
orientation = portrait
fullscreen = 1

# Android
android.api = 34
android.minapi = 24
android.archs = arm64-v8a
android.allow_backup = True

# Не включать лишнее в APK (папки, которые не нужны в сборке)
source.exclude_dirs = tests,.git,.buildozer,bin,__pycache__
source.exclude_patterns = hay_save.json,*.apk

# Иконка (положите icon.png 512x512 в корень; пока нет — закомментировано)
# icon.filename = %(source.dir)s/icon.png

# Куда сохранять готовый APK
build_dir = ./.buildozer
bin_name = %(title)s.apk

#
# Строки ниже менять не нужно
#
[buildozer]
log_level = 2
warn_on_root = 1
