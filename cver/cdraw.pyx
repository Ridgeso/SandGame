from values import *
import pygame as py
from time import perf_counter

import numpy as np
cimport numpy as np
np.import_array()
from cython.parallel import parallel, prange
from libc.stdio cimport printf
from libc.stdlib cimport malloc, free

from vector cimport *
from cparticle cimport *
from tools cimport *


ctypedef enum MouseKey:
    LEFT = 0
    SCROLL
    RIGHT


cdef class Display:
    cdef int winY, winX

    cdef win
    cdef surface
    cdef np.ndarray surfaceArray
    cdef int[:,:] surfaceArrayView
    
    cdef Board board
    cdef Brush brush
    cdef ivec lastMousePosition

    cdef int chunkSize, chunkRows, chunkColumns
    cdef Chunk** chunks
    cdef int chunkThreshold

    def __cinit__(self, int y, int x):
        self.winX = y
        self.winY = x

        # Main window
        self.win = py.display.set_mode((self.winX, self.winY))
        # Simulation Texture
        self.surface = py.Surface((BOARD_X, BOARD_Y))
        self.surfaceArray = np.zeros((BOARD_X, BOARD_Y), dtype=int)
        self.surfaceArrayView = self.surfaceArray

        # Board
        self.board = initBoard(BOARD_Y, BOARD_X)
        self.brush = initBrush()

        self.lastMousePosition.y = -1
        self.lastMousePosition.x = -1

        # Chunks
        self.chunkSize = 10  # 10 x 10
        self.chunkRows = BOARD_Y / self.chunkSize
        self.chunkColumns = BOARD_X / self.chunkSize

        self.chunks = <Chunk**>malloc(self.chunkRows * sizeof(Chunk*))

        cdef int row, column, chunkHeight, chunkWidth, offset
        
        # for row in range(0, BOARD_Y, self.chunkSize):
        for row in range(self.chunkRows):
            self.chunks[row] = <Chunk*>malloc(self.chunkColumns * sizeof(Chunk))

            # max chunk size or chunk loss
            offset = BOARD_Y - row * self.chunkSize
            chunkHeight = self.chunkSize if offset > self.chunkSize else offset
            
            # for column in range(0, BOARD_X, self.chunkSize):
            for column in range(self.chunkColumns):
                # max chunk size or chunk loss
                offset = BOARD_X - row * self.chunkSize
                chunkWidth = self.chunkSize if offset > self.chunkSize else offset
                
                self.chunks[row][column] = makeChunk(
                    row * self.chunkSize, column * self.chunkSize,
                    chunkHeight, chunkWidth
                )
            
        self.chunkThreshold = <int>SCALE * self.chunkSize

    def __dealloc__(self):
        freeBoard(&self.board)

        cdef int i
        for i in range(self.chunkRows):
            free(<void*>self.chunks[i])
        free(<void*>self.chunks)

    cdef void _activateChunkOnDraw(self, ivec mousePos):
        cdef Chunk* chunk
        cdef ivec brushPos = mousePos
        brushPos.y /= SCALE
        brushPos.x /= SCALE
        cdef ivec lastBrushPos = self.lastMousePosition
        lastBrushPos.y /= SCALE
        lastBrushPos.x /= SCALE

        cdef ivec inear, ilastNear
        cdef vec near, lastNear
        cdef float distance, penSize = <float>self.brush.penSize

        cdef vec leftTop, rightTop, rightBottom, leftBottom 

        cdef vec mousePosChunk = ivec2vec(&mousePos)
        mousePosChunk.y /= SCALE
        mousePosChunk.x /= SCALE
        cdef vec lastMousePosChunk = ivec2vec(&self.lastMousePosition)
        lastMousePosChunk.y /= SCALE
        lastMousePosChunk.x /= SCALE
            
        cdef int i, j
        for i in range(self.chunkRows):
                for j in range(self.chunkColumns):
                    chunk = &self.chunks[i][j]

                    # Calculating relative position between Chunk and Brush (on the left or right side, above or below)
                    inear.y = max(chunk.y, min(chunk.y + chunk.height, brushPos.y))
                    inear.x = max(chunk.x, min(chunk.x + chunk.width,  brushPos.x))
                    ilastNear.y = max(chunk.y, min(chunk.y + chunk.height, lastBrushPos.y))
                    ilastNear.x = max(chunk.x, min(chunk.x + chunk.width,  lastBrushPos.x))
                    # Nearest point downsize to the origin
                    inear = isubv(&inear, &brushPos)
                    ilastNear = isubv(&ilastNear, &lastBrushPos)

                    near = ivec2vec(&inear)
                    lastNear = ivec2vec(&ilastNear)
                    # if distance is lower than brush radius we have an intersection
                    distance = length(&near)
                    if distance <= penSize:
                        activateChunk(chunk)
                        continue
                    distance = length(&lastNear)
                    if distance <= penSize:
                        activateChunk(chunk)
                    continue

                    leftTop = vec(<float>chunk.y, <float>chunk.x)
                    rightTop = vec(<float>chunk.y, <float>(chunk.x + chunk.width))
                    rightBottom = vec(<float>(chunk.y + chunk.height), <float>(chunk.x + chunk.width))
                    leftBottom = vec(<float>(chunk.y + chunk.height), <float>chunk.x)

                    if linePointLen(mousePosChunk, lastMousePosChunk, leftTop) < penSize:
                        activateChunk(chunk)
                    elif linePointLen(mousePosChunk, lastMousePosChunk, rightTop) < penSize:
                        activateChunk(chunk)
                    elif linePointLen(mousePosChunk, lastMousePosChunk, rightBottom) < penSize:
                        activateChunk(chunk)
                    elif linePointLen(mousePosChunk, lastMousePosChunk, leftBottom) < penSize:
                        activateChunk(chunk)

    cpdef void paint_particles(self):
        cdef ivec mousePos
        cdef ParticleType tempPen

        mp = py.mouse.get_pos()
        mousePos.y = mp[1]
        mousePos.x = mp[0]

        if self.lastMousePosition.y == -1 and self.lastMousePosition.x == -1:
            self.lastMousePosition = mousePos

        mouseButtonPressed = py.mouse.get_pressed(num_buttons=3)
        keysPressed = py.key.get_pressed()

        if mouseButtonPressed[LEFT]:
            # Draw Particles
            paint(&self.brush, &self.board, mousePos, self.lastMousePosition)
            # Activate chunks
            self._activateChunkOnDraw(mousePos)
            
            self.lastMousePosition = mousePos

        elif mouseButtonPressed[RIGHT]:
            # Erase Particles
            tempPen = self.brush.pen
            self.brush.pen = EMPTY
            paint(&self.brush, &self.board, mousePos, self.lastMousePosition)
            self.brush.pen = tempPen
            # Activate chunks
            self._activateChunkOnDraw(mousePos)
            
            self.lastMousePosition = mousePos

        else:
            self.lastMousePosition.y = -1
            self.lastMousePosition.x = -1

        if keysPressed[py.K_s]:
            self.brush.pen = SAND
        elif keysPressed[py.K_q]:
            self.brush.pen = WOOD
        elif keysPressed[py.K_w]:
            self.brush.pen = WATER
        elif keysPressed[py.K_e]:
            self.brush.pen = FIRE
        elif keysPressed[py.K_r]:
            self.brush.pen = SMOKE
    
    cpdef void resize_cursor(self, int value):
        if 0 < self.brush.penSize + value < 50:
            self.brush.penSize += value

    cpdef void draw_cursor(self):
        py.draw.circle(self.win, (66, 66, 66), py.mouse.get_pos(), SCALE * self.brush.penSize, 2)

    cdef void activateChunksAround(self, int row, int column):
        activateChunk(&self.chunks[row][column])

        if 0 <= row - 1 < self.chunkRows:
            activateChunk(&self.chunks[row - 1][column])
        if 0 <= row + 1 < self.chunkRows:
            activateChunk(&self.chunks[row + 1][column])
        if 0 <= column - 1 < self.chunkColumns:
            activateChunk(&self.chunks[row][column - 1])
        if 0 <= column + 1 < self.chunkColumns:
            activateChunk(&self.chunks[row][column + 1])

        if 0 <= row - 1 < self.chunkRows and 0 <= column - 1 < self.chunkColumns:
            activateChunk(&self.chunks[row - 1][column - 1])
        if 0 <= row - 1 < self.chunkRows and 0 <= column + 1 < self.chunkColumns:
            activateChunk(&self.chunks[row - 1][column + 1])
        if 0 <= row + 1 < self.chunkRows and 0 <= column - 1 < self.chunkColumns:
            activateChunk(&self.chunks[row + 1][column - 1])
        if 0 <= row + 1 < self.chunkRows and 0 <= column + 1 < self.chunkColumns:
            activateChunk(&self.chunks[row + 1][column + 1])
    
    cdef void onUpdateChunk(self, Chunk* chunk):
        cdef bint haveMoved
        cdef Particle_t* cell
        cdef int i, j
        for i in reversed(range(chunk.height)):
            for j in range(chunk.width):
                cell = getParticle(&self.board, chunk.y + i, chunk.x + j)
                if cell.pType != EMPTY:
                    haveMoved = onUpdate(cell, &self.board)
                    if haveMoved:
                        self.activateChunksAround(
                            cell.pos.y / self.chunkSize, # row
                            cell.pos.x / self.chunkSize  # column
                        )

    # @Timeit(log="UPDATING", max_time=True, min_time=True, avg_time=True)
    cpdef void update(self):
        cdef Chunk* chunk
        cdef int row, column
        for row in reversed(range(self.chunkRows)):
            for column in range(self.chunkColumns):
                chunk = &self.chunks[row][column]
                if chunk.updateThisFrame:
                    self.onUpdateChunk(chunk)

    cdef void onRedrawBoard(self) nogil:
        cdef Particle_t* cell
        cdef int i, j
        with nogil, parallel():
            for i in prange(self.board.height):
                for j in prange(self.board.width):
                    cell = getParticle(&self.board, i, j)
                    self.surfaceArrayView[j][i] = cell.color
                    resetParticle(cell)

    # @Timeit(log="DRAWING", max_time=True, min_time=True, avg_time=True)
    cpdef void redraw(self):
        self.onRedrawBoard()
                
        py.surfarray.blit_array(self.surface, self.surfaceArray)
        cdef surf = py.transform.scale(self.surface, (WX, WY))
        self.win.blit(surf, (0, 0))
        
        cdef int[2][2] chunkRect
        cdef Chunk* chunk
        cdef int color
        for i in range(self.chunkRows):
            for j in range(self.chunkColumns):
                chunk = &self.chunks[i][j]
                
                chunkRect = [[chunk.x * <int>SCALE,     chunk.y * <int>SCALE],
                                [chunk.width * <int>SCALE, chunk.height * <int>SCALE]]
                            
                color = 0x00FF00 if chunk.updateThisFrame else 0xFF0000
                py.draw.rect(self.win, color, chunkRect, 1)

    cpdef void reset_chunks(self):
        cdef int row, column
        for row in range(self.chunkRows):
            for column in range(self.chunkColumns):
                updateChunk(&self.chunks[row][column])
    
    cdef void map_colors(self):
        pass




