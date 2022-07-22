from typing import Set, Union
import numpy as np
from enum import Enum, auto

from values import *
import pygame as py
import random


class Vec:
    MaxVel: int = 5

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
        if value < self.MaxVel:
            self._y = value

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, value: int) -> None:
        if value < self.MaxVel:
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


class ParticleType(Enum):
    Particle = 0
    Sand: int = auto()
    Water: int = auto()
    Fire: int = auto()
    Wood: int = auto()
    Smoke: int = auto()
    Eraser: int = auto()


class Particle:
    IterationCount: int = 3
    priority: Set[ParticleType] = set()

    def __init__(self, y: int, x: int) -> None:
        self.lifetime: int = 0
        self.flammable: bool = False
        self._pos: Vec = Vec(y, x)
        self.vel: Vec = Vec()
        self.color: np.ndarray = np.array([0, 0, 0])

    @property
    def pos(self) -> Vec:
        return self._pos

    @pos.setter
    def pos(self, pos: Vec) -> None:
        self._pos = pos

    def update_frame(self, board) -> None:
        pass

    def draw(self, win: py.Surface) -> None:
        py.draw.rect(win, self.color, ((self.pos.x*SCALE, self.pos.y*SCALE), (SCALE, SCALE)), 0)

    @classmethod
    def id(cls):
        return getattr(ParticleType, cls.__name__)

    @classmethod
    def is_valid_spot(cls, spot: Union[None, ParticleType]) -> bool:
        if spot is None:
            return True
        elif spot.id() == cls.id():
            return False
        else:
            return spot.id() not in cls.priority


class Sand(Particle):
    priority = {ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Sand, self).__init__(y, x)
        self.color = random.choice(COLORS["Sand"])

    def update_frame(self, board) -> None:
        # TODO: Refactor Part I
        if self.vel.is_zero():
            self.vel.y = 1
            return

        prev_pos = self.pos
        for i in range(self.IterationCount):
            nex_pos = self.pos + self.vel
            if not board.check_spot(nex_pos.y, nex_pos.x):
                break
            if not self.is_valid_spot(board[nex_pos.y, nex_pos.x]):
                self.vel.y = 0
                break
            prev_pos = nex_pos
            self.vel.y += 1

        if prev_pos != self.pos:
            temp = board[self.pos.y, self.pos.x]
            board[self.pos.y, self.pos.x] = board[prev_pos.y, prev_pos.x]
            board[prev_pos.y, prev_pos.x] = temp
            self.pos = prev_pos

        # for i in reversed(range(1, self.MAX_VELOCITY)):
        #     if self.pos.y+i >= board.shape[0]:
        #         continue
        #     move = board[self.pos.y+i][self.pos.x].id() == self.id() or board[self.pos.y+i][self.pos.x].id() in self.priority
        #     if board[self.pos.y+i][self.pos.x].id() in self.priority:
        #         temp = board[self.pos.y+i, self.pos.x]
        #         board[self.pos.y+i, self.pos.x] = Sand(self.pos.y+i, self.pos.x)
        #         board[self.pos.y, self.pos.x] = temp
        #         return
        #
        # for i in reversed(range(1, self.MAX_VELOCITY)):
        #     if self.pos.y < len(board)-i:
        #         if self.pos.x >= i and not isinstance(board[self.pos.y+i][self.pos.x-i], (Sand, Wood)):
        #             board[self.pos.y+i, self.pos.x-i] = Sand(self.pos.y+i, self.pos.x-i)
        #             board[self.pos.y, self.pos.x] = None
        #             return
        #
        #         elif self.pos.x < len(board[0])-i and not isinstance(board[self.pos.y+i][self.pos.x+i], (Sand, Wood)):
        #             board[self.pos.y+i, self.pos.x+i] = Sand(self.pos.y+i, self.pos.x+i)
        #             board[self.pos.y, self.pos.x] = None
        #             return


