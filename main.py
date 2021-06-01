import pygame as py
from draw import (
    redraw,
    paint_particles,
    map_colors,
    WY, WX, FPS,
    SCALE, PAINT_SCALE
)
# from cdraw import *

py.init()

win = py.display.set_mode((WX, WY))
clock = py.time.Clock()


def main():
    sim = False
    run = True
    while run:
        clock.tick(FPS)

        win.fill((0, 0, 0))
        redraw(win, sim)
        paint_particles()
        py.draw.circle(win, (66, 66, 66), py.mouse.get_pos(), PAINT_SCALE*(SCALE+1), 2)
        py.display.flip()

        # print(clock.get_fps())

        for event in py.event.get():
            if event.type == py.QUIT:
                run = False
                py.quit()
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    run = False
                    py.quit()
                if event.key == py.K_p:
                    sim = False if sim else True
                if event.key == py.K_LEFTBRACKET:
                    pass
                if event.key == py.K_RIGHTBRACKET:
                    pass
                if event.key == py.K_n:
                    map_colors()


if __name__ == '__main__':
    main()
