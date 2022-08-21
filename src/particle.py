from typing import Type, Set, Union
from enum import Enum, auto

import random
import pygame as py

from src.vec import Vec, interpolate_pos
from values import *
Board = Type['Board']


class ParticleType(Enum):
    Particle: int = 0
    Sand: int = auto()
    Water: int = auto()
    Fire: int = auto()
    Wood: int = auto()
    Smoke: int = auto()
    Eraser: int = auto()


class Particle:
    priority: Set[ParticleType] = set()
    Iterations: int = 3

    def __init__(self, y: int, x: int, is_falling: bool = True, been_updated: bool = False) -> None:
        self.has_been_modified = False
        self.color: int = 0

        self.lifetime: float = 0.0
        self.flammable: float = 100.0
        self.heat: float = 0.0
        self.been_updated: bool = been_updated

        self.is_falling: bool = is_falling

        self.pos: Vec = Vec(y, x)

    def _step(self, board: Board, move: Vec) -> bool:
        pass

    def on_update(self, board: Board) -> bool:
        if self.been_updated:
            return False
        self.been_updated = True

        move = self.pos.copy()

        for i in range(self.Iterations):
            stop = self._step(board, move)
            if not stop:
                break
            else:
                self.has_been_modified = True

        if move != self.pos:
            board.swap(self, move.y, move.x)
        else:
            self.is_falling = False

        return self.has_been_modified

    def reset(self) -> None:
        self.been_updated = False
        self.has_been_modified = False

    def push_neighbours(self, board: Board):
        if board.in_bounds(self.pos.y, self.pos.x - 1):
            left = board[self.pos.y, self.pos.x - 1]
            if left is not None and self.id() == left.id():
                left.is_falling = True
        if board.in_bounds(self.pos.y, self.pos.x + 1):
            right = board[self.pos.y, self.pos.x + 1]
            if right is not None and self.id() == right.id():
                right.is_falling = True

    @classmethod
    def id(cls) -> ParticleType:
        return getattr(ParticleType, cls.__name__)

    @classmethod
    def is_valid(cls, spot: Union['Particle', None]) -> bool:
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
        self.friction = 0.75

    def _step(self, board: Board, move: Vec) -> bool:
        if board.in_bounds(move.y + 1, move.x) and self.is_valid(board[move.y + 1, move.x]):
            self.is_falling = True
            move.y += 1
            self.push_neighbours(board)
            return True

        if not self.is_falling:
            return False

        d = -1 if random.randint(0, 1) else 1
        if board.in_bounds(move.y + 1, move.x + d) and self.is_valid(board[move.y + 1, move.x + d]):
            move.y += 1
            move.x += d
        elif board.in_bounds(move.y + 1, move.x - d) and self.is_valid(board[move.y + 1, move.x - d]):
            move.y += 1
            move.x -= d
        else:
            return False

        self.push_neighbours(board)
        return True


class Water(Particle):
    priority = {ParticleType.Sand, ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Water, self).__init__(y, x)
        self.color = random.choice(COLORS["Water"])

    def _step(self, board: Board, move: Vec) -> bool:
        if board.in_bounds(move.y + 1, move.x) and self.is_valid(board[move.y + 1, move.x]):
            move.y += 1
            return True

        d = -1 if random.randint(0, 1) else 1
        if board.in_bounds(move.y + 1, move.x + d) and self.is_valid(board[move.y + 1, move.x + d]):
            move.y += 1
            move.x += d
            return True

        if board.in_bounds(move.y + 1, move.x - d) and self.is_valid(board[move.y + 1, move.x - d]):
            move.y += 1
            move.x -= d
            return True

        if board.in_bounds(move.y + 1, move.x + d) and self.is_valid(board[move.y + 1, move.x + d]):
            move.y += 1
            move.x += d
            return True

        if board.in_bounds(move.y + 1, move.x - d) and self.is_valid(board[move.y + 1, move.x - d]):
            move.y += 1
            move.x -= d
            return True

        if board.in_bounds(move.y, move.x + d) and self.is_valid(board[move.y, move.x + d]):
            move.x += d
            return True

        if board.in_bounds(move.y, move.x - d) and self.is_valid(board[move.y, move.x - d]):
            move.x -= d
            return True

        return False


