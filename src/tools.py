from typing import Type, Callable, Iterator, Optional, Any, Union
from functools import wraps
from time import perf_counter
import math

import glm
import numpy as np
import pygame as py

from values import *
Particle = Type['Particle']


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

    def __repr__(self) -> str:
        return f"Chunk(y={self.x},x={self.y},h={self.width},w={self.height})"

    def draw_debug_chunk(self, win) -> None:
        color = 0x00FF00 if self.updated_this_frame else 0xFF0000
        py.draw.rect(win, color, ((self.y*SCALE, self.x*SCALE), (self.height*SCALE, self.width*SCALE)), 1)


class Board(np.ndarray):
    def __new__(cls, y: int, x: int) -> 'Board':
        return super(Board, cls).__new__(cls, (y, x), dtype=object)

    def in_bounds(self, y: int, x: int) -> bool:
        return 0 <= y < self.shape[0] and 0 <= x < self.shape[1]

    def swap(self, cell: Particle, y: int, x: int) -> None:
        self[cell.pos.y, cell.pos.x] = self[y, x]
        self[y, x] = cell

        if self[cell.pos.y, cell.pos.x] is not None:
            self[cell.pos.y, cell.pos.x].pos = cell.pos

        cell.pos = glm.ivec2(x, y)


class Brush:
    def __init__(self, pen: Type[Particle]) -> None:
        self._pen: Type[Particle] = pen
        self._pen_size: int = PAINT_SCALE
        self.PendDifference: int = self._pen_size
        self.last_mouse_on_board_position: Optional[glm.ivec2] = None

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
    def pen_size(self, value: int) -> None:
        if value > 0:
            self._pen_size = value
            self.PendDifference = value

    def paint_point(self, board: Board, point: glm.ivec2) -> None:
        if not board.in_bounds(point.y, point.x):
            return
        if self.pen.is_valid(board[point.y, point.x]):
            board[point.y, point.x] = self.pen(point.y, point.x)

    def paint_from_to(self, board: Board, start: Union[glm.vec2, glm.ivec2], end: Union[glm.vec2, glm.ivec2],
                      slope: Optional[glm.vec2] = None) -> None:
        for pos in interpolate_pos(start, end, slope):
            self.paint_point(board, pos)

    def paint(self, board: Board, pos: glm.ivec2) -> None:
        pos = glm.ivec2(pos)

        pos /= SCALE

        if self.last_mouse_on_board_position is None:
            self.last_mouse_on_board_position = glm.ivec2(pos)
        slope = glm.vec2(pos - self.last_mouse_on_board_position)
        if slope != glm.vec2():
            slope = glm.normalize(slope)

        # drawing cross that expends over the gap between the brush positions
        for offset in range(-self.pen_size, self.pen_size):
            y = glm.ivec2(0, offset)
            point_y = pos + y
            last_point_y = self.last_mouse_on_board_position + y
            self.paint_from_to(board, last_point_y, point_y, slope)

            x = glm.ivec2(offset, 0)
            point_x = pos + x
            last_point_x = self.last_mouse_on_board_position + x
            self.paint_from_to(board, last_point_x, point_x, slope)

        # drawing a circle at the previous point and the current point
        for y in range(-self.pen_size, self.pen_size):
            offset = pow((pow(self.pen_size, 2) - pow(y, 2)), 0.5)
            offset = round(offset)
            for x in range(-offset, offset):
                r_phi = glm.ivec2(y, x)
                point = pos + r_phi
                last_point = self.last_mouse_on_board_position + r_phi
                self.paint_point(board, point)
                self.paint_point(board, last_point)

        self.last_mouse_on_board_position = pos
        

def interpolate_pos(start: Union[glm.vec2, glm.ivec2], end: Union[glm.vec2, glm.ivec2],
                    slope: Optional[glm.vec2] = None) -> Iterator[glm.ivec2]:
    if slope is None:
        slope = glm.vec2(end - start)
        length = glm.length(slope)
        if length:
            slope = glm.normalize(slope)
    else:
        length = glm.length(glm.vec2(end - start))

    for i in range(round(length) + 1):
        yield start + glm.ivec2(glm.round(slope * i))


def interpolate_pos_dda(start: Union[glm.vec2, glm.ivec2], end: Union[glm.vec2, glm.ivec2],
                        slope: Optional[glm.vec2] = None) -> Iterator[glm.ivec2]:
    """
    Generate position vector for each cell along the path
    :param start: Starting cell
    :param end: Target Cell
    :param slope: unit slope vector
    :returns: glm.ivec2
    """

    if slope is None and (slope := end - start) != glm.vec2():
        slope = glm.normalize(glm.vec2(slope))

    # Moving through cells
    cell_direction = glm.ivec2(1 if slope.x > 0. else -1,
                               1 if slope.y > 0. else -1)

    # Moving through plane
    dx = slope.x/slope.y if slope.y != 0.0 else math.inf
    dy = slope.y/slope.x if slope.x != 0.0 else math.inf
    unit_distance = glm.vec2(glm.length(glm.vec2(1, dy)),  # dx for 1x
                             glm.length(glm.vec2(1, dx)))  # dy for 1y

    # 1st position
    yield glm.ivec2(start)

    current_cell = glm.ivec2(start)
    end = glm.ivec2(end)
    distances = glm.vec2(unit_distance)
    while current_cell != end:
        if distances.y < distances.x:
            current_cell.y += cell_direction.y
            distances.y += unit_distance.y
        else:
            current_cell.x += cell_direction.x
            distances.x += unit_distance.x

        yield glm.ivec2(current_cell)


# Debug
class Timeit:
    def __init__(self, log: str = "", max_time: bool = False, min_time: bool = False, avg_time: bool = False) -> None:
        self.log = f"[{log:<15}] | AT"

        self.max_time = max_time
        self.min_time = min_time
        self.avg_time = avg_time
        
        self.avg_counter = 0.0

        self.max_time_spent = 0
        self.min_time_spent = 1_000_000
        self.avg_time_spent = 0.0

    def __call__(self, f: Callable[[Any, ...], Any]) -> Callable[[Any, ...], Any]:
        self.log += f"[{f.__name__:<15}]" + " | {:7.03f} ms"

        @wraps(f)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Function
            start = perf_counter()
            result = f(*args, **kwargs)
            end = perf_counter()
            end = 1000 * (end - start)

            # Logging
            log = self.log.format(end)
            if self.max_time:
                self.max_time_spent = max(end, self.max_time_spent)
                log += f" | Max {self.max_time_spent: 7.03f}"
            if self.min_time:
                self.min_time_spent = min(end, self.min_time_spent)
                log += f" | Min {self.min_time_spent: 7.03f}"
            if self.avg_time:
                self.avg_counter += 1.0
                self.avg_time_spent += end
                avg = self.avg_time_spent / self.avg_counter
                log += f" | Avg {avg: 7.03f}"
            print(log)

            return result
        return wrapper
