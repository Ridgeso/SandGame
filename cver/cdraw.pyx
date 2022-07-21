from enum import IntEnum
import numpy as np

import pygame as py
from src import convert
from values import *
from cver.cparticle import *


class Board(np.ndarray):
    def __new__(cls, x, y):
        return super().__new__(cls, (x, y), dtype=np.object)
    
    def check_spot(self, x, y):
        return 0 <= x < self.shape[0] and 0 <= y < self.shape[1]


class Brush:
    def __init__(self, pen):
        self.pen = pen
        self.pen_size = PAINT_SCALE
    
    @property
    def pen(self):
        return self._pen
    
    @pen.setter
    def pen(self, value):
        self._pen = value
    
    @property
    def pen_size(self):
        return self.pen_size
    
    @pen_size.setter
    def pen_size(self, value):
        if value > 0:
            self.pen_size = value

    def paint(self, board):
        pos_x, pos_y = py.mouse.get_pos()
        pos_y //= SCALE
        pos_x //= SCALE

        for x in range(-self.pen_size, self.pen_size):
            for y in range(-self.pen_size, self.pen_size):
                if not board.check_spot(pos_y+y, pos_x+x):
                    continue
                if self.pen.is_valid_spot(board[pos_y+y][pos_x+x]):
                    board[pos_y+y][pos_x+x] = self.pen(pos_y+y, pos_x+x)


class Display:

    def __init__(self, x, y):
        self.win_x = x
        self.win_y = y

        self.win = py.dispaly.set_mode((self.win_x, self.win_y))

        self.board = Board(BOARDY, BOARDX)
        self.brush = Brush(Sand)
    
    class MouseKey(IntEnum):
        Left = 0
        Scroll = auto()
        Right = auto()

    def paint_particles(self):
        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        keys = py.key.get_pressed()

        if mouse_button_pressed[self.MouseKey.Left]:
            self.brush.paint(self.board)

        if mouse_button_pressed[self.MouseKey.Scroll]:
            current_brush = Sand
        elif mouse_button_pressed[self.MouseKey.Right]:
            current_brush = Water
        elif keys[py.K_q]:
            current_brush = Wood
        elif keys[py.K_w]:
            current_brush = Eraser
        elif keys[py.K_e]:
            current_brush = Fire
        elif keys[py.K_r]:
            current_brush = Smoke
        
        if keys[py.K_LEFTBRACKET]:
            self.brush.pen_size -= 1
        elif keys[py.K_RIGHTBRACKET]:
            self.brush.pen_size += 1
        
    def draw_cursor(self):
        py.draw.cirlce(self.win, (66, 66, 66), py.mouse.get_pos(), SCALE*self.brush.pen_size, 2)

    def fill(self, color):
        self.win.fill(color)

    def update(self):
        for level in reversed(self.board):
            for cell in level:
                if cell is not None:
                    cell.update_frame(self.board)

    def redraw(self):
        # cdef int i, j
        for i in reversed(range(BOARDY)):
            for j in range(BOARDX):
                cell = board[i][j]
                if cell is not None:
                    cell.draw(self.win)


    def map_colors(self):
        # cdef np.ndarray data
        # cdef int offset_x, offset_y, i, j
        # cdef int pval, v
        obj = ["Sand", "Water", "Wood", "Fire", "Smoke"]

        # cdef int minval, newmin, c, which

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