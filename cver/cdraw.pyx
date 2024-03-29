from values import *
import pygame as py
from time import perf_counter

import numpy as np
cimport numpy as np
np.import_array()

from cython cimport boundscheck, wraparound
cdef extern from "<pthread.h>" nogil:
    ctypedef int pthread_t
    ctypedef struct pthread_attr_t:
        pass

    int pthread_create(pthread_t *thread, pthread_attr_t *attr, void* (*start_routine) (void *), void *arg)
    int pthread_join(pthread_t thread, void **retval)

from libc.stdio cimport printf
from libc.stdlib cimport malloc, free

from cver.vector cimport *
from cver.cparticle cimport *
from cver.tools cimport *


ctypedef enum MouseKey:
    LEFT = 0
    SCROLL
    RIGHT


ctypedef struct UpdateArgs_t:
    # segment args
    Chunk** chunks
    int chunkRows, chunkColumns
    int chunkColumnStart, chunkColumnEnd
    # chunk args
    Board* board
    int chunkSize

ctypedef struct DrawArgs_t:
    Board* board
    int* surfaceArrayView
    int start, end
    int boardY


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

    cdef int threadsCount
    cdef int chunksSeparator, chunksSeparatorGap
    
    cdef pthread_t[8] threads
    cdef UpdateArgs_t[8] updateArgs
    cdef DrawArgs_t[4] drawArgs

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
        self.chunkRows = BOARD_Y // self.chunkSize + (1 if BOARD_Y % self.chunkSize else 0)
        self.chunkColumns = BOARD_X // self.chunkSize + (1 if BOARD_X % self.chunkSize else 0)

        self.chunks = <Chunk**>malloc(self.chunkRows * sizeof(Chunk*))

        cdef int row, column, chunkHeight, chunkWidth, offset
        
        for row in range(self.chunkRows):
            self.chunks[row] = <Chunk*>malloc(self.chunkColumns * sizeof(Chunk))

            # max chunk size or chunk loss
            offset = BOARD_Y - row * self.chunkSize
            chunkHeight = self.chunkSize if offset > self.chunkSize else offset
            
            for column in range(self.chunkColumns):
                # max chunk size or chunk loss
                offset = BOARD_X - row * self.chunkSize
                chunkWidth = self.chunkSize if offset > self.chunkSize else offset
                
                self.chunks[row][column] = makeChunk(
                    row * self.chunkSize, column * self.chunkSize,
                    chunkHeight, chunkWidth
                )
            
        cdef int i

        # Update Arguments
        if self.chunkColumns < 64:
            self.threadsCount = 2
        else:
            self.threadsCount = 4
        
        self.chunksSeparator = self.chunkColumns // (2 * self.threadsCount)
        self.chunksSeparatorGap = self.chunkColumns % (2 * self.threadsCount)
        for i in range(self.threadsCount * 2):
            self.updateArgs[i].chunks = self.chunks
            self.updateArgs[i].chunkRows = self.chunkRows
            self.updateArgs[i].chunkColumns = self.chunkColumns
            self.updateArgs[i].chunkColumnStart = i * self.chunksSeparator
            self.updateArgs[i].chunkColumnEnd = (i + 1) * self.chunksSeparator
            self.updateArgs[i].board = &self.board
            self.updateArgs[i].chunkSize = self.chunkSize
        self.updateArgs[self.threadsCount - 1].chunkColumnEnd += self.chunksSeparatorGap

        # Draw Arguments
        cdef int drawSep = self.board.height // 4
        cdef int drawSepGap = self.board.height % 4
        for i in range(4):
            self.drawArgs[i].board = &self.board
            self.drawArgs[i].surfaceArrayView = <int*>self.surfaceArray.data
            self.drawArgs[i].start = i * drawSep
            self.drawArgs[i].end = (i + 1) * drawSep
            self.drawArgs[i].boardY = <int>BOARD_Y
        self.drawArgs[3].end += drawSepGap
    
    def __dealloc__(self):
        freeBoard(&self.board)

        cdef int i
        for i in range(self.chunkRows):
            free(<void*>self.chunks[i])
        free(<void*>self.chunks)

    cdef void _activateChunkOnDraw(self, ivec mousePos):
        cdef Chunk* chunk
        cdef ivec brushPos = mousePos
        brushPos.y //= SCALE
        brushPos.x //= SCALE
        cdef ivec lastBrushPos = self.lastMousePosition
        lastBrushPos.y //= SCALE
        lastBrushPos.x //= SCALE

        cdef ivec inear, ilastNear
        cdef vec near, lastNear
        cdef float distance, penSize = <float>self.brush.penSize

        cdef vec leftTop, rightTop, rightBottom, leftBottom 

        cdef vec mousePosChunk = ivec2vec(&mousePos)
        mousePosChunk.y //= SCALE
        mousePosChunk.x //= SCALE
        cdef vec lastMousePosChunk = ivec2vec(&self.lastMousePosition)
        lastMousePosChunk.y //= SCALE
        lastMousePosChunk.x //= SCALE
            
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
                if distance <= penSize:  # Chunks around mouse position
                    activateChunk(chunk)
                    continue
                distance = length(&lastNear)
                if distance <= penSize:  # Chunks around mouse previous position
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
        cdef ivec chunkUpdate
        cdef bint haveMoved
        cdef Particle_t* cell
        cdef int i, j
        cdef int y, x
        for i in reversed(range(chunk.height)):
            for j in range(chunk.width):
                cell = getParticle(&self.board, chunk.y + i, chunk.x + j)
                if cell.pType == EMPTY:
                    continue

                haveMoved = onUpdate(cell, &self.board)
                # if not haveMoved:
                #     chunkUpdate.y = cell.pos.y / args.chunkSize
                #     chunkUpdate.x = cell.pos.x / args.chunkSize
                #     self.activateChunksAround(chunkUpdate.y, chunkUpdate.x)
                
        activateChunk(chunk)

    # @Timeit(log="UPDATING", max_time=True, min_time=True, avg_time=True)
    cpdef void onUpdate(self):
        cdef Chunk* chunk
        cdef int i, j
        for i in reversed(range(self.chunkRows)):
            for j in range(self.chunkColumns):
                chunk = &self.chunks[i][j]
                if chunk.updateThisFrame:
                    self.onUpdateChunk(chunk)

        # cdef int i
        # for i in range(0, self.threadsCount * 2, 2):
        #     pthread_create(&self.threads[i], NULL, &onUpdateSegment, &self.updateArgs[i])
        # for i in range(0, self.threadsCount * 2, 2):
        #     pthread_join(self.threads[i], NULL)

        # for i in range(1, self.threadsCount * 2, 2):
        #     pthread_create(&self.threads[i], NULL, &onUpdateSegment, &self.updateArgs[i])
        # for i in range(1, self.threadsCount * 2, 2):
        #     pthread_join(self.threads[i], NULL)

    # @Timeit(log="DRAWING", max_time=True, min_time=True, avg_time=True)
    cpdef void redraw(self):
        cdef int i
        for i in range(4):
            pthread_create(&self.threads[i], NULL, &drawSegmentC, &self.drawArgs[i])
        
        for i in range(4):
            pthread_join(self.threads[i], NULL)
                
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


