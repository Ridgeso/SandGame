from typing import Set, Union
import numpy as np
from enum import Enum, auto

from src.vec import Vec
from values import *
import pygame as py
import random


class ParticleType(Enum):
    Particle = 0
    Sand: int = auto()
    Water: int = auto()
    Fire: int = auto()
    Wood: int = auto()
    Smoke: int = auto()
    Eraser: int = auto()


class Particle:
    Iterations: int = 3
    priority: Set[ParticleType] = set()

    def __init__(self, y: int, x: int, is_falling: bool = True, been_updated: bool = False) -> None:
        self.lifetime: int = 0
        self.flammable: bool = False
        self.is_falling: bool = is_falling
        self._pos: Vec = Vec(y, x)
        self.vel: Vec = Vec()
        self.color: np.ndarray = np.array([0, 0, 0])
        self.been_updated = been_updated

    @property
    def pos(self) -> Vec:
        return self._pos

    @pos.setter
    def pos(self, value: Vec) -> None:
        self._pos = value

    def _step(self, board, move: Vec):
        pass

    def on_update(self, board) -> None:
        self.been_updated = True
        move = self.pos.copy()
        for i in range(self.Iterations):
            if not self._step(board, move):
                break

        if move != self.pos:
            board.swap(self, move.y, move.x)
        else:
            self.is_falling = False

    def draw(self, win: py.Surface) -> None:
        py.draw.rect(win, self.color, ((self.pos.x*SCALE, self.pos.y*SCALE), (SCALE, SCALE)), 0)
        self.been_updated = False

    @classmethod
    def id(cls):
        return getattr(ParticleType, cls.__name__)

    @classmethod
    def is_valid(cls, spot: Union[None, 'Particle']) -> bool:
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

    def _step(self, board, move: Vec) -> bool:
        if board.in_bounds(move.y + 1, move.x) and self.is_valid(board[move.y + 1, move.x]):
            self.is_falling = True
            move.y += 1
        elif not self.is_falling:
            return False
        elif board.in_bounds(move.y + 1, move.x + 1) and self.is_valid(board[move.y + 1, move.x + 1]):
            move.y += 1
            move.x += 1
        elif board.in_bounds(move.y + 1, move.x - 1) and self.is_valid(board[move.y + 1, move.x - 1]):
            move.y += 1
            move.x -= 1
        else:
            return False

        if board.in_bounds(self.pos.y, self.pos.x-1):
            left = board[self.pos.y, self.pos.x - 1]
            if left is not None and self.id() == left.id():
                left.is_falling = True
        if board.in_bounds(self.pos.y, self.pos.x+1):
            right = board[self.pos.y, self.pos.x + 1]
            if right is not None and self.id() == right.id():
                right.is_falling = True

        return True


class Water(Particle):
    priority = {ParticleType.Sand, ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Water, self).__init__(y, x)
        self.color = random.choice(COLORS["Water"])

    def _step(self, board, move: Vec) -> bool:
        if board.in_bounds(move.y + 1, move.x) and self.is_valid(board[move.y + 1, move.x]):
            move.y += 1
        elif board.in_bounds(move.y + 1, move.x + 1) and self.is_valid(board[move.y + 1, move.x + 1]):
            move.y += 1
            move.x += 1
        elif board.in_bounds(move.y + 1, move.x - 1) and self.is_valid(board[move.y + 1, move.x - 1]):
            move.y += 1
            move.x -= 1
        elif board.in_bounds(move.y, move.x - 1) and self.is_valid(board[move.y, move.x - 1]):
            move.x -= 1
        elif board.in_bounds(move.y, move.x + 1) and self.is_valid(board[move.y, move.x + 1]):
            move.x += 1
        else:
            return False

        if board.in_bounds(self.pos.y, self.pos.x-1):
            left = board[self.pos.y, self.pos.x - 1]
            if left is not None and ParticleType.Sand == left.id():
                left.is_falling = True
        if board.in_bounds(self.pos.y, self.pos.x+1):
            right = board[self.pos.y, self.pos.x + 1]
            if right is not None and ParticleType.Sand == right.id():
                right.is_falling = True

        return True

    # def on_update(self, board) -> None:
    #     for i in reversed(range(1, self.Iterations)):
    #         if self.pos.y < len(board)-i and not isinstance(board[self.pos.y+i, self.pos.x], (Sand, Wood, Water)):
    #             board[self.pos.y+i, self.pos.x] = Water(self.pos.y+i, self.pos.x)
    #             board[self.pos.y, self.pos.x] = None
    #             return
    #
    #     for i in reversed(range(1, self.Iterations)):
    #         if self.pos.y < len(board)-i:
    #             if self.pos.x >= i and not isinstance(board[self.pos.y+i, self.pos.x-i], (Sand, Wood, Water)):
    #                 board[self.pos.y+i, self.pos.x-i] = Water(self.pos.y+i, self.pos.x-i)
    #                 board[self.pos.y, self.pos.x] = None
    #                 return
    #
    #             elif self.pos.x < len(board[0])-i and not isinstance(board[self.pos.y+i, self.pos.x+i], (Sand, Wood, Water)):
    #                 board[self.pos.y+i, self.pos.x+i] = Water(self.pos.y+i, self.pos.x+i)
    #                 board[self.pos.y, self.pos.x] = None
    #                 return
    #
    #     for i in reversed(range(1, self.Iterations)):
    #         if self.pos.x < len(board[0])-i and not isinstance(board[self.pos.y, self.pos.x+i], (Sand, Wood, Water)):
    #             board[self.pos.y, self.pos.x+i] = Water(self.pos.y, self.pos.x+i)
    #             board[self.pos.y, self.pos.x] = None
    #             return
    #         elif self.pos.x >= i and not isinstance(board[self.pos.y, self.pos.x-i], (Sand, Wood, Water)):
    #             board[self.pos.y, self.pos.x-i] = Water(self.pos.y, self.pos.x-i)
    #             board[self.pos.y, self.pos.x] = None
    #             return


class Wood(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Wood, self).__init__(y, x)
        self.color = random.choice(COLORS["Wood"])
        self.flammable = True
        self.lifetime = 100

    def on_update(self, board) -> None:
        pass


class Fire(Particle):
    priority = {ParticleType.Sand, ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Fire, self).__init__(y, x)
        self.color = random.choice(COLORS["Fire"])
        self.lifetime = random.randint(150, 220)

    def on_update(self, board) -> None:
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

    def __init__(self, y: int, x: int, been_updated: bool = False):
        super(Smoke, self).__init__(y, x, been_updated=been_updated)
        self.color = random.choice(COLORS["Smoke"])
        self.lifetime = random.randint(10, 80)

    def on_update(self, board) -> None:
        if self.been_updated:
            self.been_updated = False
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
    def __new__(cls, *args, **kwargs) -> None:
        return None

    @classmethod
    def is_valid(cls, spot: Union[None, ParticleType]) -> bool:
        return True


COLORS = {
    "Sand": np.array([[76, 70, 50], [74, 68, 48]]),
    "Water": np.array([[28, 163, 236], [32, 169, 229]]),
    "Wood": np.array([[35, 30, 24], [40, 40, 34]]),
    "Fire": np.array([[206, 67, 32], [216, 75, 39]]),
    "Smoke": np.array([[49, 49, 49], [41, 41, 41]])
}
