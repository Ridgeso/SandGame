from values import *
cimport numpy as np
import numpy as np

import pygame as py
import random


ctypedef enum ParticleType:
    ParticleT = 0,
    SandT,
    WaterT,
    FireT,
    WoodT,
    SmokeT,
    EraserT


cdef class Particle:
    cdef int VELOCITY
    cdef int lifetime, x, y
    cdef bint flammable
    cdef public int color[3]
    cdef bint has_been_updated

    def __init__(self, int y, int x):
        self.VELOCITY = 3
        self.lifetime = 0
        self.flammable = False
        self.x = x
        self.y = y
        self.color = (0, 0, 0)

    @staticmethod
    def id():
        return ParticleType.ParticleT
    
    @staticmethod
    def priority(int id):
        return True

    cpdef void update_frame(self, np.ndarray board):
        pass
    
    cpdef void draw(self, win):
        py.draw.rect(win, self.color, ((self.x*SCALE, self.y*SCALE), (SCALE, SCALE)), 0)

    @classmethod
    def is_valid_spot(cls, spot):
        if spot is None:
            return True
        if spot.id == cls.id:
            return False
        return not cls.priority(spot.id())


cdef class Sand(Particle):
    def __init__(self, int y, int x):
        super(Sand, self).__init__(y, x)
        self.color = random.choice(COLORS["Sand"])

    @staticmethod
    def id():
        return ParticleType.SandT

    @staticmethod
    def priority(int id):
        return id == ParticleType.WoodT
    
    cpdef void update_frame(self, np.ndarray board):
        cdef int i
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


cdef class Water(Particle):
    def __init__(self, int y, int x):
        super(Water, self).__init__(y, x)
        self.color = random.choice(COLORS["Water"])

    @staticmethod
    def id():
        return ParticleType.WaterT
        
    @staticmethod
    def priority(int id):
        return id == ParticleType.SandT or id == ParticleType.WoodT
        
    cpdef void update_frame(self, np.ndarray board):
        cdef int i
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


cdef class Wood(Particle):
    def __init__(self, int y, int x):
        super(Wood, self).__init__(y, x)
        self.color = random.choice(COLORS["Wood"])
        self.flammable = True
        self.lifetime = 100
            
    @staticmethod
    def id():
        return ParticleType.WoodT
    
    @staticmethod
    def priority(int id):
        return True


cdef class Fire(Particle):
    def __init__(self, int y, int x):
        super(Fire, self).__init__(y, x)
        self.color = random.choice(COLORS["Fire"])
        self.lifetime = random.randint(150, 220)
        
    @staticmethod
    def id():
        return ParticleType.FireT

    @staticmethod
    def priority(ParticleType id):
        return id == ParticleType.SandT or id == ParticleType.WoodT

    cpdef void update_frame(self, np.ndarray board):
        if self.lifetime < 0:
            board[self.y][self.x] = Smoke(self.y, self.x)
            return
        cdef int i, j
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


cdef class Smoke(Particle):
    def __init__(self, int y, int x, bint update=False):
        super(Smoke, self).__init__(y, x)
        self.color = random.choice(COLORS["Smoke"])
        self.lifetime = random.randint(10, 80)
        self.has_been_updated = update

    @staticmethod
    def id():
        return ParticleType.SmokeT
        
    @staticmethod
    def priority(ParticleType id):
        return id == ParticleType.SandT or  id == ParticleType.WaterT or  id == ParticleType.WoodT

    cpdef void update_frame(self, np.ndarray board):
        if self.has_been_updated:
            self.has_been_updated = False
            return
        if self.lifetime < 0:
            board[self.y][self.x] = None
            return
        self.lifetime -= 1
        new_y = None
        new_x = None
        if self.y >= 1 and board[self.y-1][self.x] is None:
            new_y = self.y-1
            new_x = self.x
        
        if random.randint(1, 2) % 2:
            if self.y <= 0:
                return

            if self.x > 0 and board[self.y-1][self.x-1] is None:
                new_y = self.y-1
                new_x = self.x-1
            elif self.x < len(board[0])-1 and board[self.y-1][self.x+1] is None:
                new_y = self.y-1
                new_x = self.x+1

        if new_y is not None and new_x is not None:
            board[new_y][new_x] = Smoke(new_y, new_x, True)
            board[self.y][self.x] = None


class Eraser(Particle):
    
    def __new__(cls, *args, **kwargs):
        return None

    @staticmethod
    def id():
        return ParticleType.EraserT

    @classmethod
    def is_valid_spot(cls, spot):
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
