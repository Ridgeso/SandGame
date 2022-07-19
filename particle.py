from typing import List, Tuple, Union
import numpy as np

from values import *
import pygame as py
import random


class Vec2:
    def __init__(self) -> None:
        self.x: int = 1
        self.y: int = 1


class Particle:
    VELOCITY: int = 3

    def __init__(self, y: int, x: int) -> None:
        self.lifetime: int = 0
        self.flammable: bool = False
        self.x: int = x
        self.y: int = y
        self.vel: Vec2 = Vec2()
        self.color: Tuple[int, int, int] = (0, 0, 0)

    def update_frame(self, board: List[Union[None, 'Particle']]) -> None:
        pass

    @classmethod
    def paint(cls, board: List[Union[None, 'Particle']]) -> None:
        pos_x, pos_y = py.mouse.get_pos()
        pos_y //= SCALE
        pos_x //= SCALE
        
        rand_x, rand_y = np.random.randint(-PAINT_RANGE, PAINT_RANGE+1, size=(2, PAINT_SCALE))

        for x, y in zip(rand_x, rand_y):
            if board[pos_y+y][pos_x+x] is None and 0 <= pos_y+y < len(board) and 0 <= pos_x+x < len(board[0]):
                board[pos_y+y][pos_x+x] = cls(pos_y+y, pos_x+x)

    def draw(self, win: py.Surface) -> None:
        py.draw.rect(win, self.color, ((self.x*SCALE, self.y*SCALE), (SCALE, SCALE)), 0)


class Sand(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Sand, self).__init__(y, x)
        self.color = random.choice(COLORS["Sand"])

    def update_frame(self, board: List[Union[None, 'Particle']]) -> None:
        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i and not isinstance(board[self.y+i][self.x], (Sand, Wood)):
                board[self.y+i][self.x] = Sand(self.y+i, self.x)
                board[self.y][self.x] = None
                return

        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i:
                if self.x >= i and not isinstance(board[self.y+i][self.x-i], (Sand, Wood)):
                    board[self.y+i][self.x-i] = Sand(self.y+i, self.x-i)
                    board[self.y][self.x] = None
                    return

                elif self.x < len(board[0])-i and not isinstance(board[self.y+i][self.x+i], (Sand, Wood)):
                    board[self.y+i][self.x+i] = Sand(self.y+i, self.x+i)
                    board[self.y][self.x] = None
                    return


class Water(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Water, self).__init__(y, x)
        self.color = random.choice(COLORS["Water"])

    def update_frame(self, board: List[Union[None, 'Particle']]) -> None:
        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i and not isinstance(board[self.y+i][self.x], (Sand, Wood, Water)):
                board[self.y+i][self.x] = Water(self.y+i, self.x)
                board[self.y][self.x] = None
                return

        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i:
                if self.x >= i and not isinstance(board[self.y+i][self.x-i], (Sand, Wood, Water)):
                    board[self.y+i][self.x-i] = Water(self.y+i, self.x-i)
                    board[self.y][self.x] = None
                    return

                elif self.x < len(board[0])-i and not isinstance(board[self.y+i][self.x+i], (Sand, Wood, Water)):
                    board[self.y+i][self.x+i] = Water(self.y+i, self.x+i)
                    board[self.y][self.x] = None
                    return

        for i in reversed(range(1, self.VELOCITY)):
            if self.x < len(board[0])-i and not isinstance(board[self.y][self.x+i], (Sand, Wood, Water)):
                board[self.y][self.x+i] = Water(self.y, self.x+i)
                board[self.y][self.x] = None
                return
            elif self.x >= i and not isinstance(board[self.y][self.x-i], (Sand, Wood, Water)):
                board[self.y][self.x-i] = Water(self.y, self.x-i)
                board[self.y][self.x] = None
                return


