from typing import Tuple
from enum import IntEnum, auto
import numpy as np
import convert

import pygame as py

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


class Display:
    
    def __init__(self, x: int, y: int) -> None:
        self.win_x = x
        self.win_y = y

        self.win = py.display.set_mode((self.win_x, self.win_y))
    
        self.board = [[None]*(BOARDX) for _ in range(BOARDY)]
        self.brush = Sand
        self.brush_size = 1

    class MouseKey(IntEnum):
            Left = 0
            Scrol = auto()
            Right = auto()

    def paint_particles(self) -> None:
        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        if mouse_button_pressed[self.MouseKey.Left]:
            self.brush.paint(self.board)

        if mouse_button_pressed[self.MouseKey.Scrol]:
            self.brush = Sand
        elif mouse_button_pressed[self.MouseKey.Right]:
            self.brush = Water
        
        keys = py.key.get_pressed()
        if keys[py.K_q]:
            self.brush = Wood
        elif keys[py.K_w]:
            self.brush = Eraser
        elif keys[py.K_e]:
            self.brush = Fire
        elif keys[py.K_r]:
            self.brush = Smoke

    def draw_cursor(self) -> None:
        py.draw.circle(self.win, (66, 66, 66), py.mouse.get_pos(), PAINT_SCALE*(SCALE+self.brush_size), 2)

    def fill(self, color: Tuple[int, ...]) -> None:
        self.win.fill(color)

    def update(self) -> None:
        for level in reversed(self.board):
            for cell in level:
                if cell is not None:
                    cell.update_frame(self.board)

    def redraw(self) -> None:
        for level in self.board:
            for cell in level:
                if cell is not None:
                    cell.draw(self.win)

    def map_colors(self) -> None:
        data, offset_y, offset_x = convert.convert_img()
        
        which_color = {"Sand": 0, "Water": 0, "Wood": 0, "Fire": 0, "Smoke": 0}

        for i, pixels in enumerate(data):
            for j, pixel in enumerate(pixels):
                pixel = sum([pow(int(p), 2) for p in np.nditer(pixel)])
        
                for color in COLORS_MEDIAN:
                    which_color[color] = abs(COLORS_MEDIAN[color] - pixel)
        
                try:
                    color = COLORS_OBJ[min(which_color, key=which_color.get)]
                    self.board[offset_y+i][offset_x+j] = color(offset_y+i, offset_x+j)
                except Exception:
                    print(min(COLORS_MEDIAN))
                    print(offset_y+i, offset_x+j)
                    return
