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
from fourwire import FourWire

from adafruit_st7789 import ST7789

BORDER_WIDTH = 28
TEXT_SCALE = 3

# Release any resources currently in use for the displays
displayio.release_displays()

# built-in, silkscreen labelled SPI bus
spi = board.SPI()
tft_cs = board.D5
tft_dc = board.D6
tft_rst = board.D9

# If using a Raspberry Pi Pico or Pico-w
# Uncomment the below code to use GP (General Purpose) pins
# instead of D (Digital)

# import busio
# spi = busio.SPI(board.GP2, board.GP3, board.GP4)
# tft_cs = board.GP5
# tft_dc = board.GP6
# tft_rst = board.GP7

display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_rst)

display = ST7789(display_bus, width=320, height=172, colstart=34, rotation=270)

# Make the display context
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(display.width, display.height, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0x00FF00  # Bright Green
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)

# Draw a smaller inner rectangle
inner_bitmap = displayio.Bitmap(
    display.width - (BORDER_WIDTH * 2), display.height - (BORDER_WIDTH * 2), 1
)

inner_palette = displayio.Palette(1)
inner_palette[0] = 0xAA0088  # Purple
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=BORDER_WIDTH, y=BORDER_WIDTH
)
splash.append(inner_sprite)

# Draw a label
text_area = label.Label(
    terminalio.FONT,
    text="Hello World!",
    color=0xFFFF00,
    scale=TEXT_SCALE,
    anchor_point=(0.5, 0.5),
    anchored_position=(display.width // 2, display.height // 2),
)
splash.append(text_area)

while True:
    pass
