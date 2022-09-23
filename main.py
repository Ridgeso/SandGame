import pygame as py
from values import *
# from src.draw import Display
# from cver.cdraw import Display
from cver.cdrawPthread import Display


class SandSim:
    def __init__(self) -> None:
        py.init()

        self.display = Display(WX, WY)
        self.clock = py.time.Clock()

        self.sim = True
        self.is_running = True

    def run(self) -> None:
        while self.is_running:
            self.clock.tick(FPS)

            if self.sim:
                self.display.update()

            self.display.paint_particles()
            self.display.redraw()
            self.display.draw_cursor()

            if self.sim:
                self.display.reset_chunks()

            py.display.flip()

            self.handle_events()

            # print(self.clock.get_fps())
            py.display.set_caption(f"Sand Game | FPS {self.clock.get_fps():0.2f}")

    def handle_events(self) -> None:
        for event in py.event.get():
            if event.type == py.QUIT:
                self.is_running = False
                py.quit()
            elif event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    self.is_running = False
                    py.quit()
                if event.key == py.K_p:
                    self.sim = False if self.sim else True
                if event.key == py.K_n:
                    self.display.map_colors()
            elif event.type == py.MOUSEWHEEL:
                self.display.resize_cursor(event.y)


def main() -> None:
    sand_sim = SandSim()
    sand_sim.run()


if __name__ == '__main__':
    main()
