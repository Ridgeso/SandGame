cimport numpy as np
import numpy as np

import pygame as py
from src import convert
from values import *
from cver.cparticle import *


class Board(np.ndarray):
    def __new__(cls, int x, int y):
        return super().__new__(cls, (x, y), dtype=np.object)
    
    def check_spot(self, int x, int y):
        return 0 <= x < self.shape[0] and 0 <= y < self.shape[1]


cdef class Brush:
    cdef _pen
    cdef int pen_size

    def __cinit__(self, pen):
        self._pen = pen
        self.pen_size = PAINT_SCALE
    
    @property
    def pen(self):
        return self._pen
    
    @pen.setter
    def pen(self, value):
        self._pen = value
    
    cpdef int get_pen_size(self):
        return self.pen_size
    
    cpdef void set_pen_size(self, int value):
        if value > 0:
            self.pen_size = value

    cpdef void paint(self, np.ndarray board):
        cdef int pos_x, pos_y
        cdef x, y

        pos_x, pos_y = py.mouse.get_pos()
        pos_y /= SCALE
        pos_x /= SCALE

        for x in range(-self.get_pen_size(), self.get_pen_size()):
            for y in range(-self.get_pen_size(), self.get_pen_size()):
                if not board.check_spot(pos_y+y, pos_x+x):
                    continue
                if self.pen.is_valid_spot(board[pos_y+y][pos_x+x]):
                    board[pos_y+y][pos_x+x] = self.pen(pos_y+y, pos_x+x)


ctypedef enum MouseKey:
    Left = 0,
    Scroll = 1,
    Right = 2


class Display:

    def __init__(self, int x, int y):
        self.win_x = x
        self.win_y = y

        self.win = py.display.set_mode((self.win_x, self.win_y))

        self.board = Board(BOARDY, BOARDX)
        self.brush = Brush(Sand)
    

    def paint_particles(self):
        cdef bint[3] mouse_button_pressed

        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        keys = py.key.get_pressed()

        if mouse_button_pressed[<int> Left]:
            self.brush.paint(self.board)

        if mouse_button_pressed[<int> Scroll]:
            self.brush.pen = Sand
        elif mouse_button_pressed[<int> Right]:
            self.brush.pen = Water
        elif keys[py.K_q]:
            self.brush.pen = Wood
        elif keys[py.K_w]:
            self.brush.pen = Eraser
        elif keys[py.K_e]:
            self.brush.pen = Fire
        elif keys[py.K_r]:
            self.brush.pen = Smoke
        
        if keys[py.K_LEFTBRACKET]:
            size = self.brush.get_pen_size() - 1
            self.brush.set_pen_size(size)
        elif keys[py.K_RIGHTBRACKET]:
            size = self.brush.get_pen_size() + 1
            self.brush.set_pen_size(size)
        
    def draw_cursor(self):
        py.draw.circle(self.win, (66, 66, 66), py.mouse.get_pos(), SCALE*self.brush.get_pen_size(), 2)

    def fill(self, tuple color):
        self.win.fill(color)

    def update(self):
        cdef np.ndarray level
        for level in reversed(self.board):
            for cell in reversed(level):
                if cell is not None:
                    cell.update_frame(self.board)

    def redraw(self):
        cdef np.ndarray level
        for level in reversed(self.board):
            for cell in reversed(level):
                if cell is not None:
                    cell.draw(self.win)


    def map_colors(self):
        cdef int offset_y, offset_x, i, j

        which_color = {"Sand": 0, "Water": 0, "Wood": 0, "Fire": 0, "Smoke": 0}

        data, offset_y, offset_x = convert.convert_img()
        for i, pixels in enumerate(data):
            for j, pixel in enumerate(pixels):
            
                for color in COLORS:
                    pos_difference = COLORS[color] - pixel[:3]
                    which_color[color] = min(map(lambda v: v[0]*v[0] + v[1]*v[1] + v[2]*v[2], pos_difference))

                best_pixel = COLORS_OBJ[min(which_color, key=which_color.get)]
                try:
                    self.board[offset_y+i][offset_x+j] = best_pixel(offset_y+i, offset_x+j)
                except IndexError:
                    print(offset_y+i, offset_x+j)
                    return
