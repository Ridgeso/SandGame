from copy import copy


class Vec:
    def __init__(self, y: int = 0, x: int = 0) -> None:
        self._y: int = y
        self._x: int = x

    def __iter__(self):
        yield self._y
        yield self._x

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

    def copy(self) -> 'Vec':
        return copy(self)
