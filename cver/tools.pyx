from ..values import *

from libc.stdio cimport printf
from libc.stdlib cimport malloc, free
from cparticle cimport *

cdef extern from "math.h":
    float INFINITY
    double sqrt(double)


cdef extern from "vector.h": *


cdef public struct Chunk:
    int y, x
    int height, width
    bint updateThisFrame
    bint shouldBeUpdatedNextFrame


cdef Chunk makeChunk(int y, int x, int height, int width):
    cdef Chunk chunk
    chunk.y = y
    chunk.x = x
    chunk.height = height
    chunk.width = width
    chunk.updateThisFrame = True
    chunk.shouldBeUpdatedNextFrame = True
    return chunk

cdef void activateChunk(Chunk* chunk):
    chunk.shouldBeUpdatedNextFrame = True

cdef void deactivateChunk(Chunk* chunk):
    chunk.shouldBeUpdatedNextFrame = False

cdef void updateChunk(Chunk* chunk):
    chunk.updateThisFrame = chunk.shouldBeUpdatedNextFrame
    chunk.shouldBeUpdatedNextFrame = False

cdef void printChunk(Chunk* chunk):
    printf("Chunk y=%d x=%d height=%d width=%d\n", chunk.y, chunk.x, chunk.height, chunk.width)



cdef public struct Board:
    int height, width
    Particle_t** board

cdef Board initBoard(int height, int width):
    cdef Board board
    board.height = height
    board.width = width

    board.board = <Particle_t**>malloc(height * sizeof(Particle_t*))
    cdef int i, j
    for i in range(height):
        board.board[i] = <Particle_t*>malloc(width * sizeof(Particle_t))
        for j in range(width):
            board.board[i][j] = Empty(i, j, False, True)
        
    return board

cdef inline Particle_t* getParticle(Board* board, int y, int x):
    return board.board[y][x]

cdef inline void setParticle(Board* board, int y, int x, Particle_t particle):
    board.board[y][x] = particle

cdef void freeBoard(Board* board):
    cdef int i
    for i in range(board.height):
        free(<void*>board.board[i])
    free(<void*>board.board)

cdef bint inBounds(Board* board, int y, int y):
    return 0 <= y < board.height and 0 <= x < board.width

cdef void swap(Board* board, Particle_t* cell, int y, int x):
    cdef Particle_t* other = getParticle(board, y, x)
    
    board.board[cell.pos.y][cell.pos.x] = other
    board.board[y][x] = cell

    other.pos = cell.pos

    cell.pos.y = y
    cell.pos.x = x


cdef public struct Brush:
    ParticleType particle
    int penSize

cdef Brush initBrush():
    cdef Brush brush
    brush.particle = SAND
    brush.penSize = PAINT_SACLE
    return brush

cdef void paintPoint(Brush* brush, Board* board, vec* point):
    if not inBounds(board, point.y, point.x):
        return
    cdef Particle_t particle
    cdef Particle_t* pos = getParticle(board, point.y, point.x)
    if isValid(brush.particle, pos.pType):
        if brush.particle == SAND:
            particle = Sand(point.y, point.x, False, True)
        elif brush.particle == WATER:
            particle = Water(point.y, point.x, False, True)
        elif brush.particle == WOOD:
            particle = Wood(point.y, point.x, False, True)
        elif brush.particle == FIRE:
            particle = Fire(point.y, point.x, False, True)
        elif brush.particle == SMOKE:
            particle = Smoke(point.y, point.x, False, True)
        elif brush.particle == EMPTY:
            particle = Water(point.y, point.x, False, True)
        setParticle(board, particle)

cdef void paintFromTo(Brush* brush, Board* board, vec* start, vec* end):
    cdef vec* point = interpolatePos(start, end)
    while point != NULL:
        paintPoint(brush, board, point)
        point = interpolatePos(NULL, end)

cdef void paint(Brush* brush, Board* board, vec mousePos, vec lastMousePosition):
    mousePos = imulv(&mousePos, 1/SCALE)
    
    cdef vec slope = <vec>isubv(&mousePos, &lastMousePosition)
    slope = normalize(&slope)

    cdef ivec y, x
    y.x = 0
    x.y = 0
    cdef ivec pointY, pointX
    cdef ivec lastPointY, lastPointX
    cdef int offset
    for offset in range(-brush.penSize, brush.penSize):
        y.y = offset
        pointY = iaddv(&y, &mousePos)
        lastPointY = iaddv(&y, &lastMousePosition)
        paintFromTo(brush, board, &pointY, &lastPointY)

        x.x = offset
        pointX = iaddv(&x, &mousePos)
        lastPointX = iaddv(&x, &lastMousePosition)
        paintFromTo(brush, board, &pointX, &lastPointX)

    cdef int cy, cx, radius
    cdef ivec point, lastPoint, r_phi
    for cy in range(-brush.penSize, brush.penSize):
        radius = <int>sqrt(brush.penSize * brush.penSize - cy * cy)
        for cx in range(-radius, radius):
            r_phi.y = cy
            r_phi.x = cx
            
            point = iaddv(&mousePos, &r_phi)
            paintPoint(brush, board, &point)

            lastPoint = iaddv(&lastMousePosition, &r_phi)
            paintPoint(brush, board, &lastMousePosition)


# Interpolation
cdef ivec current_cell, cell_direction
cdef vec distances, unit_distance
cdef ivec* out = <ivec*>malloc(sizeof(ivec))

cdef ivec* interpolatePos(vec* start, vec* end):
    if start == NULL:
        if equalIVec(out, end):
            return NULL
        
        if distances.y < distances.x:
            current_cell.y += cell_direction.y
            distances.y += unit_distance.y
        else:
            current_cell.x += cell_direction.x
            distances.x += unit_distance.x

        out.y = current_cell.y
        out.x = current_cell.x
        return out
    
    else:
        cdef vec slope = subv(end, start)
        slope = normalize(&slope)

        # Moving through cells
        cell_direction.y = 1 if slope.x > 0. else -1
        cell_direction.x = 1 if slope.y > 0. else -1

        # Moving through plane
        cdef float dx = slope.x/slope.y if slope.y != 0.0 else INFINITY
        cdef float dy = slope.y/slope.x if slope.x != 0.0 else INFINITY
        cdef vec dist
        dist.y = 1

        dist.x = dy
        unit_distance.y = length(&dist)  # dx for 1x
        dist.x = dx
        unit_distance.x = length(&dist)  # dy for 1y

        # 1st position
        current_cell = start
        distances = unit_distance

        out.y = start.y
        out.x = start.x
        return out
