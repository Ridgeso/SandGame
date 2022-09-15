from values import *

from libc.stdio cimport printf
from libc.stdlib cimport malloc, free

from tools cimport *
from cparticle cimport *

cdef extern from "math.h":
    const float INFINITY
    double sqrt(double)
    double round(double y)


#### CHUNK
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


##### BOARD
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

cdef void freeBoard(Board* board):
    cdef int i
    for i in range(board.height):
        free(<void*>board.board[i])
    free(<void*>board.board)

cdef void swapParticles(Board* board, Particle_t* cell, int y, int x):
    cdef Particle_t swapCell = getParticle(board, y, x)[0]  # Copying the Cell to swap
    
    swapCell.pos = cell.pos

    cell.pos.y = y
    cell.pos.x = x
    
    board.board[y][x] = cell[0]
    board.board[swapCell.pos.y][swapCell.pos.x] = swapCell


##### BRUSH
cdef Brush initBrush():
    cdef Brush brush
    brush.pen = SAND
    brush.penSize = <int>PAINT_SCALE
    return brush

cdef void paintPoint(Brush* brush, Board* board, ivec* point):
    if not inBounds(board, point.y, point.x):
        return
    cdef Particle_t newParticle
    cdef Particle_t* pos = getParticle(board, point.y, point.x)
    if isValid(brush.pen, pos.pType):
        if brush.pen == SAND:
            newParticle = Sand(point.y, point.x, False, True)
        elif brush.pen == WATER:
            newParticle = Water(point.y, point.x, False, True)
        elif brush.pen == WOOD:
            newParticle = Wood(point.y, point.x, False, True)
        elif brush.pen == FIRE:
            newParticle = Fire(point.y, point.x, False, True)
        elif brush.pen == SMOKE:
            newParticle = Smoke(point.y, point.x, False, True)
        elif brush.pen == EMPTY:
            newParticle = Empty(point.y, point.x, False, True)
        setParticle(board, point.y, point.x, &newParticle)

cdef void paintFromTo(Brush* brush, Board* board, ivec* start, ivec* end):
    cdef ivec* point = interpolatePos(start, end)
    while point != NULL:
        paintPoint(brush, board, point)
        point = interpolatePos(NULL, end)

cdef void paint(Brush* brush, Board* board, ivec mousePos, ivec lastMousePosition):
    mousePos.y /= <int>SCALE
    mousePos.x /= <int>SCALE
    lastMousePosition.y /= <int>SCALE
    lastMousePosition.x /= <int>SCALE

    cdef vec fmousePos = ivec2vec(&mousePos)
    cdef vec flastMousePosition = ivec2vec(&lastMousePosition)
    
    cdef vec slope = <vec>subv(&fmousePos, &flastMousePosition)
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
        radius = <int>round(sqrt(brush.penSize * brush.penSize - cy * cy))
        for cx in range(-radius, radius):
            r_phi.y = cy
            r_phi.x = cx
            
            point = iaddv(&mousePos, &r_phi)
            paintPoint(brush, board, &point)

            lastPoint = iaddv(&lastMousePosition, &r_phi)
            paintPoint(brush, board, &lastMousePosition)


# Interpolation
cdef ivec currentCell, cellDirection
currentCell.y = 0; currentCell.x = 0
cellDirection.y = 0; cellDirection.x = 0

cdef vec distances, unitDistance
distances.y = 0; distances.x = 0
unitDistance.y = 0; unitDistance.x = 0

cdef ivec* out = <ivec*>malloc(sizeof(ivec))
out.y = 0; out.x = 0

cdef ivec* interpolatePos(ivec* start, ivec* end):
    global currentCell, cellDirection
    global distances, unitDistance
    global out

    cdef vec slope, fstart, fend
    cdef float dy, dx

    cdef vec dist

    if start == NULL:
        if equalIVec(out, end):
            return NULL
        
        if distances.y < distances.x:
            currentCell.y += cellDirection.y
            distances.y += unitDistance.y
        else:
            currentCell.x += cellDirection.x
            distances.x += unitDistance.x

        out[0] = currentCell
        return out
    
    else:
        dist.y = 1

        fstart = ivec2vec(start)
        fend = ivec2vec(end)
        slope = subv(&fend, &fstart)
        slope = normalize(&slope)

        # Moving through cells
        cellDirection.y = 1 if slope.y > 0. else -1
        cellDirection.x = 1 if slope.x > 0. else -1

        # Moving through plane
        dy = slope.x/slope.y if slope.y != 0.0 else INFINITY
        dx = slope.y/slope.x if slope.x != 0.0 else INFINITY

        dist.x = dy
        unitDistance.y = length(&dist)  # dx for 1x
        dist.x = dx
        unitDistance.x = length(&dist)  # dy for 1y

        # 1st position
        currentCell = start[0]
        distances = unitDistance

        out[0] = start[0]
        return out