class Wood(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Wood, self).__init__(y, x)
        self.color = random.choice(COLORS["Wood"])
        self.flammable = 96
        self.lifetime = 100

    def on_update(self, board: Board) -> bool:
        return False


class Fire(Particle):
    priority = {ParticleType.Sand, ParticleType.Water, ParticleType.Wood}

    def __init__(self, y: int, x: int, been_updated: bool = False) -> None:
        super(Fire, self).__init__(y, x, been_updated=been_updated)
        self.original_color = random.choice(COLORS["Fire"])
        self.color = self.original_color
        self.heat = 100
        self.flammable = 1

    def receive_heat(self, cell: Union[Particle, None]) -> None:
        if cell is None:
            self.heat *= 0.99
            return

        if cell.id() == ParticleType.Fire:
            self.heat = (self.heat + cell.heat)/2

        elif cell.id() == ParticleType.Water:
            self.heat = 0

        if self.heat > 100:
            self.heat = 100

    def on_update(self, board: Board) -> bool:
        if self.been_updated:
            return False
        self.been_updated = True

        if self.heat <= 0:
            board[self.pos.y, self.pos.x] = None
            return True

        for i in range(-1, 2):
            for j in range(-1, 2):
                if (i == 0 and j == 0) or not board.in_bounds(self.pos.y + i, self.pos.x + j):
                    continue

                cell = board[self.pos.y + i, self.pos.x + j]
                self.receive_heat(cell)

                self.pos = self.pos.round()
                if cell is None:
                    if not random.randint(0, 51):
                        board[self.pos.y + i, self.pos.x + j] = Smoke(self.pos.y + i, self.pos.x + j, False)
                elif cell.id() == ParticleType.Wood:
                    if random.randint(0, 100) > cell.flammable:
                        board[self.pos.y + i, self.pos.x + j] = Fire(self.pos.y + i, self.pos.x + j, True)

        # self.color = self.original_color - (abs(self.heat)//100)
        self.heat -= 1
        return True


class Smoke(Particle):
    priority = {ParticleType.Sand, ParticleType.Water, ParticleType.Wood}
    Iterations = 1

    def __init__(self, y: int, x: int, been_updated: bool = False) -> None:
        super(Smoke, self).__init__(y, x, been_updated=been_updated)
        self.color = random.choice(COLORS["Smoke"])
        self.lifetime = random.randint(10, 80)

    def _step(self, board: Board, move: Vec) -> bool:
        if self.lifetime < 0:
            board[self.pos.y, self.pos.x] = None
            return False
        self.lifetime -= 1

        if board.in_bounds(move.y - 1, move.x) and board[move.y - 1, move.x] is None:
            move.y -= 1

        d = random.randint(-1, 1)
        if not d:
            return True

        if board.in_bounds(move.y - 1, move.x - d) and board[move.y - 1, move.x - d] is None:
            move.y = move.y - 1
            move.x = move.x - d
        elif board.in_bounds(move.y - 1, move.x + d) and board[move.y - 1, move.x + d] is None:
            move.y = self.pos.y - 1
            move.x = self.pos.x + d

        return True


class Eraser(Particle):
    def __new__(cls, *args, **kwargs) -> None:
        return None

    @classmethod
    def is_valid(cls, spot: Union[ParticleType, None]) -> bool:
        return True


COLORS = {  # R G B  24bits
    "Sand": [0xE4EB15, 0xFFCD18, 0xC1C707, 0xE49009],
    "Water": [0x0F5E9C, 0x1CA3EC, 0x2389DA, 0x5ABCD8],
    "Wood": [0x461F00, 0x643D01, 0x8C6529],
    "Fire": [0xFF0000, 0xFF4500, 0xE25822],
    "Smoke": [0x0A0A0A, 0x232323, 0x2C2424]
}
