from typing import Type, Tuple
from enum import IntEnum

from src import convert
from src.particle import *


class Board(np.ndarray):
    def __new__(cls, y: int, x: int) -> 'Board':
        return super().__new__(cls, (y, x), dtype=object)

    def in_bounds(self, y: int, x: int) -> bool:
        return 0 <= y < self.shape[0] and 0 <= x < self.shape[1]

    def swap(self, cell: Particle, y: int, x: int):
        temp = self[cell.pos.y, cell.pos.x]
        self[cell.pos.y, cell.pos.x] = self[y, x]
        self[y, x] = temp

        if self[cell.pos.y, cell.pos.x] is not None:
            self[cell.pos.y, cell.pos.x].pos = cell.pos

        self[y, x].pos = Vec(y, x)


class Brush:
    def __init__(self, pen: Type[Particle]) -> None:
        self._pen: Type[Particle] = pen
        self._pen_size: int = PAINT_SCALE
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

    def paint(self, board: Board) -> None:
        pos = Vec(*py.mouse.get_pos())
        if self.last_mouse_position is None:
            self.last_mouse_position = Vec(pos.y, pos.x)
        pos.y //= SCALE
        pos.x //= SCALE

        slope = (pos - self.last_mouse_position)
        slope = slope.y / slope.x
        # TODO: fix taring brush effect
        for y in range(-self.pen_size, self.pen_size):
            offset = (self.pen_size**2 - y**2)**0.5
            offset = round(offset)
            for x in range(-offset, offset):
                if not board.in_bounds(pos.y + y, pos.x + x):
                    continue
                if self.pen.is_valid(board[pos.y + y, pos.x + x]):
                    board[pos.y + y, pos.x + x] = self.pen(pos.y + y, pos.x + x)

        self.last_mouse_position = pos


class Display:
    def __init__(self, y: int, x: int) -> None:
        self.win_x = y
        self.win_y = x

        self.win = py.display.set_mode((self.win_x, self.win_y))
    
        self.board = Board(BOARDY, BOARDX)
        self.brush = Brush(Sand)

    class MouseKey(IntEnum):
        Left: int = 0
        Scroll: int = auto()
        Right: int = auto()
        ScrollUp: int = auto()
        ScrollDown: int = auto()

    def paint_particles(self) -> None:
        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        keys = py.key.get_pressed()

        if mouse_button_pressed[self.MouseKey.Left]:
            self.brush.paint(self.board)
        else:
            self.brush.last_mouse_position = None

        if mouse_button_pressed[self.MouseKey.Scroll]:
            self.brush.pen = Sand
        elif mouse_button_pressed[self.MouseKey.Right]:
            self.brush.pen = Water        
        elif keys[py.K_q]:
            self.brush.pen = Wood
        elif keys[py.K_w]:
            self.brush.pen = Eraser
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

    def update(self) -> None:
        for level in reversed(self.board):
            for cell in level:
                if cell is not None:
                    cell.on_update(self.board)

    def redraw(self) -> None:
        for level in self.board:
            for cell in level:
                if cell is not None:
                    cell.draw(self.win)

    def map_colors(self) -> None:
        data, offset_y, offset_x = convert.convert_img()
        
        which_color = {"Sand": 0, "Water": 0, "Wood": 0, "Fire": 0, "Smoke": 0}
        color_obj = {"Sand": Sand, "Water": Water, "Wood": Wood, "Fire": Fire, "Smoke": Smoke}

        for i, pixels in enumerate(data):
            for j, pixel in enumerate(pixels):

                for color in COLORS:
                    pos_difference = COLORS[color] - pixel[:3]
                    which_color[color] = min(map(lambda v: v[0]*v[0] + v[1]*v[1] + v[2]*v[2], pos_difference))

                best_pixel = color_obj[min(which_color, key=which_color.get)]
                # TODO: What is wrong with this exception bloc
                try:
                    self.board[offset_y+i][offset_x+j] = best_pixel(offset_y+i, offset_x+j)
                except IndexError:
                    print(offset_y+i, offset_x+j)
                    return
