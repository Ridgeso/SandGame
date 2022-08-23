import time
import pytest
from src.tools import *

MAX_TIME = 1


@pytest.fixture
def start():
    return (
        Vec(0, 0),
        Vec(0, 0),
        Vec(0, 0),
        Vec(0, 0),
        Vec(0, 0),
        Vec(0, 0)
    )


@pytest.fixture
def end():
    return (
        Vec(10, 0),
        Vec(0, 10),
        Vec(5, 5),
        Vec(5, 1),
        Vec(0, 0),
        Vec(0.5, 0.1)
    )


def test_interpolate_pos(start, end):
    for s, e in zip(start, end):
        last_pos = None

        direction = interpolate_pos(s, e)

        start = time.perf_counter()
        for pos in direction:
            assert time.perf_counter() - start < MAX_TIME, TimeoutError(f"Infinity loop for [{s, e}]")
            last_pos = pos
        assert last_pos == e.round()