class Water(Particle):
    priority = {ParticleType.Sand, ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Water, self).__init__(y, x)
        self.color = random.choice(COLORS["Water"])

    def update_frame(self, board) -> None:
        for i in reversed(range(1, self.IterationCount)):
            if self.pos.y < len(board)-i and not isinstance(board[self.pos.y+i, self.pos.x], (Sand, Wood, Water)):
                board[self.pos.y+i, self.pos.x] = Water(self.pos.y+i, self.pos.x)
                board[self.pos.y, self.pos.x] = None
                return

        for i in reversed(range(1, self.IterationCount)):
            if self.pos.y < len(board)-i:
                if self.pos.x >= i and not isinstance(board[self.pos.y+i, self.pos.x-i], (Sand, Wood, Water)):
                    board[self.pos.y+i, self.pos.x-i] = Water(self.pos.y+i, self.pos.x-i)
                    board[self.pos.y, self.pos.x] = None
                    return

                elif self.pos.x < len(board[0])-i and not isinstance(board[self.pos.y+i, self.pos.x+i], (Sand, Wood, Water)):
                    board[self.pos.y+i, self.pos.x+i] = Water(self.pos.y+i, self.pos.x+i)
                    board[self.pos.y, self.pos.x] = None
                    return

        for i in reversed(range(1, self.IterationCount)):
            if self.pos.x < len(board[0])-i and not isinstance(board[self.pos.y, self.pos.x+i], (Sand, Wood, Water)):
                board[self.pos.y, self.pos.x+i] = Water(self.pos.y, self.pos.x+i)
                board[self.pos.y, self.pos.x] = None
                return
            elif self.pos.x >= i and not isinstance(board[self.pos.y, self.pos.x-i], (Sand, Wood, Water)):
                board[self.pos.y, self.pos.x-i] = Water(self.pos.y, self.pos.x-i)
                board[self.pos.y, self.pos.x] = None
                return


class Wood(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Wood, self).__init__(y, x)
        self.color = random.choice(COLORS["Wood"])
        self.flammable = True
        self.lifetime = 100


class Fire(Particle):
    priority = {ParticleType.Sand, ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Fire, self).__init__(y, x)
        self.color = random.choice(COLORS["Fire"])
        self.lifetime = random.randint(150, 220)

    def update_frame(self, board) -> None:
        if self.lifetime < 0:
            board[self.pos.y, self.pos.x] = Smoke(self.pos.y, self.pos.x)
            return
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 < self.pos.y+i < len(board)-1 and 0 < self.pos.x+j < len(board[0])-1:
                    if isinstance(board[self.pos.y+i, self.pos.x+j], Wood) and self.lifetime < 140:
                        board[self.pos.y+i, self.pos.x+j] = Fire(self.pos.y+i, self.pos.x+j)
                    elif isinstance(board[self.pos.y+i, self.pos.x+j], int) and not random.randint(0, 31):
                        board[self.pos.y+i, self.pos.x+j] = Smoke(self.pos.y+i, self.pos.x+j, False)
        self.lifetime -= 1


class Smoke(Particle):
    priority = {ParticleType.Sand, ParticleType.Water, ParticleType.Wood}

    def __init__(self, y: int, x: int, update: bool = False):
        super(Smoke, self).__init__(y, x)
        self.color = random.choice(COLORS["Smoke"])
        self.lifetime = random.randint(10, 80)
        self.has_been_updated = update

    def update_frame(self, board) -> None:
        if self.has_been_updated:
            self.has_been_updated = False
            return
        if self.lifetime < 0:
            board[self.pos.y, self.pos.x] = None
            return
        self.lifetime -= 1
        new_x = None
        new_y = None
        if self.pos.y >= 1 and board[self.pos.y-1, self.pos.x] is None:
            new_y = self.pos.y-1
            new_x = self.pos.x

        if random.randint(1, 2) % 2:
            if self.pos.y <= 0:
                return

            if self.pos.x > 0 and board[self.pos.y-1, self.pos.x-1] is None:
                new_y = self.pos.y-1
                new_x = self.pos.x-1
            elif self.pos.x < len(board[0])-1 and board[self.pos.y-1, self.pos.x+1] is None:
                new_y = self.pos.y-1
                new_x = self.pos.x+1

        if new_y is not None and new_x is not None:
            board[new_y][new_x] = Smoke(new_y, new_x, True)
            board[self.pos.y, self.pos.x] = None


class Eraser(Particle):
    def __new__(cls, *args, **kwargs):
        return None

    @classmethod
    def is_valid_spot(cls, spot: Union[None, ParticleType]) -> bool:
        return True


COLORS = {
    "Sand": np.array([[76, 70, 50], [74, 68, 48]]),
    "Water": np.array([[28, 163, 236], [32, 169, 229]]),
    "Wood": np.array([[35, 30, 24], [40, 40, 34]]),
    "Fire": np.array([[206, 67, 32], [216, 75, 39]]),
    "Smoke": np.array([[49, 49, 49], [41, 41, 41]])
}

COLORS_OBJ = {
    "Sand": Sand,
    "Water": Water,
    "Wood": Wood,
    "Fire": Fire,
    "Smoke": Smoke
}
