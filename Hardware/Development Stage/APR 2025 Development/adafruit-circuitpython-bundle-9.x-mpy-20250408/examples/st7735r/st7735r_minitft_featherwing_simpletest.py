# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
This test will initialize the display using displayio and draw a solid green
background, a smaller purple rectangle, and some yellow text.
"""

import board
import displayio
import terminalio
from adafruit_display_text import label
from adafruit_seesaw.seesaw import Seesaw
from fourwire import FourWire

from adafruit_st7735r import ST7735R

# Release any resources currently in use for the displays
displayio.release_displays()

reset_pin = 8
i2c = board.I2C()  # uses board.SCL and board.SDA
# i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
ss = Seesaw(i2c, 0x5E)
ss.pin_mode(reset_pin, ss.OUTPUT)

spi = board.SPI()
tft_cs = board.D5
tft_dc = board.D6

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs)

ss.digital_write(reset_pin, True)
display = ST7735R(display_bus, width=160, height=80, colstart=24, rotation=270, bgr=True)

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(160, 80, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green

bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(150, 70, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088  # Purple
inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=5, y=5)
splash.append(inner_sprite)

# Draw a label
text_group = displayio.Group(scale=2, x=11, y=40)
text = "Hello World!"
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFF00)
text_group.append(text_area)  # Subgroup for text scaling
splash.append(text_group)

while True:
    pass
