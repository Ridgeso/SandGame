import copy
import math
from typing import Union


class Vec:
    def __init__(self, y: Union[int, float] = 0, x: Union[int, float] = 0) -> None:
        self._y: Union[int, float] = y
        self._x: Union[int, float] = x

    def is_zero(self) -> bool:
        return self._y == 0 and self._x == 0

    @property
    def y(self) -> Union[int, float]:
        return self._y

    @y.setter
    def y(self, value: Union[int, float]) -> None:
        self._y = value

    @property
    def x(self) -> Union[int, float]:
        return self._x

    @x.setter
    def x(self, value: Union[int, float]) -> None:
        self._x = value

    def __add__(self, other: 'Vec') -> 'Vec':
        return Vec(self._y + other._y, self._x + other._x)

    def __sub__(self, other: 'Vec') -> 'Vec':
        return Vec(self._y - other._y, self._x - other._x)

    def __mul__(self, other: Union[int, float]) -> 'Vec':
        return Vec(self._y * other, self._x * other)

    def __repr__(self) -> str:
        y = round(self._y, 2) if type(self._y) is float else self._y
        x = round(self._x, 2) if type(self._x) is float else self._x
        return f'Vec(y:{y},x:{x})'

    def __eq__(self, other: 'Vec') -> bool:
        return self._y == other._y and self._x == other._x

    def __ne__(self, other: 'Vec') -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self._x, self._y))

    def round(self) -> 'Vec':
        return Vec(round(self._y), round(self._x))

    def size(self) -> float:
        return math.pow(self._y, 2) + math.pow(self._x, 2)

    def magnitude(self) -> float:
        return math.sqrt(self.size())

    def normalize(self) -> 'Vec':
        mag = self.magnitude()
        if mag:
            return Vec(self._y/mag, self._x/mag)
        return Vec()

    def copy(self) -> 'Vec':
        return copy.copy(self)
