from values import *
import pygame as pg

from libc.stdio import printf
from libc.stdlib import malloc, free
from cparticle cimport *
from tools cimport *

cdef extern from "vector.h": *


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
        self.lastMousePosition = None

        # Chunks
        self.chunkSize = 10  # 10 x 10
        self.chunkRows = BOARD_Y / self.chunkSize
        self.chunkColumns = BOARD_X / self.chunkSize

        self.chunks = <Chunk**>malloc(self.chunkRows * sizeof(Chunk*))

        cdef int row, chunkHeight, chunkWidth, offset
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
                chunk_width = self.chunkSize if offset > self.chunkSize else offset
                self.chunks[row][column] = makeChunk(
                    row * self.chunkSize, column * self.chunkSize,
                    chunkHeight, chunkWidth
                )
            
        self.chunkThreshold = SCALE * self.chunkSize

    def __dealloc__(self):
        freeBoard(&self.board)

        cdef int i
        for i in range(self.chunkRows):
            free(<void*>self.chunks[i])
        free(<void*>self.chunks)

    cdef void paintParticles(self):
        pass
    
    cdef void resizeCursor(self):
        pass
    
    cdef void activateChunkAround(self, int row, int column):
        pass
    
    cdef void inUpdateChunk(self, Chunk* chunk):
        pass
    
    cdef void update(self):
        pass
    
    cdef void redraw(self):
        pass
    
    cpdef void resetChunks(self):
        cdef int row, column
        for row in range(self.chunkRows):
            for column in range(self.chunkColumns):
                updateChunk(&self.chunks[row][column])
    
    cdef void map_colors(self):
        pass
