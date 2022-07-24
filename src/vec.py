from copy import copy
from typing import Union


class Vec:
    def __init__(self, y: int = 0, x: int = 0) -> None:
        self._y: int = y
        self._x: int = x

    def is_zero(self) -> bool:
        return self._y == 0 and self._x == 0

    @property
    def y(self) -> int:
        return self._y

    @y.setter
    def y(self, value: int) -> None:
        self._y = value

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        self._x = value

    def __add__(self, other: 'Vec') -> 'Vec':
        return Vec(self._y+other._y, self._x+other._x)

    def __sub__(self, other: 'Vec') -> 'Vec':
        return Vec(self._y-other._y, self._x-other._x)

    def __repr__(self) -> str:
        return f'Vec(y:{self._y},x:{self._x})'

    def __eq__(self, other: 'Vec') -> bool:
        return self._y == other._y and self._x == other._x

    def __ne__(self, other: 'Vec') -> bool:
        return not self == other

    def round(self) -> 'Vec':
        return Vec(round(self._y), round(self._x))

    def copy(self) -> 'Vec':
        return copy(self)


def interpolate_pos(start: Vec, end: Vec, slope: Union[Vec, None] = None):
    if slope is None:
        slope = end - start
        length = pow(pow(slope.y, 2) + pow(slope.x, 2), 0.5)
        if length != 0:
            slope.y /= length
            slope.x /= length

    while True:
        pos = start.round()
        yield pos
        if pos == end:
            return
        start += slope
