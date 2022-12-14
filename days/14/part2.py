import sys
from collections import namedtuple
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

Point = namedtuple("Point", "x,y")
START_POINT = Point(500, 0)


class Puzzle:
    def __init__(self):
        self.grid = set()
        self.bottom = 0
        self.sand = 0

    def block(self, point):
        self.grid.add(point)
        return point

    def add_vertical(self, start, stop):
        yrange = sorted([start.y, stop.y])
        x = start.x
        for yy in range(yrange[0], yrange[1] + 1):
            self.block(Point(x, yy))
            self.bottom = max(self.bottom, yy)

    def add_horizontal(self, start, stop):
        xrange = sorted([start.x, stop.x])
        y = start.y
        for xx in range(xrange[0], xrange[1] + 1):
            self.block(Point(xx, y))
        self.bottom = max(self.bottom, y)

    def add_lineseg(self, start, stop):
        if start.x == stop.x:
            self.add_vertical(start, stop)
        elif start.y == stop.y:
            self.add_horizontal(start, stop)
        else:
            raise Exception("ooops")

    def step_sand(self, loc):
        x, y = loc

        if y == self.bottom:
            return self.block(loc)

        if Point(x, y + 1) not in self.grid:
            return Point(x, y + 1)

        if Point(x - 1, y + 1) not in self.grid:
            return Point(x - 1, y + 1)

        if Point(x + 1, y + 1) not in self.grid:
            return Point(x + 1, y + 1)

        return self.block(loc)

    def drop_sand(self):
        prev_pt = START_POINT
        while True:
            next_pt = self.step_sand(prev_pt)
            if next_pt == START_POINT:
                return 0
            if next_pt == prev_pt:
                return 1
            prev_pt = next_pt


def parser(input_data):
    for line in input_data.splitlines():
        pairs = line.split(" -> ")
        for start, end in zip(pairs, pairs[1:]):
            start = eval(f"Point({start})")
            end = eval(f"Point({end})")
            yield (start, end)


def solve(input_data):
    puzzle = Puzzle()

    for start, end in parser(input_data):
        puzzle.add_lineseg(start, end)
    puzzle.bottom += 1

    count = 1
    while puzzle.drop_sand():
        count += 1
    return count


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE = """498,4 -> 498,6 -> 496,6
503,4 -> 502,4 -> 502,9 -> 494,9"""


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 93)], ids=idfn)
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":

    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v"])
    if ex != pytest.ExitCode.OK and ex != pytest.ExitCode.NO_TESTS_COLLECTED:
        print(f"tests FAILED ({ex})")
        sys.exit(1)
    else:
        print("tests PASSED")

    #  Actual input data generally has more iterations, turn off log
    ic.disable()
    my_input = Path("input.txt").read_text()
    result = solve(my_input)
    print(result)
