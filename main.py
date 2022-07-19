import pygame as py
from draw import (
    Display,
    WX, WY, FPS
)
# from cdraw import *


class SandSim:
    def __init__(self, ) -> None:
            py.init()

            self.display = Display(WX, WY)
            self.clock = py.time.Clock()

            self.sim = False
            self.is_running = True
    
    def run(self) -> None:
        while self.is_running:
            self.clock.tick(FPS)

            self.display.fill((0, 0, 0))
            self.display.paint_particles()
            
            if self.sim:
                self.display.update()

            self.display.redraw()
            self.display.draw_cursor()
            
            py.display.flip()

            # print(clock.get_fps())

            self.handle_events()

    def handle_events(self) -> None:
        for event in py.event.get():
            if event.type == py.QUIT:
                self.is_running = False
                py.quit()
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    self.is_running = False
                    py.quit()
                if event.key == py.K_p:
                    self.sim = False if self.sim else True
                if event.key == py.K_LEFTBRACKET:
                    self.display.brush_size -= 1
                if event.key == py.K_RIGHTBRACKET:
                    self.display.brush_size += 1
                if event.key == py.K_n:
                    self.display.map_colors()


def main() -> None:
    sand_sim = SandSim()
    sand_sim.run()


if __name__ == '__main__':
    main()
