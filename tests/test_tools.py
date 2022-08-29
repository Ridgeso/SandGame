import time
from typing import Iterable
import pytest
from src.tools import *

MAX_TIME = 3


@pytest.fixture
def start():
    return (
        # Vec(0, 0),
        # Vec(0, 0),
        # Vec(0, 0),
        # Vec(0, 0),
        # Vec(0, 0),
        # Vec(0, 0),
        # Vec(0, 0),
        # Vec(0, 0),
        glm.ivec2(0, 0),
        glm.ivec2(0, 0),
        glm.ivec2(0, 0),
        glm.ivec2(0, 0),
        glm.ivec2(0, 0),
        glm.ivec2(0, 0),
        glm.ivec2(0, 0),
        glm.ivec2(0, 0),
    )


@pytest.fixture
def end():
    return (
        glm.ivec2(10, 0),
        glm.ivec2(0, 10),
        glm.ivec2(5, 5),
        glm.ivec2(5, 1),
        glm.ivec2(0, 0),
        # Vec(0.5, 0.1),
        glm.ivec2(7, 7),
        glm.ivec2(0.1, 124),
    )


def test_interpolate_pos(start: Iterable[Vec], end: Iterable[Vec]) -> None:
    for i, (s, e) in enumerate(zip(start, end), 1):
        print(f"\nTEST NUMBER {i} WITH DATA {s} | {e}")
        last_pos = None

        direction = interpolate_pos(s, e)

        start = time.perf_counter()
        for pos in direction:
            assert time.perf_counter() - start < MAX_TIME, TimeoutError(f"Infinity loop")
            last_pos = pos

        # assert round(last_pos.magnitude()) == round(e.magnitude()), ValueError("Destination not reached")
        assert round(glm.length(glm.vec2(last_pos))) == round(glm.length(glm.vec2(e))),\
            ValueError("Destination not reached")


def test_interpolate_pos_dda(start: Iterator[Vec], end: Iterator[Vec]) -> None:
    for i, (s, e) in enumerate(zip(start, end), 1):
        print(f"\nTEST NUMBER {i} WITH DATA {s} | {e}")
        last_pos = None
        prev_pos = s

        direction = interpolate_pos_dda(s, e)

        start_time = time.perf_counter()
        for pos in direction:
            assert time.perf_counter() - start_time < MAX_TIME, TimeoutError(f"Infinity loop")
            last_pos = prev_pos
            prev_pos = pos

        # end = e.round()
        # assert last_pos == end\
        #     or last_pos == end - Vec(1, 0)\
        #     or last_pos == end - Vec(0, 1)\
        #     or last_pos == end + Vec(1, 0)\
        #     or last_pos == end + Vec(0, 1), ValueError("Destination not reached")

        assert last_pos == e\
            or last_pos == e - glm.ivec2(1, 0)\
            or last_pos == e - glm.ivec2(0, 1)\
            or last_pos == e + glm.ivec2(1, 0)\
            or last_pos == e + glm.ivec2(0, 1), ValueError(f"Destination not reached for {last_pos}")