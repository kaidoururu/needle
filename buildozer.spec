[app]
title = Needle In Haystack
package.name = NeedleInHaystack
package.domain = org.kaidoururu
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
source.exclude_dirs = .buildozer,bin,__pycache__,.git
source.exclude_patterns = *.md,*.zip,hay_save.json,build_log.txt
version = 1.0
requirements = python3==3.10.12,hostpython3==3.10.12,pygame==2.6.1,pyjnius==1.6.1
orientation = portrait
fullscreen = True
android.api = 34
android.minapi = 24
android.ndk = 28c
android.accept_sdk_license = True
android.archs = arm64-v8a
android.allow_backup = True
log_level = 2
warn_on_root = 1

[buildozer]
log_level = 2
warn_on_root = 1
