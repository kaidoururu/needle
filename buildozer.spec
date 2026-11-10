[app]
title = Needle In Haystack
package.name = needle
package.domain = org.yourname
source.dir = .
source.include_exts = py,png,jpg
version = 1.0

# Interlocked pins (tested pygame setup): python3 3.10.12 + pyjnius 1.5.0 +
# kivy 2.3.0 + p4a 2023.5.21 (pinned in the workflow). Do not change one alone.
requirements = python3==3.10.12,hostpython3==3.10.12,pyjnius==1.5.0,kivy==2.3.0,pygame

orientation = portrait
fullscreen = True

android.archs = arm64-v8a
android.api = 34
android.minapi = 24
android.ndk = 27c
android.accept_sdk_license = True

source.exclude_dirs = .buildozer,bin,__pycache__,.git
source.exclude_patterns = *.md,*.zip,build_log.txt,hay_save.json

[buildozer]
log_level = 2
warn_on_root = 1
