from cver.cparticle cimport *
from cver.vector cimport *
cdef extern from "<pthread.h>" nogil:
    """
    #define _OPEN_THREADS
    """
    ctypedef struct pthread_mutexattr_t:
        pass
    ctypedef struct pthread_mutex_t:
       pass
    
    int pthread_mutex_init(pthread_mutex_t *mutex, pthread_mutexattr_t *mutexattr)
    int pthread_mutex_destroy(pthread_mutex_t *mutex)
    int pthread_mutex_lock(pthread_mutex_t *mutex)
    int pthread_mutex_unlock(pthread_mutex_t *mutex)


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
    pthread_mutex_t mutex

cdef Board initBoard(int height, int width)
cdef void freeBoard(Board* board)
cdef void swapParticles(Board* board, Particle_t* cell, int y, int x) nogil

cdef inline bint inBounds(Board* board, int y, int x) nogil:
    return 0 <= y < board.height and 0 <= x < board.width

cdef inline Particle_t* getParticle(Board* board, int y, int x) nogil:
    return &board.board[y][x]

cdef inline void setParticle(Board* board, int y, int x, Particle_t* particle) nogil:
    pthread_mutex_lock(&board.mutex)
    board.board[y][x] = particle[0]
    pthread_mutex_unlock(&board.mutex)


cdef struct Brush:
    ParticleType pen
    int penSize

cdef Brush initBrush()
cdef void paint(Brush* brush, Board* board, ivec mousePos, ivec lastMousePosition)

cdef float linePointLen(vec lineStart, vec lineEnd, vec point)

cdef ivec* interpolatePos(ivec* start, ivec* end, int depth) nogil
