from values import *
from random import choice, randint, sample


cdef class Particle:
    cdef int VELOCITY
    cdef int lifetime, x, y
    cdef bint flammable
    cdef public int color[3]
    cdef bint has_been_updated

    def __init__(self, int y, int x):
        self.VELOCITY = 3
        self.lifetime
        self.flammable = False
        self.x = x
        self.y = y
        self.color = (0, 0, 0)

    cpdef update_frame(self, board):
        pass

    @classmethod
    def paint(cls, board, pos):
        cdef int pos_x, pos_y, x, y
        pos_x = pos[0]
        pos_y = pos[1]
        pos_y //= SCALE
        pos_x //= SCALE
        ran = sample(range(-PAINT_RANGE, PAINT_RANGE), PAINT_SCALE*2)
        for x, y in zip(ran[PAINT_SCALE:], ran[:PAINT_SCALE]):
            if 0 <= pos_y+y < len(board) and 0 <= pos_x+x < len(board[0]) and isinstance(board[pos_y+y][pos_x+x], int):
                board[pos_y+y][pos_x+x] = cls(pos_y+y, pos_x+x)


cdef class Sand(Particle):
    def __init__(self, int y, int x):
        super(Sand, self).__init__(y, x)
        self.color = choice(COLORS["Sand"])

    cpdef update_frame(self, board):
        cdef int i
        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i and not isinstance(board[self.y+i][self.x], (Sand, Wood)):
                board[self.y+i][self.x] = Sand(self.y+i, self.x)
                board[self.y][self.x] = 0
                return

        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i:
                if self.x >= i and not isinstance(board[self.y+i][self.x-i], (Sand, Wood)):
                    board[self.y+i][self.x-i] = Sand(self.y+i, self.x-i)
                    board[self.y][self.x] = 0
                    return

                elif self.x < len(board[0])-i and not isinstance(board[self.y+i][self.x+i], (Sand, Wood)):
                    board[self.y+i][self.x+i] = Sand(self.y+i, self.x+i)
                    board[self.y][self.x] = 0
                    return


cdef class Water(Particle):
    def __init__(self, int y, int x):
        super(Water, self).__init__(y, x)
        self.color = choice(COLORS["Water"])

    cpdef update_frame(self, board):
        cdef int i
        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i and not isinstance(board[self.y+i][self.x], (Sand, Wood, Water)):
                board[self.y+i][self.x] = Water(self.y+i, self.x)
                board[self.y][self.x] = 0
                return

        for i in reversed(range(1, self.VELOCITY)):
            if self.y < len(board)-i:
                if self.x >= i and not isinstance(board[self.y+i][self.x-i], (Sand, Wood, Water)):
                    board[self.y+i][self.x-i] = Water(self.y+i, self.x-i)
                    board[self.y][self.x] = 0
                    return

                elif self.x < len(board[0])-i and not isinstance(board[self.y+i][self.x+i], (Sand, Wood, Water)):
                    board[self.y+i][self.x+i] = Water(self.y+i, self.x+i)
                    board[self.y][self.x] = 0
                    return

        for i in reversed(range(1, self.VELOCITY)):
            if self.x < len(board[0])-i and not isinstance(board[self.y][self.x+i], (Sand, Wood, Water)):
                board[self.y][self.x+i] = Water(self.y, self.x+i)
                board[self.y][self.x] = 0
                return
            elif self.x >= i and not isinstance(board[self.y][self.x-i], (Sand, Wood, Water)):
                board[self.y][self.x-i] = Water(self.y, self.x-i)
                board[self.y][self.x] = 0
                return


cdef class Wood(Particle):
    def __init__(self, int y, int x):
        super(Wood, self).__init__(y, x)
        self.color = choice(COLORS["Wood"])
        self.flammable = True
        self.lifetime = 100

    @classmethod
    def paint(cls, board, pos):
        cdef int pos_x, pos_y, i, j
        pos_x = pos[0]
        pos_y = pos[1]
        pos_y //= SCALE
        pos_x //= SCALE
        for i in range(-PAINT_SCALE, PAINT_SCALE):
            for j in range(-PAINT_SCALE, PAINT_SCALE):
                if 0 <= pos_y+i < len(board) and 0 <= pos_x+j < len(board[0]):
                    board[pos_y+i][pos_x+j] = cls(pos_y+i, pos_x+j)


cdef class Fire(Particle):
    def __init__(self, int y, int x):
        super(Fire, self).__init__(y, x)
        self.color = choice(COLORS["Fire"])
        self.lifetime = randint(150, 220)

    cpdef update_frame(self, board):
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
                    elif isinstance(board[self.y+i][self.x+j], int) and not randint(0, 31):
                        board[self.y+i][self.x+j] = Smoke(self.y+i, self.x+j, False)
        self.lifetime -= 1

    @classmethod
    def paint(cls, board, pos):
        cdef int pos_x, pos_y, i, j
        pos_x = pos[0]
        pos_y = pos[1]        
        pos_y //= SCALE
        pos_x //= SCALE
        for i in range(-PAINT_SCALE, PAINT_SCALE):
            for j in range(-PAINT_SCALE, PAINT_SCALE):
                if 0 <= pos_y+i < len(board) and 0 <= pos_x+j < len(board[0]):
                    board[pos_y+i][pos_x+j] = cls(pos_y+i, pos_x+j)


cdef class Smoke(Particle):
    def __init__(self, int y, int x, bint update=False):
        super(Smoke, self).__init__(y, x)
        self.color = choice(COLORS["Smoke"])
        self.lifetime = randint(10, 80)
        self.has_been_updated = update

    cpdef update_frame(self, board):
        if self.has_been_updated:
            self.has_been_updated = False
            return
        if self.lifetime < 0:
            board[self.y][self.x] = 0
            return
        self.lifetime -= 1
        new_board_pos = None
        if self.y >= 1 and isinstance(board[self.y-1][self.x], int):
            new_board_pos = [self.y-1, self.x]

        if randint(1, 2) % 2:
            if self.y > 0:
                if self.x > 0 and isinstance(board[self.y-1][self.x-1], int):
                    new_board_pos = [self.y-1, self.x-1]

                elif self.x < len(board[0])-1 and isinstance(board[self.y-1][self.x+1], int):
                    new_board_pos = [self.y-1, self.x+1]

        if new_board_pos is not None:
            board[new_board_pos[0]][new_board_pos[1]] = Smoke(*new_board_pos, True)
            board[self.y][self.x] = 0


cdef class Eraser(Particle):
    def __init__(self):
        super(Eraser, self).__init__(-1, -1)

    @classmethod
    def paint(cls, board, pos):
        cdef int pos_x, pos_y, i, j
        pos_x = pos[0]
        pos_y = pos[1]
        pos_y //= SCALE
        pos_x //= SCALE
        for i in range(-PAINT_SCALE, PAINT_SCALE):
            for j in range(-PAINT_SCALE, PAINT_SCALE):
                if 0 <= pos_y+i < len(board) and 0 <= pos_x+j < len(board[0]):
                    board[pos_y+i][pos_x+j] = 0


COLORS_OBJ = {
    "Sand": Sand,
    "Water": Water,
    "Wood": Wood,
    "Fire": Fire,
    "Smoke": Smoke
}
