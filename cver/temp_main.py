import pygame as py
from values import *
from cdraw import Display


class SandSim:
    def __init__(self) -> None:
        py.init()

        self.display = Display(WX, WY)


def main() -> None:
    sand_sim = SandSim()


if __name__ == '__main__':
    main()