@boundscheck(False)
@wraparound(False)
cdef void* onUpdateSegment(void* argsPass) nogil:
    cdef UpdateArgs_t* args = <UpdateArgs_t*>argsPass
    # Segment variables
    cdef Chunk* chunk
    cdef int row, column
    cdef int seperator
    
    # Chunk variables
    cdef ivec chunkUpdate
    cdef bint haveMoved
    cdef Particle_t* cell
    cdef int i, j
    cdef int y, x

    # Segment script
    for row in reversed(range(args.chunkRows)):
        for column in range(args.chunkColumnStart, args.chunkColumnEnd):
            chunk = &args.chunks[row][column]
            if not chunk.updateThisFrame:
                continue

            # Chunk script
            for i in reversed(range(chunk.height)):
                for j in range(chunk.width):
                    cell = getParticle(args.board, chunk.y + i, chunk.x + j)
                    if cell.pType == EMPTY:
                        continue

                    haveMoved = onUpdate(cell, args.board)
                    if not haveMoved:
                        continue
                    
                    # activateChunksAround
                    # chunkUpdate.y = cell.pos.y / args.chunkSize
                    # chunkUpdate.x = cell.pos.x / args.chunkSize
                    # for y in range(-1, 2):
                    #     for x in range(-1, 2):
                    #         if y == 0 == x:
                    #             continue
                    #         if not 0 <= chunkUpdate.y + y < args.chunkRows:
                    #             continue
                    #         if not 0 <= chunkUpdate.x + x < args.chunkColumns:
                    #             continue
                    #         activateChunk(&args.chunks[chunkUpdate.y + y][chunkUpdate.x + x])
            activateChunk(chunk)
    return NULL

@boundscheck(False)
@wraparound(False)
cdef void* drawSegmentC(void* argsPass) nogil:
    cdef DrawArgs_t* args = <DrawArgs_t*>argsPass
    cdef Particle_t* cell
    cdef int i, j
    for i in range(args.start, args.end):
        for j in range(args.board.width):
            cell = getParticle(args.board, i, j)
            args.surfaceArrayView[i + j * args.boardY] = cell.color
            resetParticle(cell)
    return NULL


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
