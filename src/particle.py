from typing import Set, Optional
from enum import Enum, auto
import random
import math

import src.tools as tools
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
    state: StateOfAggregation = None

    def __init__(self, y: int, x: int, is_falling: bool = True, been_updated: bool = False) -> None:
        self.been_updated: bool = been_updated
        self.is_falling: bool = is_falling

        self.color: int = 0
        self.pos: Vec = Vec(y, x)
        self.vel: Vec = Vec(0., 0.)

        self.lifetime: float = 0.0
        self.flammable: float = 100.0
        self.heat: float = 0.0
        self.friction: float = 1.0
        self.inertial_resistance: float = 1.0
        self.bounciness: float = 1.0
        self.density: float = 0.0
        self.dispersion: int = 0
        self.mass: float = 0.0

    def _step(self, board: tools.Board) -> bool:
        pass

    def on_update(self, board: tools.Board) -> bool:
        if self.been_updated:
            return False
        self.been_updated = True

        has_been_modified = self._step(board)

        return has_been_modified

    def reset(self) -> None:
        self.been_updated = False

    def push_neighbours(self, board: tools.Board, from_location: Vec) -> None:
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
    def is_valid(cls, spot: Optional['Particle']) -> bool:
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

    @staticmethod
    def _round_shift(v: float) -> float:
        if v < -0.1:
            return math.floor(v)
        elif v > 0.1:
            return math.ceil(v)
        return 0


class Sand(Particle):
    priority = {ParticleType.Wood}
    state = StateOfAggregation.Solid

    def __init__(self, y: int, x: int) -> None:
        super(Sand, self).__init__(y, x)
        self.color = random.choice(COLORS["Sand"])

        self.vel = Vec(0., 0.)

        self.friction = 0.75
        self.inertial_resistance = 0.5
        self.bounciness = 0.5
        self.mass = 54.0

    def _step(self, board: tools.Board) -> bool:
        move = self.pos.copy()

        self.vel.y += GRAVITY
        if self.is_falling:
            self.vel.x *= AIR_FRICTION

        target_position = (self.pos + self.vel).round()
        direction = tools.interpolate_pos_dda(self.pos, target_position)
        next(direction)  # skipping current position

        for pos in direction:
            if not board.in_bounds(pos.y, pos.x):
                self.vel = Vec(0.0, 0.0)
                break

            neighbor = board[pos.y, pos.x]
            if self.is_valid(neighbor):
                move = pos
                self.push_neighbours(board, move)
            else:
                if self.is_falling:
                    vel_on_hit = max(self.vel.y * self.bounciness, 3.0)
                    if self.vel.x:
                        self.vel.x = vel_on_hit if self.vel.x > 0.0 else -vel_on_hit
                    else:
                        d = -1.0 if random.randint(0, 1) else 1.0
                        self.vel.x = vel_on_hit * d

                additional_pos = self.vel.normalize()

                self.vel.x *= self.friction * neighbor.friction
                avg_vel = (self.vel.y + neighbor.vel.y) / 2
                if avg_vel < GRAVITY:
                    self.vel.y = GRAVITY
                else:
                    self.vel.y = avg_vel

                neighbor.vel.y = self.vel.y

                if -0.1 < additional_pos.y < 0.1:
                    additional_pos.y = 0
                else:
                    additional_pos.y = -1 if additional_pos.y < 0 else 1
                if -0.1 < additional_pos.x < 0.1:
                    additional_pos.x = 0
                else:
                    additional_pos.x = -1 if additional_pos.x < 0 else 1
                additional_pos = additional_pos.round()

                diagonal_neighbor_pos = move + additional_pos
                if board.in_bounds(diagonal_neighbor_pos.y, diagonal_neighbor_pos.x):
                    diagonal_neighbor = board[diagonal_neighbor_pos.y, diagonal_neighbor_pos.x]
                    if self.is_valid(diagonal_neighbor):
                        # self.is_falling = True
                        move = diagonal_neighbor_pos
                        break

                next_neighbor_pos = move + Vec(0, additional_pos.x)
                if next_neighbor_pos != diagonal_neighbor_pos:
                    if board.in_bounds(next_neighbor_pos.y, next_neighbor_pos.x):
                        next_neighbor = board[next_neighbor_pos.y, next_neighbor_pos.x]
                        if self.is_valid(next_neighbor):
                            self.is_falling = False
                            move = next_neighbor_pos
                            break
                        else:
                            self.vel.x *= -1

                self.is_falling = False
                break
        else:
            neighbor = board[target_position.y, target_position.x]
            if self.is_valid(neighbor):
                self.is_falling = True

        if move == self.pos:
            self.is_falling = False
            return False

        board.swap(self, move.y, move.x)
        return True


