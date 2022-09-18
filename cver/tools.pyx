from values import *

from libc.stdio cimport printf
from libc.stdlib cimport malloc, free

from tools cimport *
from cparticle cimport *

cdef extern from "math.h":
    const float INFINITY
    double sqrt(double)
    double round(double)


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
    cdef ivec* point = interpolatePos(start, end, 0)
    while point != NULL:
        paintPoint(brush, board, point)
        point = interpolatePos(NULL, end, 0)

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


cdef float linePointLen(vec lineStart, vec lineEnd, vec point):
    if equalVec(&lineStart, &lineEnd):
        return INFINITY
    cdef vec slope = subv(&lineEnd, &lineStart)
    cdef float divisor = pow(slope.x, 2) + pow(slope.y, 2)

    cdef float t = ((point.x - lineStart.x) * slope.x + (point.y - lineStart.y) * slope.y) / divisor
    if not 0.0 <= t <= 1.0:  # Checking if p's projection lies on the line
        return INFINITY

    cdef float point_distance_from_line = abs(slope.x * (lineStart.y - point.y) - (lineStart.x - point.x) * slope.y)
    point_distance_from_line /= sqrt(divisor)

    return point_distance_from_line


# Interpolation
cdef ivec[3] currentCell
cdef ivec[3] cellDirection

cdef vec[3] distances
cdef vec[3] unitDistance

cdef ivec[3] out

cdef ivec* interpolatePos(ivec* start, ivec* end, int depth):
    global currentCell, cellDirection
    global distances, unitDistance
    global out

    cdef vec slope, fstart, fend
    cdef float dy, dx

    cdef vec dist

    if start == NULL:
        if equalIVec(&out[depth], end):
            return NULL
        
        if distances[depth].y < distances[depth].x:
            currentCell[depth].y += cellDirection[depth].y
            distances[depth].y += unitDistance[depth].y
        else:
            currentCell[depth].x += cellDirection[depth].x
            distances[depth].x += unitDistance[depth].x

        out[depth] = currentCell[depth]
        return &out[depth]
    
    else:
        dist.y = 1

        fstart = ivec2vec(start)
        fend = ivec2vec(end)
        slope = subv(&fend, &fstart)
        slope = normalize(&slope)

        # Moving through cells
        cellDirection[depth].y = 1 if slope.y > 0. else -1
        cellDirection[depth].x = 1 if slope.x > 0. else -1

        # Moving through plane
        dy = slope.x/slope.y if slope.y != 0.0 else INFINITY
        dx = slope.y/slope.x if slope.x != 0.0 else INFINITY

        dist.x = dy
        unitDistance[depth].y = length(&dist)  # dx for 1x
        dist.x = dx
        unitDistance[depth].x = length(&dist)  # dy for 1y

        # 1st position
        currentCell[depth] = start[0]
        distances[depth] = unitDistance[depth]

        out[depth] = start[0]
        return &out[depth]