class Wood(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Wood, self).__init__(y, x)
        self.color = random.choice(COLORS["Wood"])
        self.flammable = True
        self.lifetime = 100

    @classmethod
    def paint(cls, board: List[Union[None, 'Particle']]) -> None:
        pos_x, pos_y = py.mouse.get_pos()
        pos_y //= SCALE
        pos_x //= SCALE
        for i in range(-PAINT_SCALE, PAINT_SCALE):
            for j in range(-PAINT_SCALE, PAINT_SCALE):
                if 0 <= pos_y+i < len(board) and 0 <= pos_x+j < len(board[0]):
                    board[pos_y+i][pos_x+j] = cls(pos_y+i, pos_x+j)


class Fire(Particle):
    def __init__(self, y: int, x: int) -> None:
        super(Fire, self).__init__(y, x)
        self.color = random.choice(COLORS["Fire"])
        self.lifetime = random.randint(150, 220)

    def update_frame(self, board: List[Union[None, 'Particle']]) -> None:
        if self.lifetime < 0:
            board[self.y][self.x] = Smoke(self.y, self.x)
            return
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                if 0 < self.y+i < len(board)-1 and 0 < self.x+j < len(board[0])-1:
                    if isinstance(board[self.y+i][self.x+j], Wood) and self.lifetime < 140:
                        board[self.y+i][self.x+j] = Fire(self.y+i, self.x+j)
                    elif isinstance(board[self.y+i][self.x+j], int) and not random.randint(0, 31):
                        board[self.y+i][self.x+j] = Smoke(self.y+i, self.x+j, False)
        self.lifetime -= 1

    @classmethod
    def paint(cls, board: List[Union[None, 'Particle']]) -> None:
        pos_x, pos_y = py.mouse.get_pos()
        pos_y //= SCALE
        pos_x //= SCALE
        for i in range(-PAINT_SCALE, PAINT_SCALE):
            for j in range(-PAINT_SCALE, PAINT_SCALE):
                if 0 <= pos_y+i < len(board) and 0 <= pos_x+j < len(board[0]):
                    board[pos_y+i][pos_x+j] = cls(pos_y+i, pos_x+j)


class Smoke(Particle):
    def __init__(self, y: int, x: int, update: bool=False):
        super(Smoke, self).__init__(y, x)
        self.color = random.choice(COLORS["Smoke"])
        self.lifetime = random.randint(10, 80)
        self.has_been_updated = update

    def update_frame(self, board: List[Union[None, 'Particle']]) -> None:
        if self.has_been_updated:
            self.has_been_updated = False
            return
        if self.lifetime < 0:
            board[self.y][self.x] = None
            return
        self.lifetime -= 1
        new_board_pos = None
        if self.y >= 1 and board[self.y-1][self.x] is None:
            new_board_pos = [self.y-1, self.x]

        if random.randint(1, 2) % 2:
            if self.y > 0:
                if self.x > 0 and board[self.y-1][self.x-1] is None:
                    new_board_pos = [self.y-1, self.x-1]

                elif self.x < len(board[0])-1 and board[self.y-1][self.x+1] is None:
                    new_board_pos = [self.y-1, self.x+1]

        if new_board_pos is not None:
            board[new_board_pos[0]][new_board_pos[1]] = Smoke(*new_board_pos, True)
            board[self.y][self.x] = None


class Eraser(Particle):
    def __init__(self):
        super(Eraser, self).__init__(-1, -1)

    @classmethod
    def update_frame(self, board: List[Union[None, 'Particle']]) -> None:
        pos_x, pos_y = py.mouse.get_pos()
        pos_y //= SCALE
        pos_x //= SCALE
        for i in range(-PAINT_SCALE, PAINT_SCALE):
            for j in range(-PAINT_SCALE, PAINT_SCALE):
                if 0 <= pos_y+i < len(board) and 0 <= pos_x+j < len(board[0]):
                    board[pos_y+i][pos_x+j] = None


COLORS_OBJ = {
    "Sand": Sand,
    "Water": Water,
    "Wood": Wood,
    "Fire": Fire,
    "Smoke": Smoke
}