class Water(Particle):
    priority = {ParticleType.Sand, ParticleType.Wood}
    state = StateOfAggregation.Liquid

    def __init__(self, y: int, x: int) -> None:
        super(Water, self).__init__(y, x)
        self.color = random.choice(COLORS["Water"])

        self.vel = Vec(0.0, 0.0)

        self.bounciness = 0.75
        self.density = 10.
        self.dispersion = 4
        self.mass = 30.

    def _step(self, board: tools.Board) -> bool:
        move = self.pos.copy()

        self.vel.y += GRAVITY
        if self.is_falling:
            self.vel.x *= AIR_FRICTION

        target_position = (self.pos + self.vel).round()
        direction = tools.interpolate_pos_dda(self.pos, target_position)
        next(direction)  # skipping current position

        for pos in direction:
            if not board.in_bounds(pos.y, pos.x):
                self.vel = Vec(0.0, 0.0)
                break

            neighbor = board[pos.y, pos.x]
            if self.is_valid(neighbor):
                move = pos
                self.push_neighbours(board, move)
            else:
                # if neighbor.state == StateOfAggregation.Liquid:
                #     if self.density > neighbor.density:
                #         move = pos
                #         continue
                #     elif self.vel.y - neighbor.vel.y > 2:
                #         move = pos
                #         self.vel.y = 0
                #         continue

                if self.is_falling:
                    vel_on_hit = max(self.vel.y * self.bounciness, 4.0)
                    if self.vel.x:
                        self.vel.x = vel_on_hit if self.vel.x > 0.0 else -vel_on_hit
                    else:
                        d = -1.0 if random.randint(0, 1) else 1.0
                        self.vel.x = vel_on_hit * d

                additional_pos = self.vel.normalize()

                self.vel.x *= self.friction * neighbor.friction
                avg_vel = (self.vel.y + neighbor.vel.y) / 2
                # if avg_vel < GRAVITY:
                #     self.vel.y = GRAVITY
                # else:
                #     self.vel.y = avg_vel
                self.vel.y = 0.0
                # neighbor.vel.y = self.vel.y

                if -0.1 < additional_pos.y < 0.1:
                    additional_pos.y = 0
                else:
                    additional_pos.y = -1 if additional_pos.y < 0 else 1
                if -0.1 < additional_pos.x < 0.1:
                    additional_pos.x = 0
                else:
                    additional_pos.x = -1 if additional_pos.x < 0 else 1
                additional_pos = additional_pos.round()

                go_out = False
                diagonal_neighbor_pos = move + additional_pos
                new_target = diagonal_neighbor_pos.copy()
                new_target.x += additional_pos.x * self.dispersion
                for new_pos in tools.interpolate_pos_dda(diagonal_neighbor_pos, new_target):
                    if board.in_bounds(new_pos.y, new_pos.x):
                        diagonal_neighbor = board[new_pos.y, new_pos.x]
                        if self.is_valid(diagonal_neighbor):
                            self.is_falling = True
                            move = new_pos
                        else:
                            break
                    else:
                        go_out = True
                        break
                else:
                    break

                if go_out:
                    break

                next_neighbor_pos = move + Vec(0, additional_pos.x)
                new_target = next_neighbor_pos.copy()
                new_target.x += additional_pos.x * self.dispersion
                if next_neighbor_pos != diagonal_neighbor_pos:
                    for new_pos in tools.interpolate_pos_dda(next_neighbor_pos, new_target):
                        if board.in_bounds(new_pos.y, new_pos.x):
                            next_neighbor = board[new_pos.y, new_pos.x]
                            if self.is_valid(next_neighbor):
                                self.is_falling = False
                                move = next_neighbor_pos
                            else:
                                self.vel.x *= -1
                                break
                        else:
                            break
                    else:
                        break

                self.is_falling = False
                break
        else:
            neighbor = board[target_position.y, target_position.x]
            if self.is_valid(neighbor):
                self.is_falling = True

        if move == self.pos:
            self.is_falling = False
            return False

        board.swap(self, move.y, move.x)
        return True


class Wood(Particle):
    state = StateOfAggregation.Solid

    def __init__(self, y: int, x: int) -> None:
        super(Wood, self).__init__(y, x)
        self.color = random.choice(COLORS["Wood"])

        self.flammable = 96
        self.friction = 0.5

    def on_update(self, board: tools.Board) -> bool:
        return False


class Fire(Particle):
    priority = {ParticleType.Sand, ParticleType.Water, ParticleType.Wood}
    state = StateOfAggregation.Gas

    def __init__(self, y: int, x: int, been_updated: bool = False) -> None:
        super(Fire, self).__init__(y, x, been_updated=been_updated)
        self.original_color = random.choice(COLORS["Fire"])
        self.color = self.original_color
        self.heat = 100
        self.flammable = 1

    def receive_heat(self, cell: Optional[Particle]) -> None:
        if cell is None:
            self.heat *= 0.99
            return

        if cell.id() == ParticleType.Fire:
            self.heat = (self.heat + cell.heat)/2

        elif cell.id() == ParticleType.Water:
            self.heat = 0

        if self.heat > 100:
            self.heat = 100

    def on_update(self, board: tools.Board) -> bool:
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
    state = StateOfAggregation.Gas

    def __init__(self, y: int, x: int, been_updated: bool = False) -> None:
        super(Smoke, self).__init__(y, x, been_updated=been_updated)
        self.color = random.choice(COLORS["Smoke"])
        self.lifetime = random.randint(10, 80)

        self.vel = Vec(-1., 0.)

    def _step(self, board: tools.Board) -> bool:
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
    def is_valid(cls, spot: Optional[ParticleType]) -> bool:
        return True


COLORS = {  # R G B  24bits
    "Sand": [0xE4EB15, 0xFFCD18, 0xC1C707, 0xE49009],
    "Water": [0x0F5E9C, 0x1CA3EC, 0x2389DA, 0x5ABCD8],
    "Wood": [0x461F00, 0x643D01, 0x8C6529],
    "Fire": [0xFF0000, 0xFF4500, 0xE25822],
    "Smoke": [0x0A0A0A, 0x232323, 0x2C2424]
}
