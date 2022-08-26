from typing import Union, Optional
import numpy as np


class Vec:
    def __init__(self, y: Union[np.ndarray, int, float] = 0, x: Optional[Union[int, float]] = 0) -> None:
        if isinstance(y, np.ndarray):
            self._v = y
        else:
            self._v: np.ndarray = np.array([y, x])

    def is_zero(self) -> bool:
        return self._v == np.zeros((2,))

    @property
    def y(self) -> Union[int, float]:
        return self._v[0]

    @y.setter
    def y(self, value: Union[int, float]) -> None:
        self._v[0] = value

    @property
    def x(self) -> Union[int, float]:
        return self._v[1]

    @x.setter
    def x(self, value: Union[int, float]) -> None:
        self._v[1] = value

    def __add__(self, other: 'Vec') -> 'Vec':
        return Vec(self._v + other._v)

    def __sub__(self, other: 'Vec') -> 'Vec':
        return Vec(self._v - other._v)

    def __mul__(self, other: Union[int, float]) -> 'Vec':
        return Vec(self._v * other)

    def __repr__(self) -> str:
        y = round(self._v[0], 2) if self._v[0].dtype == np.float_ else self._v[0]
        x = round(self._v[1], 2) if self._v[1].dtype == np.float_ else self._v[1]
        return f'Vec(y:{y},x:{x})'

    def __eq__(self, other: 'Vec') -> bool:
        return np.array_equal(self._v, other._v)

    def __ne__(self, other: 'Vec') -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self._v[0], self._v[1]))

    def round(self) -> 'Vec':
        return Vec(np.around(self._v).astype(np.int_))

    def size(self) -> float:
        return self._v.dot(self._v)

    def magnitude(self) -> float:
        return np.sqrt(self.size())

    def normalize(self) -> 'Vec':
        mag = self.magnitude()
        if mag:
            return Vec(self._v / mag)
        return Vec()

    def to_float(self) -> 'Vec':
        if self._v.dtype == np.float_:
            return self.copy()
        return Vec(self._v.astype(np.float_))

    def to_int(self) -> 'Vec':
        if self._v.dtype == np.int_:
            return self.copy()
        return Vec(self._v.astype(np.int_))

    def copy(self) -> 'Vec':
        return Vec(self._v.copy())
