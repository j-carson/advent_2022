import sys
from collections import UserDict, namedtuple
from pathlib import Path
from string import ascii_lowercase

import numpy as np
import pytest
from icecream import ic

# a number longer than any path we'll be making
NOT_REACHED = 1_000_000


# --> Puzzle solution


def parse(input_text):
    all_lines = []
    for i, line in enumerate(input_text.splitlines()):
        if "S" in line:
            start_row = i
            start_col = line.index("S")
            line = line.replace("S", "a")
        if "E" in line:
            dest_row = i
            dest_col = line.index("E")
            line = line.replace("E", "z")
        all_lines.append([ascii_lowercase.index(let) for let in line])

    data = np.array(all_lines)
    return data, (start_row, start_col), (dest_row, dest_col)


WorkItem = namedtuple("WorkItem", "score,startpointer")


class Puzzle:
    def __init__(self, grid, goal):
        self.grid = grid
        self.scores = np.full_like(self.grid, NOT_REACHED)
        self.goal = goal
        self.work_list = []

    def step_legal(self, start, end):
        # assume start (current pos) is legal, but end could be trying
        # to walk off the edge
        if not 0 <= end[0] < self.grid.shape[0]:
            ic("invalid index x")
            return False
        if not 0 <= end[1] < self.grid.shape[1]:
            ic("invalid index y")
            return False

        # check elevation change rule
        start_elevation = self.grid[start]
        end_elevation = self.grid[end]
        if not (end_elevation <= start_elevation + 1):
            ic("invalid elevation")
            return False

        # check already visited
        return self.scores[end] == NOT_REACHED

    def get_steps(self, curpos):
        x, y = curpos
        candidates = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]

        for next_step in candidates:
            if self.step_legal(curpos, next_step):
                yield next_step

    def path_search(self, pos, cur_depth):
        for step in self.get_steps(pos):
            self.scores[step] = cur_depth + 1
            if step == self.goal:
                return
            self.work_list.append(WorkItem(cur_depth + 1, step))

    def walk(self, start):
        self.scores[start] = 0
        self.path_search(start, 0)

        while self.scores[self.goal] == NOT_REACHED:
            if self.work_list:
                next_job = self.work_list.pop(0)
                self.path_search(next_job.startpointer, next_job.score)
            else:
                # goal is not reachable from here
                return NOT_REACHED

        return self.scores[self.goal]


def solve1(input_data):
    grid, start, stop = parse(input_data)

    puzzle = Puzzle(grid, stop)
    return puzzle.walk(start)


def solve2(input_data):
    grid, start, stop = parse(input_data)
    n_rows, n_cols = grid.shape
    running_min = NOT_REACHED

    for i in range(n_rows):
        for j in range(n_cols):
            if grid[i, j] == 0:
                puzzle = Puzzle(grid, stop)
                score = puzzle.walk((i, j))
                running_min = min(score, running_min)

    return running_min


# --> Test driven development helpers

EXAMPLE = """Sabqponm
abcryxxl
accszExk
acctuvwj
abdefghi"""

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 31)], ids=idfn)
def test_part1(sample_data, sample_solution) -> None:
    assert solve1(sample_data) == sample_solution


@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 29)], ids=idfn)
def test_part2(sample_data, sample_solution) -> None:
    assert solve2(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":

    #  Run the test examples with icecream debug-trace turned on
    ic.disable()
    ex = pytest.main([__file__, "--capture=tee-sys", "-v"])
    if ex != pytest.ExitCode.OK and ex != pytest.ExitCode.NO_TESTS_COLLECTED:
        print(f"tests FAILED ({ex})")
        sys.exit(1)
    else:
        print("tests PASSED")

    #  Actual input data generally has more iterations, turn off log
    ic.disable()
    my_input = Path("input.txt").read_text()
    result = solve1(my_input)
    print("Part1:", result)
    result = solve2(my_input)
    print("Part2:", result)
