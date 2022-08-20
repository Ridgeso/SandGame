from typing import Type, Tuple
from enum import IntEnum

import pygame as py
import numpy as np

from src import convert
from src.particle import *
from src.tools import *


class Display:
    def __init__(self, y: int, x: int) -> None:
        self.win_x = y
        self.win_y = x

        # Main window
        self.win = py.display.set_mode((self.win_x, self.win_y))
        # Simulation Texture
        self.surface = py.Surface((BOARD_X, BOARD_Y))

        # Board
        self.board = Board(BOARD_Y, BOARD_X)
        self.board[10, 50] = Sand(10, 50)
        self.brush = Brush(Sand)

        # Chunks
        self.chunk_size = 10  # 10 x 10
        temp_chunks = []
        for row in range(0, BOARD_Y, self.chunk_size):
            temp_chunk_row = []
            # max chunk size or chunk loss
            chunk_height = self.chunk_size if BOARD_Y - row > self.chunk_size else BOARD_Y - row
            for column in range(0, BOARD_X, self.chunk_size):
                # max chunk size or chunk loss
                chunk_width = self.chunk_size if BOARD_X - column > self.chunk_size else BOARD_X - column
                # temp_chunks.append(Chunk(
                temp_chunk_row.append(Chunk(
                    row, column,
                    chunk_height, chunk_width,
                    True, False
                ))
            temp_chunks.append(temp_chunk_row)

        self.chunks = np.array(temp_chunks)
        self.chunk_threshold = SCALE * self.chunk_size
        # if i change my mind
        # rand_pos = Vec(635, 324)
        # x = rand_pos.x // SCALE // self.chunk_size
        # y = rand_pos.y // SCALE // self.chunk_size
        self.max_time = 0

    class MouseKey(IntEnum):
        Left: int = 0
        Scroll: int = auto()
        Right: int = auto()

    def paint_particles(self) -> None:
        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        keys = py.key.get_pressed()

        mouse_pos = Vec(*py.mouse.get_pos())
        chunk_pos = Vec(mouse_pos.x // self.chunk_threshold, mouse_pos.y // self.chunk_threshold)
        mouse_chunk = self.chunks[chunk_pos.y, chunk_pos.x]
        mouse_chunk.updated_this_frame = True

        def activate_chunks_on_draw():
            for chunk_row in self.chunks:
                for chunk in chunk_row:
                    if chunk_intersect_with_brush(chunk, self.brush, mouse_pos):
                        chunk.activate()
                        chunk.update()

        if mouse_button_pressed[self.MouseKey.Left]:
            self.brush.paint(self.board, mouse_pos)
            # Activate chunks
            activate_chunks_on_draw()
        elif mouse_button_pressed[self.MouseKey.Right]:
            self.brush.erase(self.board, mouse_pos)
            # Activate chunks
            activate_chunks_on_draw()
        else:
            self.brush.last_mouse_position = None

        if keys[py.K_s]:
            self.brush.pen = Sand
        elif keys[py.K_q]:
            self.brush.pen = Wood
        elif keys[py.K_w]:
            self.brush.pen = Water
        elif keys[py.K_e]:
            self.brush.pen = Fire
        elif keys[py.K_r]:
            self.brush.pen = Smoke

    def resize_cursor(self, value: int) -> None:
        self.brush.pen_size += value

    def draw_cursor(self) -> None:
        py.draw.circle(self.win, (66, 66, 66), py.mouse.get_pos(), SCALE*self.brush.pen_size, 2)

    def fill(self, color: Tuple[int, ...]) -> None:
        self.win.fill(color)

    def _partial_update(self, chunk: Tuple[int, int]) -> None:
        for level in reversed(range(self.board.shape[0])):
            for cell in range(*chunk):
                if self.board[level, cell] is not None:
                    self.board[level, cell].on_update(self.board)

    def update_chunk(self, chunk: Chunk) -> None:
        for i in reversed(range(chunk.width)):
            for j in range(chunk.height):
                cell = self.board[chunk.x + i, chunk.y + j]
                if cell is not None:
                    have_moved = cell.on_update(self.board)
                    if have_moved:
                        cell_chunk = Vec(cell.pos.y // self.chunk_size, cell.pos.x // self.chunk_size)
                        self.chunks[cell_chunk.y, cell_chunk.x].activate()

                    cell.been_updated = True

    @Timeit(log="[UPDATING]", max_time=True, min_time=True)
    def update(self) -> None:
        # TODO: Fix Bug that not empty chunks above empty is not updating
        for chunk_row in reversed(self.chunks):
            for chunk in chunk_row:
                if not chunk.is_active():
                    continue
                self.update_chunk(chunk)
        for chunk_row in self.chunks:
            for chunk in chunk_row:
                chunk.update()

    def redraw(self) -> None:
        for j, level in enumerate(self.board):
            for i, cell in enumerate(level):
                if cell is not None:
                    self.surface.set_at((i, j), cell.color)
                    cell.been_updated = False
                else:
                    self.surface.set_at((i, j), 0x00_00_00)

        surf = py.transform.scale(self.surface, (WX, WY))
        self.win.blit(surf, (0, 0))

        for chunk_row in self.chunks:
            for chunk in chunk_row:
                chunk.draw_debug_chunk(self.win)

    def map_colors(self) -> None:
        data, offset_y, offset_x = convert.convert_img(WX, WY)

        which_color = {"Sand": 0, "Water": 0, "Wood": 0, "Fire": 0, "Smoke": 0}
        color_obj = {"Sand": Sand, "Water": Water, "Wood": Wood, "Fire": Fire, "Smoke": Smoke}

        for i, pixels in enumerate(data):
            for j, pixel in enumerate(pixels):
                if not self.board.in_bounds(offset_y+i, offset_x+j):
                    return
                for color in COLORS:
                    pos_difference = COLORS[color] - pixel[:3]
                    which_color[color] = min(map(lambda v: v[0]*v[0] + v[1]*v[1] + v[2]*v[2], pos_difference))

                best_pixel = color_obj[min(which_color, key=which_color.get)]
                self.board[offset_y+i][offset_x+j] = best_pixel(offset_y+i, offset_x+j)
