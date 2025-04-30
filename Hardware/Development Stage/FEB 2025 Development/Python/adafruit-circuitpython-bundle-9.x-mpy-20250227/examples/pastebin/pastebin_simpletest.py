# SPDX-FileCopyrightText: Copyright (c) 2022 Alec Delaney for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

from os import getenv
import ssl
import wifi
import socketpool
import adafruit_requests as requests
from adafruit_pastebin.pastebin import PasteBin, ExpirationSetting, PrivacySetting

# Get WiFi details and PasteBin keys, ensure these are setup in settings.toml
ssid = getenv("CIRCUITPY_WIFI_SSID")
password = getenv("CIRCUITPY_WIFI_PASSWORD")
auth_key = getenv("auth_key")

wifi.radio.connect(ssid, password)
pool = socketpool.SocketPool(wifi.radio)
session = requests.Session(pool, ssl.create_default_context())

pastebin = PasteBin(session, auth_key)
paste_url = pastebin.paste(
    "This is a test paste!",
    name="My Test Paste",
    expiration=ExpirationSetting.ONE_DAY,
    privacy=PrivacySetting.UNLISTED,
)
print(paste_url)
