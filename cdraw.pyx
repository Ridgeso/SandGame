import pygame as py
cimport numpy as np
import convert
from values import *
from cparticle import *


board = [[0]*(BOARDX) for _ in range(BOARDY)]
current_brush = Sand


def paint_particles():
    global current_brush
    if py.mouse.get_pressed()[0]:
        current_brush.paint(board, py.mouse.get_pos())

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


def redraw(win, bint sim):
    global current_brush
    cdef int i, j
    for i in reversed(range(BOARDY)):
        for j in range(BOARDX):
            cell = board[i][j]
            if not isinstance(cell, int):
                if sim:
                    cell.update_frame(board)
                py.draw.rect(win, cell.color, ((j*SCALE, i*SCALE), (SCALE, SCALE)), 0)


def map_colors():
    cdef np.ndarray data
    cdef int offset_x, offset_y, i, j
    cdef int pval, v
    obj = ["Sand", "Water", "Wood", "Fire", "Smoke"]

    cdef int minval, newmin, c, which

    data, offset_y, offset_x = convert.convert_img()
    for i, pixels in enumerate(data):
        for j, pixel in enumerate(pixels):
            pval = 0
            which = 0
            for v in pixel:
                pval += v*v
            minval = abs(COLORS_MEDIAN["Sand"] - pval)
            for c in range(1, 5):
                newmin = abs(COLORS_MEDIAN[obj[c]] - pval)
                if newmin < minval:
                    minval = newmin
                    which=c
            color = COLORS_OBJ[obj[which]]
            board[offset_y+i][offset_x+j] = color(offset_y+i, offset_x+j)