cdef class Timeit:
    cdef log
    cdef bint max_time, min_time, avg_time

    cdef double max_time_spent, min_time_spent
    cdef double avg_counter, avg_time_spent

    def __cinit__(self, log, bint max_time = False, bint min_time = False, bint avg_time= False):
        self.log = f"[{log}] | AT"

        self.max_time = max_time
        self.min_time = min_time
        self.avg_time = avg_time
        
        self.avg_counter = 0.0

        self.max_time_spent = 0
        self.min_time_spent = 1_000_000
        self.avg_time_spent = 0.0

    def __call__(self, f):
        self.log += f"[{f.__name__}]" + " | {:7.03f} ms"

        def wrapper(*args, **kwargs):
            # Function
            start = perf_counter()
            result = f(*args, **kwargs)
            end = perf_counter()
            end = 1000 * (end - start)

            # Logging
            log = self.log.format(end)
            if self.max_time:
                self.max_time_spent = max(end, self.max_time_spent)
                log += f" | Max {self.max_time_spent: 7.03f}"
            if self.min_time:
                self.min_time_spent = min(end, self.min_time_spent)
                log += f" | Min {self.min_time_spent: 7.03f}"
            if self.avg_time:
                self.avg_counter += 1.0
                self.avg_time_spent += end
                avg = self.avg_time_spent / self.avg_counter
                log += f" | Avg {avg: 7.03f}"
            print(log)

            return result
        return wrapper
