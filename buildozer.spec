[app]
title = Needle in the Haystack
package.name = needle
package.domain = org.yourname
source.dir = .
source.include_exts = py,png,jpg
source.exclude_dirs = .buildozer,bin,__pycache__,.git
source.exclude_exts = md,zip,txt
version = 1.0
requirements = python3==3.10.12,hostpython3==3.10.12,pygame==2.6.1,pyjnius==1.6.1
orientation = portrait
fullscreen = True
android.api = 34
android.minapi = 24
android.ndk = 28c
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 1
warn_on_root = 1
