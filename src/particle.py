import math
from typing import Type, Set, Union
from enum import Enum, auto
import random

import pygame as py

from src.tools import interpolate_pos, Board
from src.vec import Vec
from values import *


class StateOfAggregation(Enum):
    Gas: int = 0
    Liquid: int = auto()
    Solid: int = auto()


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
        self.been_updated: bool = been_updated
        self.is_falling: bool = is_falling

        self.color: int = 0
        self.pos: Vec = Vec(y, x)
        self.vel: Vec = Vec()

        self.lifetime: float = 0.0
        self.flammable: float = 100.0
        self.heat: float = 0.0
        self.friction = 1.0
        self.inertial_resistance = 1.0
        self.bounciness = 1.0
        self.mass = 0.0

    def _step(self, board: Board) -> bool:
        pass

    def on_update(self, board: Board) -> bool:
        if self.been_updated:
            return False
        self.been_updated = True

        has_been_modified = self._step(board)

        return has_been_modified

    def reset(self) -> None:
        self.been_updated = False

    def push_neighbours(self, board: Board, from_location: Vec) -> None:
        if board.in_bounds(from_location.y, from_location.x - 1):
            left = board[from_location.y, from_location.x - 1]
            if left is not None and self.id() == left.id():
                if random.random() > left.inertial_resistance:
                    left.is_falling = True

        if board.in_bounds(from_location.y, from_location.x + 1):
            right = board[from_location.y, from_location.x + 1]
            if right is not None and self.id() == right.id():
                if random.random() > right.inertial_resistance:
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

    def __eq__(self, other):
        if other is None:
            return False
        return self.pos.x == other.pos.x and self.pos.y == other.pos.y


class Sand(Particle):
    priority = {ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Sand, self).__init__(y, x)
        self.color = random.choice(COLORS["Sand"])

        self.vel = Vec(0, 0)

        self.friction = 0.9
        self.inertial_resistance = 0.1
        self.bounciness = 1
        self.mass = 0.2

    def _step(self, board: Board) -> bool:
        move = self.pos.copy()

        self.vel.y += GRAVITY
        if self.is_falling:
            self.vel.x *= 0.6

        target_position = self.pos + self.vel
        iterate_direction = interpolate_pos(self.pos, target_position)
        next(iterate_direction)  # skipping current position

        for i, pos in enumerate(iterate_direction):
            if i > 5:
                break
            if not board.in_bounds(pos.y, pos.x):
                break

            neighbor = board[pos.y, pos.x]
            if self.is_valid(neighbor):
                self.is_falling = True
                move = pos
                self.push_neighbours(board, move)

            else:
                if self.is_falling:
                    on_hit_vel = max(self.vel.y * self.bounciness, 4)
                    self.vel.x = on_hit_vel if self.vel.x > 0 else -on_hit_vel
                else:
                    self.vel.y = 0

                if neighbor is None:
                    neighbor = Wood(0, 0)

                self.vel.x *= self.friction * neighbor.friction
                norm_vel = self.vel.normalize()

                diagonal_neigh_pos = pos + Vec(1, -1 if norm_vel.x < 0 else 1)
                if board.in_bounds(diagonal_neigh_pos.y, diagonal_neigh_pos.x):
                    diagonal_neigh = board[diagonal_neigh_pos.y, diagonal_neigh_pos.x]

                next_to_neigh_pos = pos + Vec(0, -1 if norm_vel.x < 0 else 1)
                if board.in_bounds(next_to_neigh_pos.y, next_to_neigh_pos.x):
                    next_to_neigh = board[next_to_neigh_pos.y, next_to_neigh_pos.x]
                    if self.is_valid(next_to_neigh):
                        self.vel.x *= -1


                self.is_falling = False
                break


        # if board.in_bounds(move.y + 1, move.x) and self.is_valid(board[move.y + 1, move.x]):
        #     self.is_falling = True
        #     move.y += 1
        #     board.swap(self, move.y, move.x)
        #     self.push_neighbours(board, self.pos)
        #     return True
        #
        # elif self.is_falling:
        #     d = -1 if random.randint(0, 1) else 1
        #     if board.in_bounds(move.y + 1, move.x + d) and self.is_valid(board[move.y + 1, move.x + d]):
        #         move.y += 1
        #         move.x += d
        #     elif board.in_bounds(move.y + 1, move.x - d) and self.is_valid(board[move.y + 1, move.x - d]):
        #         move.y += 1
        #         move.x -= d
        #     else:
        #         self.is_falling = False
        #         self.vel = Vec(0, d)
        #         return True
        #
        #     board.swap(self, move.y, move.x)
        #     self.push_neighbours(board, self.pos)
        #     return True
        #
        # elif self.vel.x != 0:
        #     d = round(self.vel.x)
        #     if board.in_bounds(move.y, move.x + d) and self.is_valid(board[move.y, move.x + d]):
        #         move.x += d
        #         self.vel.x *= self.friction
        #         board.swap(self, move.y, move.x)
        #         return True
        #     else:
        #         self.vel.x = 0

        if move == self.pos:
            return False

        board.swap(self, move.y, move.x)
        return True


class Water(Particle):
    priority = {ParticleType.Sand, ParticleType.Wood}

    def __init__(self, y: int, x: int) -> None:
        super(Water, self).__init__(y, x)
        self.color = random.choice(COLORS["Water"])

        self.vel = Vec(0, 3)

    def _step(self, board: Board) -> bool:
        state = False
        move = self.pos.copy()
        if board.in_bounds(move.y + 1, move.x) and self.is_valid(board[move.y + 1, move.x]):
            move.y += 1
            board.swap(self, move.y, move.x)
            return True

        d = -1 if random.randint(0, 1) else 1
        if board.in_bounds(move.y + 1, move.x + d) and self.is_valid(board[move.y + 1, move.x + d]):
            move.y += 1
            move.x += d
            state = True

        elif board.in_bounds(move.y + 1, move.x - d) and self.is_valid(board[move.y + 1, move.x - d]):
            move.y += 1
            move.x -= d
            state = True

        elif board.in_bounds(move.y + 1, move.x + d) and self.is_valid(board[move.y + 1, move.x + d]):
            move.y += 1
            move.x += d
            state = True

        elif board.in_bounds(move.y + 1, move.x - d) and self.is_valid(board[move.y + 1, move.x - d]):
            move.y += 1
            move.x -= d
            state = True

        elif board.in_bounds(move.y, move.x + d) and self.is_valid(board[move.y, move.x + d]):
            move.x += d
            state = True

        elif board.in_bounds(move.y, move.x - d) and self.is_valid(board[move.y, move.x - d]):
            move.x -= d
            state = True

        board.swap(self, move.y, move.x)
        return state


class Wood(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Wood, self).__init__(y, x)
        self.color = random.choice(COLORS["Wood"])

        self.flammable = 96
        self.friction = 0.5

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

        self.vel = Vec(-1, 0)

    def _step(self, board: Board) -> bool:
        if self.lifetime < 0:
            board[self.pos.y, self.pos.x] = None
            return False
        self.lifetime -= 1

        move = self.pos.copy()

        if board.in_bounds(move.y - 1, move.x) and board[move.y - 1, move.x] is None:
            move.y -= 1

        d = random.randint(-1, 1)
        if not d:
            board.swap(self, move.y, move.x)
            return True

        if board.in_bounds(move.y, move.x - d) and board[move.y, move.x - d] is None:
            move.x = move.x - d
        elif board.in_bounds(move.y, move.x + d) and board[move.y, move.x + d] is None:
            move.x = self.pos.x + d

        board.swap(self, move.y, move.x)
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
