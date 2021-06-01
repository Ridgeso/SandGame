import pygame as py
import numpy as np
import convert
from values import *
from particle import (
    Sand,
    Water,
    Wood,
    Fire,
    Smoke,
    Eraser,
    COLORS_OBJ
)

board = [[0]*(BOARDX) for _ in range(BOARDY)]
current_brush = Sand


def paint_particles():
    global current_brush
    if py.mouse.get_pressed()[0]:
        current_brush.paint(board)

    if py.mouse.get_pressed()[1]:
        current_brush = Sand
    if py.mouse.get_pressed()[2]:
        current_brush = Water
    if py.key.get_pressed()[113]:
        current_brush = Wood
    if py.key.get_pressed()[119]:
        current_brush = Eraser
    if py.key.get_pressed()[101]:
        current_brush = Fire
    if py.key.get_pressed()[114]:
        current_brush = Smoke


def redraw(win, sim):
    global current_brush
    win.fill((0, 0, 0))

    for level in reversed(board):
        for cell in level:
            if not isinstance(cell, int):
                if sim:
                    cell.update_frame(board)
                cell.draw(win)

    py.display.flip()


def map_colors():
    data, offset_y, offset_x = convert.convert_img()
    which_color = {"Sand": 0, "Water": 0, "Wood": 0, "Fire": 0, "Smoke": 0}
    for i, pixels in enumerate(data):
        for j, pixel in enumerate(pixels):
            pixel = sum([pow(int(p), 2) for p in np.nditer(pixel)])
            for color in COLORS_MEDIAN:
                which_color[color] = abs(COLORS_MEDIAN[color] - pixel)
            try:
                color = COLORS_OBJ[min(which_color, key=which_color.get)]
                board[offset_y+i][offset_x+j] = color(offset_y+i, offset_x+j)
            except:
                print(min(COLORS_MEDIAN))
                print(offset_y+i, offset_x+j)
                return
