from values import *
import pygame as pg

from libc.stdio import printf
from libc.stdlib import malloc, free

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
        self.win = py.display.set_mode((self.win_x, self.win_y))
        # Simulation Texture
        self.surface = py.Surface((BOARD_X, BOARD_Y))

        # Board
        self.board = initBoard(BOARD_Y, BOARD_X)
        self.brush = initBrush()

        self.lastMousePosition.y = -1
        self.lastMousePosition.x = -1

        # Chunks
        self.chunkSize = 10  # 10 x 10
        self.chunkRows = BOARD_Y / self.chunkSize
        self.chunkColumns = BOARD_X / self.chunkSize

        # self.chunks = <Chunk**>malloc(self.chunkRows * sizeof(Chunk*))

        # cdef int row, chunkHeight, chunkWidth, offset
        # # for row in range(0, BOARD_Y, self.chunkSize):
        # for row in range(self.chunkRows):
        #     self.chunks[row] = <Chunk*>malloc(self.chunkColumns * sizeof(Chunk))
        #     # max chunk size or chunk loss
        #     offset = BOARD_Y - row * self.chunkSize
        #     chunkHeight = self.chunkSize if offset > self.chunkSize else offset
        #     # for column in range(0, BOARD_X, self.chunkSize):
        #     for column in range(self.chunkColumns):
        #         # max chunk size or chunk loss
        #         offset = BOARD_X - row * self.chunkSize
        #         chunk_width = self.chunkSize if offset > self.chunkSize else offset
        #         self.chunks[row][column] = makeChunk(
        #             row * self.chunkSize, column * self.chunkSize,
        #             chunkHeight, chunkWidth
        #         )
            
        # self.chunkThreshold = SCALE * self.chunkSize

    def __dealloc__(self):
        freeBoard(&self.board)

        # cdef int i
        # for i in range(self.chunkRows):
        #     free(<void*>self.chunks[i])
        # free(<void*>self.chunks)

    cdef void _activateChunkOnDraw(self, ivec mousePos):
        cdef ivec startChunkPos, endChunkPos

        startChunkPos.y = self.lastMousePosition.y // self.chunkThreshold
        startChunkPos.x = self.lastMousePosition.x // self.chunkThreshold

        endChunkPos.y = mousePos.y // self.chunkThreshold
        endChunkPos.x = mousePos.x // self.chunkThreshold
        
        cdef ivec* chunkPos = interpolatePos(&startChunkPos, &endChunkPos)
        while chunkPos != NULL:
            self.activateChunksAround(chunkPos.y, chunkPos.x)
            chunkPos = interpolatePos(NULL, &endChunkPos)
        
        self.lastMousePosition = mousePos

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
                            cell.pos.y // self.chunk_size, # row
                            cell.pos.x // self.chunk_size  # column
                        )

    
    cpdef void update(self):
        cdef Chunk* chunk
        cdef int row, column
        for row in reversed(range(self.chunkRows)):
            for column in range(self.chunkColumns):
                chunk = &self.chunks[row][column]
                if chunk.updateThisFrame:
                    self.onUpdateChunk(chunk)
    
    cpdef void redraw(self):
        cdef Particle_t* cell
        cdef int i, j
        for i in range(self.board.height):
            for j in range(self.board.width):
                cell = getParticle(&self.board, i, j)
                
                self.surface.set_at((j, i), cell.color)
                resetParticle(cell)
                
        surf = py.transform.scale(self.surface, (WX, WY))
        self.win.blit(surf, (0, 0))
    
    cpdef void reset_chunks(self):
        cdef int row, column
        for row in range(self.chunkRows):
            for column in range(self.chunkColumns):
                updateChunk(&self.chunks[row][column])
    
    cdef void map_colors(self):
        pass
