[app]
title = Needle In Haystack
package.name = needle
package.domain = org.yourname
source.dir = .
source.include_exts = py,png,jpg
version = 1.0

# Pinned stack proven for pygame builds:
# python 3.10.12 (pygame breaks on 3.11+), pyjnius 1.5.0 (compiles with Cython 0.29.x)
requirements = python3==3.10.12,hostpython3==3.10.12,pygame==2.6.1,pyjnius==1.5.0

orientation = portrait
fullscreen = True

android.archs = arm64-v8a
android.api = 34
android.minapi = 24
android.ndk = 28c
# buildozer accepts Android SDK licenses non-interactively
android.accept_sdk_license = True

source.exclude_dirs = .buildozer,bin,__pycache__,.git
source.exclude_patterns = *.md,*.zip,build_log.txt,hay_save.json

[buildozer]
log_level = 2
warn_on_root = 1
