[app]

# Change these three for your app. package.domain + package.name become the
# Android application id, which is permanent once published.
title = Pygame App
package.name = pygameapp
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
source.include_patterns = src/**/*.py,assets/**/*
version = 0.1

# The first four are pinned as a set and must move together with the p4a
# commit in docker/dockerfile.android. See the README. Everything from
# "pygame" onward is your app's own dependencies; replace as needed.
requirements = python3==3.10.12,kivy==2.3.0,pyjnius==1.5.0,hostpython3==3.10.12,pygame,android,requests,certifi

orientation = landscape, portrait
fullscreen = 1

android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

# Keep this list as small as your app can tolerate. Some permissions carry
# real cost: MANAGE_EXTERNAL_STORAGE, for instance, triggers a Play Store
# review requirement.
android.permissions = INTERNET,ACCESS_NETWORK_STATE

icon.filename = icon.png
presplash.filename = presplash.png
android.presplash_color = #000000

# FileProvider wiring, needed only if your app shares files with other apps.
# Drop both lines and docker/patch_manifest.py if you don't. See the README.
android.add_resources = res/xml/file_paths.xml:xml/file_paths.xml
android.gradle_dependencies = androidx.core:core:1.6.0

p4a.source_dir = /p4a

# Default is an AAB. An APK is what you sideload.
android.release_artifact = apk
android.keystore = keystore/release.keystore
android.keyalias = release

[buildozer]
log_level = 2
warn_on_root = 1
