from typing import Type, Callable
from functools import wraps
from time import perf_counter

import numpy as np
import pygame as py

from src.vec import *
from src.particle import Particle, Eraser
from values import *


class Chunk:
    def __init__(self,
                 x: int, y: int,
                 width: int, height: int,
                 updated_this_frame: bool = False, should_be_updated_next_frame: bool = True) -> None:
        self.y = y
        self.x = x
        self.width = width
        self.height = height
        self.updated_this_frame = updated_this_frame
        self.should_be_updated_next_frame = should_be_updated_next_frame

    def activate(self) -> None:
        self.should_be_updated_next_frame = True

    def deactivate(self) -> None:
        self.should_be_updated_next_frame = False

    def is_active(self) -> bool:
        return self.updated_this_frame

    def update(self) -> None:
        if self.should_be_updated_next_frame:
            self.updated_this_frame = True
            self.should_be_updated_next_frame = False
        else:
            self.updated_this_frame = False

    def __repr__(self):
        return f"Chunk(x1={self.x},y1={self.y},x1={self.width},y1={self.height})"

    def draw_debug_chunk(self, win):
        color = 0x00FF00 if self.updated_this_frame else 0xFF0000
        py.draw.rect(win, color, ((self.y*SCALE, self.x*SCALE), (self.height*SCALE, self.width*SCALE)), 1)


class Board(np.ndarray):
    def __new__(cls, y: int, x: int) -> 'Board':
        return super().__new__(cls, (y, x), dtype=object)

    def in_bounds(self, y: int, x: int) -> bool:
        return 0 <= y < self.shape[0] and 0 <= x < self.shape[1]

    def swap(self, cell: Particle, y: int, x: int) -> None:
        temp = self[cell.pos.y, cell.pos.x]
        if temp is None:
            breakpoint()
        self[cell.pos.y, cell.pos.x] = self[y, x]
        self[y, x] = temp

        if self[cell.pos.y, cell.pos.x] is not None:
            self[cell.pos.y, cell.pos.x].pos = cell.pos

        self[y, x].pos = Vec(y, x)


class Brush:
    def __init__(self, pen: Type[Particle]) -> None:
        self._pen: Type[Particle] = pen
        self._pen_size: int = PAINT_SCALE
        self.PendDifference: int = self._pen_size
        self.last_mouse_position: Union[Vec, None] = Vec()

    @property
    def pen(self) -> Type[Particle]:
        return self._pen

    @pen.setter
    def pen(self, value: Type[Particle]) -> None:
        self._pen = value

    @property
    def pen_size(self) -> int:
        return self._pen_size

    @pen_size.setter
    def pen_size(self, value: int):
        if value > 0:
            self._pen_size = value
            self.PendDifference = value

    def paint_point(self, board: Board, point: Vec) -> None:
        if not board.in_bounds(point.y, point.x):
            return
        if self.pen.is_valid(board[point.y, point.x]):
            board[point.y, point.x] = self.pen(point.y, point.x)

    def paint_from_to(self, board: Board, start: Vec, end: Vec, slope: Union[Vec, None] = None) -> None:
        for pos in interpolate_pos(start, end, slope):
            self.paint_point(board, pos)

    def paint(self, board: Board, pos: Vec) -> None:
        # pos = Vec(*py.mouse.get_pos())
        pos.y, pos.x = pos.x, pos.y

        pos.y //= SCALE
        pos.x //= SCALE

        if self.last_mouse_position is None:
            self.last_mouse_position = Vec(pos.y, pos.x)
        slope = pos - self.last_mouse_position
        length = pow(pow(slope.y, 2) + pow(slope.x, 2), 0.5)
        if length != 0:
            slope.y /= length
            slope.x /= length

        # drawing cross that expends over the gap between the brush positions
        for offset in range(-self.pen_size, self.pen_size):
            y = Vec(offset, 0)
            point_y = pos + y
            last_point_y = self.last_mouse_position + y
            self.paint_from_to(board, last_point_y, point_y, slope)

            x = Vec(0, offset)
            point_x = pos + x
            last_point_x = self.last_mouse_position + x
            self.paint_from_to(board, last_point_x, point_x, slope)

        # drawing a circle at the previous point and the current point
        for y in range(-self.pen_size, self.pen_size):
            offset = pow((pow(self.pen_size, 2) - pow(y, 2)), 0.5)
            offset = round(offset)
            for x in range(-offset, offset):
                r_phi = Vec(y, x)
                point = pos + r_phi
                last_point = self.last_mouse_position + r_phi
                self.paint_point(board, point)
                self.paint_point(board, last_point)

        self.last_mouse_position = pos

    def erase(self, board: Board) -> None:
        pen = self.pen
        self.pen = Eraser
        self.paint(board)
        self.pen = pen


# Debug
def timeit(log: str = ""):
    def profile(f: Callable):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start = perf_counter()
            f(*args, **kwargs)
            end = 1000 * (perf_counter() - start)
            print(log, f"{end:.03f} ms | AT [{f.__name__}]")
        return wrapper
    return profile
