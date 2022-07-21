from typing import Type
from enum import IntEnum
from src import convert

from src.particle import *


class Board(np.ndarray):
    def __new__(cls, x: int, y: int) -> 'Board':
        return super().__new__(cls, (x, y), dtype=np.object)

    def check_spot(self, x: int, y: int) -> bool:
        return 0 <= x < self.shape[0] and 0 <= y < self.shape[1]


class Brush:
    def __init__(self, pen: Type[Particle]) -> None:
        self.pen = pen
        self.pen_size = PAINT_SCALE

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
        pos_x, pos_y = py.mouse.get_pos()
        pos_y //= SCALE
        pos_x //= SCALE

        # rand_x, rand_y = np.random.randint(-PAINT_RANGE, PAINT_RANGE + 1, size=(2, PAINT_SCALE))

        # for x, y in zip(rand_x, rand_y):
        for x in range(-self.pen_size, self.pen_size):
            for y in range(-self.pen_size, self.pen_size):
                if not board.check_spot(pos_y+y, pos_x+x):
                    continue
                if self.pen.is_valid_spot(board[pos_y + y][pos_x + x]):
                    board[pos_y + y][pos_x + x] = self.pen(pos_y + y, pos_x + x)


class Display:
    def __init__(self, x: int, y: int) -> None:
        self.win_x = x
        self.win_y = y

        self.win = py.display.set_mode((self.win_x, self.win_y))
    
        self.board = Board(BOARDY, BOARDX)
        self.brush = Brush(Sand)

    class MouseKey(IntEnum):
        Left = 0
        Scroll = auto()
        Right = auto()

    def paint_particles(self) -> None:
        mouse_button_pressed = py.mouse.get_pressed(num_buttons=3)
        keys = py.key.get_pressed()

        if mouse_button_pressed[self.MouseKey.Left]:
            self.brush.paint(self.board)

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
        
        if keys[py.K_LEFTBRACKET]:
            self.brush.pen_size -= 1
        elif keys[py.K_RIGHTBRACKET]:
            self.brush.pen_size += 1

    def draw_cursor(self) -> None:
        py.draw.circle(self.win, (66, 66, 66), py.mouse.get_pos(), SCALE*self.brush.pen_size, 2)

    def fill(self, color: Tuple[int, ...]) -> None:
        self.win.fill(color)

    def update(self) -> None:
        for level in reversed(self.board):
            for cell in level:
                if cell is not None:
                    cell.update_frame(self.board)

    def redraw(self) -> None:
        for level in self.board:
            for cell in level:
                if cell is not None:
                    cell.draw(self.win)

    def map_colors(self) -> None:
        data, offset_y, offset_x = convert.convert_img()
        
        which_color = {"Sand": 0, "Water": 0, "Wood": 0, "Fire": 0, "Smoke": 0}

        for i, pixels in enumerate(data):
            for j, pixel in enumerate(pixels):

                for color in COLORS:
                    pos_difference = COLORS[color] - pixel[:3]
                    which_color[color] = min(map(lambda v: v[0]*v[0] + v[1]*v[1] + v[2]*v[2], pos_difference))

                best_pixel = COLORS_OBJ[min(which_color, key=which_color.get)]
                # TODO: What is wrong with this exception bloc
                try:
                    self.board[offset_y+i][offset_x+j] = best_pixel(offset_y+i, offset_x+j)
                except IndexError:
                    print(offset_y+i, offset_x+j)
                    return
