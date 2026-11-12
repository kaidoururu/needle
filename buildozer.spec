[app]
title = Needle In Haystack
package.name = needle
package.domain = org.kaidoururu

source.dir = .
source.include_exts = py,png,jpg
version = 1.2

icon.filename = icon.png

# Проверенные версии (pygame 2.6.1 + Python 3.10.12)
requirements = python3==3.10.12,hostpython3==3.10.12,pygame==2.6.1,pyjnius==1.7.0

# Локальный рецепт лежит в папке p4a-recipes в корне проекта
p4a.local_recipes = p4a-recipes

orientation = portrait
fullscreen = True
android.archs = arm64-v8a
android.api = 34
android.minapi = 24
android.ndk = 27c
android.accept_sdk_license = True

source.exclude_dirs = .buildozer,bin,__pycache__,.git,p4a-recipes
source.exclude_patterns = *.md,*.zip,build_log.txt,hay_save.json

[buildozer]
log_level = 2
warn_on_root = 1
