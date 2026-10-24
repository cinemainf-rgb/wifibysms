[app]
title = Fazlaka Net
package.name = fazlakanet
package.domain = org.fazlaka
source.include_exts = py,png,jpg,kv,atlas
source.dir = .
version = 1.0
requirements = python3,kivy,routeros_api
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, BLUETOOTH, BLUETOOTH_ADMIN
android.api = 31
android.minapi = 21
android.ndk = 23b
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
