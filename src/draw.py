from typing import Type, Tuple
from enum import IntEnum
import concurrent.futures as ct
import multiprocessing as mp

from src import convert
from src.particle import *


class Board(np.ndarray):
    def __new__(cls, y: int, x: int) -> 'Board':
        return super().__new__(cls, (y, x), dtype=object)

    def in_bounds(self, y: int, x: int) -> bool:
        return 0 <= y < self.shape[0] and 0 <= x < self.shape[1]

    def swap(self, cell: Particle, y: int, x: int):
        temp = self[cell.pos.y, cell.pos.x]
        if temp is None:
            breakpoint()
        self[cell.pos.y, cell.pos.x] = self[y, x]
        self[y, x] = temp

        if self[cell.pos.y, cell.pos.x] is not None:
            self[cell.pos.y, cell.pos.x].pos = cell.pos

        self[y, x].pos = Vec(y, x)


class Brush:
    def __init__(self, pen: Type[Particle]) -> None:
        self._pen: Type[Particle] = pen
        self._pen_size: int = PAINT_SCALE
        self.PendDifference: int = self._pen_size
        self.last_mouse_position: Union[Vec, None] = Vec()

    @property
    def pen(self) -> Type[Particle]:
        return self._pen

    @pen.setter
    def pen(self, value: Type[Particle]):
        self._pen = value

    @property
    def pen_size(self) -> int:
        return self._pen_size

    @pen_size.setter
    def pen_size(self, value: int):
        if value > 0:
            self._pen_size = value
            self.PendDifference = value

    def paint_point(self, board: Board, point: Vec) -> None:
        if not board.in_bounds(point.y, point.x):
            return
        if self.pen.is_valid(board[point.y, point.x]):
            board[point.y, point.x] = self.pen(point.y, point.x)

    def paint_from_to(self, board: Board, start: Vec, end: Vec, slope: Union[Vec, None] = None) -> None:
        for pos in interpolate_pos(start, end, slope):
            self.paint_point(board, pos)

    def paint(self, board: Board) -> None:
        # TODO: draw in 'Display.boards'
        pos = Vec(*py.mouse.get_pos())
        pos.y, pos.x = pos.x, pos.y

        pos.y //= SCALE
        pos.x //= SCALE

        if self.last_mouse_position is None:
            self.last_mouse_position = Vec(pos.y, pos.x)
        slope = pos - self.last_mouse_position
        length = pow(pow(slope.y, 2) + pow(slope.x, 2), 0.5)
        if length != 0:
            slope.y /= length
            slope.x /= length

        for y in range(-self.pen_size, self.pen_size):
            offset = pow((pow(self.pen_size, 2) - pow(y, 2)), 0.5)
            offset = round(offset)
            for x in range(-offset, offset):
                r_phi = Vec(y, x)
                point = pos + r_phi
                last_point = self.last_mouse_position + r_phi
                self.paint_from_to(board, last_point, point, slope)
        self.last_mouse_position = pos

    def erase(self, board):
        pen = self.pen
        self.pen = Eraser
        self.paint(board)
        self.pen = pen


class Display:
    CHUNKS_COUNT: int = 4
    CELLS_IN_ROW: int = WX//SCALE
    CHUNKS_SIZE = CELLS_IN_ROW // CHUNKS_COUNT

    def __init__(self, y: int, x: int) -> None:
        self.win_x = y
        self.win_y = x

        self.win = py.display.set_mode((self.win_x, self.win_y))

        self.board = Board(BOARDY, BOARDX)
        self.brush = Brush(Sand)

        # Threading
        # TODO: merge 'board' with 'boards'
        self.boards = np.array([Board(BOARDY, self.CELLS_IN_ROW) for _ in range(self.CHUNKS_COUNT)])
        self.odd_chunks = np.array([
            (self.CHUNKS_SIZE * i, self.CHUNKS_SIZE + self.CHUNKS_SIZE * i)
            for i in range(0, self.CHUNKS_COUNT, 2)])
        self.even_chunks = np.array([
            (self.CHUNKS_SIZE * i, self.CHUNKS_SIZE + self.CHUNKS_SIZE * i)
            for i in range(1, self.CHUNKS_COUNT, 2)])

    class MouseKey(IntEnum):
        Left: int = 0
        Scroll: int = auto()
        Right: int = auto()

    def paint_particles(self) -> None:
        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        keys = py.key.get_pressed()

        if mouse_button_pressed[self.MouseKey.Left]:
            self.brush.paint(self.board)
        elif mouse_button_pressed[self.MouseKey.Right]:
            self.brush.erase(self.board)
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

    def resize_cursor(self, value: int):
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

    @staticmethod
    def _partial_board_update(self, chunk: Board) -> None:
        for level in reversed(chunk):
            for cell in level:
                if cell is not None:
                    cell.on_update(chunk)

    def update(self) -> None:
        # TODO: group screen into chunks of last moved cells
        # for level in reversed(self.board):
        #     for cell in level:
        #         if cell is not None:
        #             cell.on_update(self.board)
        with ct.ThreadPoolExecutor() as t:
            t.map(self._partial_board_update, self.boards)
        # with ct.ThreadPoolExecutor() as t:
        #     t.map(self._partial_update, self.odd_chunks)
        # with ct.ThreadPoolExecutor() as t:
        #     t.map(self._partial_update, self.even_chunks)

    def _partial_draw(self, chunk):
        for level in range(self.board.shape[0]):
            for cell in range(*chunk):
                if self.board[level, cell] is not None:
                    self.board[level, cell].draw_and_reset(self.win)

    def redraw(self) -> None:
        # for level in self.board:
        #     for cell in level:
        #         if cell is not None:
        #             cell.draw_and_reset(self.win)
        with ct.ThreadPoolExecutor() as t:
            t.map(self._partial_draw, self.odd_chunks)
        with ct.ThreadPoolExecutor() as t:
            t.map(self._partial_draw, self.even_chunks)

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
