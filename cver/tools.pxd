from cparticle cimport *
from vector cimport *


cdef struct Chunk:
    int y, x
    int height, width
    bint updateThisFrame
    bint shouldBeUpdatedNextFrame

cdef Chunk makeChunk(int y, int x, int height, int width)
cdef void updateChunk(Chunk* chunk)
cdef void activateChunk(Chunk* chunk) nogil
cdef void printChunk(Chunk* chunk)


cdef struct Board:
    int height, width
    Particle_t** board

cdef Board initBoard(int height, int width)
cdef void freeBoard(Board* board)
cdef void swapParticles(Board* board, Particle_t* cell, int y, int x) nogil

cdef inline bint inBounds(Board* board, int y, int x) nogil:
    return 0 <= y < board.height and 0 <= x < board.width

cdef inline Particle_t* getParticle(Board* board, int y, int x) nogil:
    return &board.board[y][x]

cdef inline void setParticle(Board* board, int y, int x, Particle_t* particle):
    board.board[y][x] = particle[0]


cdef struct Brush:
    ParticleType pen
    int penSize

cdef Brush initBrush()
cdef void paint(Brush* brush, Board* board, ivec mousePos, ivec lastMousePosition)

cdef float linePointLen(vec lineStart, vec lineEnd, vec point)

cdef ivec* interpolatePos(ivec* start, ivec* end, int depth) nogil
