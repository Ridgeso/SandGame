from cparticle cimport *
from vector cimport *


cdef struct Chunk:
    int y, x
    int height, width
    bint updateThisFrame
    bint shouldBeUpdatedNextFrame

cdef Chunk makeChunk(int y, int x, int height, int width)
cdef void updateChunk(Chunk* chunk)
cdef void activateChunk(Chunk* chunk)


cdef struct Board:
    int height, width
    Particle_t** board

cdef Board initBoard(int height, int width)
cdef void freeBoard(Board* board)
cdef inline Particle_t* getParticle(Board* board, int y, int x):
    return &board.board[y][x]


cdef struct Brush:
    ParticleType pen
    int penSize

cdef void paint(Brush* brush, Board* board, ivec mousePos, ivec lastMousePosition)


cdef ivec* interpolatePos(ivec* start, ivec* end)
