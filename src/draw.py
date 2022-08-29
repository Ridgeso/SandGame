from enum import IntEnum, auto

import glm
import pygame as py
import numpy as np

from values import *
from src import convert
import src.particle as particle
import src.tools as tools


class Display:
    def __init__(self, y: int, x: int) -> None:
        self.win_x = y
        self.win_y = x

        # Main window
        self.win = py.display.set_mode((self.win_x, self.win_y))
        # Simulation Texture
        self.surface = py.Surface((BOARD_X, BOARD_Y))

        # Board
        self.board = tools.Board(BOARD_Y, BOARD_X)
        self.brush = tools.Brush(particle.Sand)
        self.last_mouse_position = None

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
                temp_chunk_row.append(tools.Chunk(
                    row, column,
                    chunk_height, chunk_width,
                    True, False
                ))
            temp_chunks.append(temp_chunk_row)

        self.chunks = np.array(temp_chunks)
        self.chunk_threshold = SCALE * self.chunk_size

    class MouseKey(IntEnum):
        Left: int = 0
        Scroll: int = auto()
        Right: int = auto()

    def paint_particles(self) -> None:
        mouse_pos = glm.ivec2(*py.mouse.get_pos())
        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        keys_pressed = py.key.get_pressed()

        def activate_chunk_on_draw() -> None:
            if self.last_mouse_position is None:
                self.last_mouse_position = mouse_pos
            start_chunk_pos = glm.ivec2(self.last_mouse_position.x // self.chunk_threshold,
                                        self.last_mouse_position.y // self.chunk_threshold)
            end_chunk_pos = glm.ivec2(mouse_pos.x // self.chunk_threshold, mouse_pos.y // self.chunk_threshold)
            for chunk_pos in tools.interpolate_pos(start_chunk_pos, end_chunk_pos):
                self.activate_chunks_around(chunk_pos.y, chunk_pos.x)
            self.last_mouse_position = mouse_pos

        if mouse_button_pressed[self.MouseKey.Left]:
            # Draw Particles
            self.brush.paint(self.board, mouse_pos)
            # pos = glm.ivec2(mouse_pos.x // SCALE, mouse_pos.y // SCALE)
            # self.brush.paint_point(self.board, pos)
            # Activate chunks
            activate_chunk_on_draw()
        elif mouse_button_pressed[self.MouseKey.Right]:
            # Erase Particles
            temp_pen = self.brush.pen
            self.brush.pen = particle.Eraser
            self.brush.paint(self.board, mouse_pos)
            self.brush.pen = temp_pen
            # Activate chunks
            activate_chunk_on_draw()
        else:
            self.brush.last_mouse_on_board_position = None
            self.last_mouse_position = None

        if keys_pressed[py.K_s]:
            self.brush.pen = particle.Sand
        elif keys_pressed[py.K_q]:
            self.brush.pen = particle.Wood
        elif keys_pressed[py.K_w]:
            self.brush.pen = particle.Water
        elif keys_pressed[py.K_e]:
            self.brush.pen = particle.Fire
        elif keys_pressed[py.K_r]:
            self.brush.pen = particle.Smoke

    def resize_cursor(self, value: int) -> None:
        self.brush.pen_size += value

    def draw_cursor(self) -> None:
        py.draw.circle(self.win, (66, 66, 66), py.mouse.get_pos(), SCALE*self.brush.pen_size, 2)

    def activate_chunks_around(self, x: int, y: int) -> None:
        self.chunks[x, y].activate()

        if 0 <= x - 1 < self.chunks.shape[0]:
            self.chunks[x - 1, y].activate()
        if 0 <= x + 1 < self.chunks.shape[0]:
            self.chunks[x + 1, y].activate()
        if 0 <= y - 1 < self.chunks.shape[1]:
            self.chunks[x, y - 1].activate()
        if 0 <= y + 1 < self.chunks.shape[1]:
            self.chunks[x, y + 1].activate()

    def on_update_chunk(self, chunk: tools.Chunk) -> None:
        for i in reversed(range(chunk.width)):
            for j in range(chunk.height):
                cell = self.board[chunk.x + i, chunk.y + j]
                if cell is not None:
                    have_moved = cell.on_update(self.board)
                    if have_moved:
                        chunk_pos = glm.ivec2(cell.pos.x // self.chunk_size, cell.pos.y // self.chunk_size)
                        self.activate_chunks_around(chunk_pos.y, chunk_pos.x)

    # @Timeit(log="UPDATING", max_time=True, min_time=True)
    def update(self) -> None:
        for chunk_row in reversed(self.chunks):
            for chunk in chunk_row:
                if chunk.is_active():
                    self.on_update_chunk(chunk)

    # @Timeit(log="DRAWING", max_time=True, min_time=True)
    def redraw(self) -> None:
        for i, level in enumerate(self.board):
            for j, cell in enumerate(level):
                if cell is not None:
                    self.surface.set_at((j, i), cell.color)
                    cell.reset()
                else:
                    self.surface.set_at((j, i), 0x00_00_00)

        surf = py.transform.scale(self.surface, (WX, WY))
        self.win.blit(surf, (0, 0))

        if DEBUG:
            for chunk_row in self.chunks:
                for chunk in chunk_row:
                    chunk.draw_debug_chunk(self.win)

    def reset_chunks(self) -> None:
        for chunk_row in self.chunks:
            for chunk in chunk_row:
                chunk.update()

    def map_colors(self) -> None:
        data, offset_y, offset_x = convert.convert_img(WX, WY)

        which_color = {"Sand": 0, "Water": 0, "Wood": 0, "Fire": 0, "Smoke": 0}
        color_obj = {"Sand": particle.Sand,
                     "Water": particle.Water,
                     "Wood": particle.Wood,
                     "Fire": particle.Fire,
                     "Smoke": particle.Smoke}

        def filter_color(c: int) -> int:
            r = c >> 16 & 0xFF
            g = c >> 8 & 0xFF
            b = c >> 0 & 0xFF
            return r * r + g * g + b * b

        for i, pixels in enumerate(data):
            for j, pixel in enumerate(pixels):
                if not self.board.in_bounds(offset_y+i, offset_x+j):
                    return

                pixel_val = (pixel[0] << 16) + (pixel[1] << 8) + pixel[2]
                for color in particle.COLORS:
                    pos_difference = particle.COLORS[color] - pixel_val
                    which_color[color] = min(map(filter_color, pos_difference))

                best_pixel = color_obj[min(which_color, key=which_color.get)]
                self.board[offset_y+i][offset_x+j] = best_pixel(offset_y+i, offset_x+j)
