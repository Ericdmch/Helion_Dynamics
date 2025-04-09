# SPDX-FileCopyrightText: Copyright (c) 2025 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
import array

import displayio
import supervisor
import terminalio
import usb.core
from adafruit_display_text.bitmap_label import Label
from displayio import Group, OnDiskBitmap, TileGrid
from tilepalettemapper import TilePaletteMapper

import adafruit_usb_host_descriptors

display = supervisor.runtime.display

main_group = Group()
display.root_group = main_group

mouse_bmp = OnDiskBitmap("mouse_cursor.bmp")

output_lbls = []
mouse_tgs = []
palette_mappers = []
color_converter = displayio.ColorConverter()
colors = [0xFF00FF, 0x00FF00]
remap_palette = displayio.Palette(3 + len(colors))
remap_palette.make_transparent(0)

# copy the 3 colors from mouse palette
for i in range(3):
    remap_palette[i] = mouse_bmp.pixel_shader[i]

# add the two extra colors to the palette
for i in range(2):
    remap_palette[i + 3] = colors[i]

for i in range(2):
    palette_mapper = TilePaletteMapper(remap_palette, 3, 1, 1)
    palette_mapper[0] = [0, 1, i + 3]
    palette_mappers.append(palette_mapper)
    mouse_tg = TileGrid(mouse_bmp, pixel_shader=palette_mapper)
    mouse_tg.x = display.width // 2 - (i * 12)
    mouse_tg.y = display.height // 2
    mouse_tgs.append(mouse_tg)
    main_group.append(mouse_tg)

    output_lbl = Label(terminalio.FONT, text=f"{mouse_tg.x},{mouse_tg.y}", color=colors[i], scale=1)
    output_lbl.anchor_point = (0, 0)
    output_lbl.anchored_position = (1, 1 + i * 13)
    output_lbls.append(output_lbl)
    main_group.append(output_lbl)

mouse_interface_indexes = []
mouse_endpoint_addresses = []
mice = []

# scan for connected USB devices
for device in usb.core.find(find_all=True):
    mouse_interface_index, mouse_endpoint_address = (
        adafruit_usb_host_descriptors.find_boot_mouse_endpoint(device)
    )
    if mouse_interface_index is not None and mouse_endpoint_address is not None:
        mouse_interface_indexes.append(mouse_interface_index)
        mouse_endpoint_addresses.append(mouse_endpoint_address)

        mice.append(device)
        print(f"mouse interface: {mouse_interface_index} ", end="")
        print(f"endpoint_address: {hex(mouse_endpoint_address)}")
        if device.is_kernel_driver_active(0):
            device.detach_kernel_driver(0)

        # set the mouse configuration so it can be used
        device.set_configuration()

# This is ordered by bit position.
BUTTONS = ["left", "right", "middle"]

mouse_bufs = []

for mouse_tg in mouse_tgs:
    # Buffer to hold data read from the mouse
    # Boot mice have 4 byte reports
    mouse_bufs.append(array.array("b", [0] * 8))


def get_mouse_deltas(buffer, read_count):
    if read_count == 4:
        delta_x = buffer[1]
        delta_y = buffer[2]
    elif read_count == 8:
        delta_x = buffer[2]
        delta_y = buffer[4]
    else:
        raise ValueError(f"Unsupported mouse packet size: {read_count}, must be 4 or 8")
    return delta_x, delta_y


while True:
    for mouse_index, mouse in enumerate(mice):
        try:
            count = mouse.read(
                mouse_endpoint_addresses[mouse_index], mouse_bufs[mouse_index], timeout=10
            )
        except usb.core.USBTimeoutError:
            continue
        mouse_deltas = get_mouse_deltas(mouse_bufs[mouse_index], count)
        mouse_tgs[mouse_index].x = max(
            0, min(display.width - 1, mouse_tgs[mouse_index].x + mouse_deltas[0])
        )
        mouse_tgs[mouse_index].y = max(
            0, min(display.height - 1, mouse_tgs[mouse_index].y + mouse_deltas[1])
        )

        out_str = f"{mouse_tgs[mouse_index].x},{mouse_tgs[mouse_index].y}"
        for i, button in enumerate(BUTTONS):
            if mouse_bufs[mouse_index][0] & (1 << i) != 0:
                out_str += f" {button}"

        output_lbls[mouse_index].text = out_str
