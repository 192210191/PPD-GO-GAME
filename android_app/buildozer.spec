[app]
title = Go Game
package.name = gogame
package.domain = org.gogame
source.dir = app/src
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy==2.2.1,kivymd==1.1.1

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.sdk = 31
android.ndk = 23b
android.arch = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
