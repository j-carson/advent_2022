import sys
from collections import deque
from pathlib import Path
from typing import Literal, NamedTuple

import numpy as np
import pytest
from icecream import ic

# --> Puzzle solution
# constants

Move = Literal["up", "down", "left", "right", "wait"]
MOVES = ["up", "down", "left", "right", "wait"]

# global variables
OPEN_SQUARES = None
N_STATES = -1
GRID_ROWS = None
GRID_COLS = None


class Coords(NamedTuple):
    x: int
    y: int
    t: int

    def go(self, step_dir: Move):
        match step_dir:
            case "wait":
                return Coords(self.x, self.y, (self.t + 1) % N_STATES)
            case "left":
                return Coords(self.x - 1, self.y, (self.t + 1) % N_STATES)
            case "right":
                return Coords(self.x + 1, self.y, (self.t + 1) % N_STATES)
            case "up":
                return Coords(self.x, self.y - 1, (self.t + 1) % N_STATES)
            case "down":
                return Coords(self.x, self.y + 1, (self.t + 1) % N_STATES)
        raise Exception(f"oops {step_dir}")


def make_maps(input_data):
    global OPEN_SQUARES
    global N_STATES
    global GRID_ROWS, GRID_COLS

    def make_bits(grid, key):
        xs, ys = np.where(grid == key)
        bits = np.zeros_like(grid, dtype=bool)
        for x, y in zip(xs, ys):
            bits[x, y] = True
        return bits

    lines = input_data.splitlines()
    grid = np.array([list(line) for line in lines], dtype=str)

    GRID_ROWS, GRID_COLS = grid.shape

    lefts = make_bits(grid, "<")[1 : GRID_ROWS - 1, 1 : GRID_COLS - 1]
    rights = make_bits(grid, ">")[1 : GRID_ROWS - 1, 1 : GRID_COLS - 1]
    ups = make_bits(grid, "^")[1 : GRID_ROWS - 1, 1 : GRID_COLS - 1]
    downs = make_bits(grid, "v")[1 : GRID_ROWS - 1, 1 : GRID_COLS - 1]
    walls = make_bits(grid, "#")

    states = []
    states.append(
        np.pad(lefts, 1) | np.pad(rights, 1) | np.pad(ups, 1) | np.pad(downs, 1) | walls
    )
    N_STATES = np.lcm(GRID_ROWS - 2, GRID_COLS - 2)
    check_shape = GRID_ROWS - 2, GRID_COLS - 2

    for _ in range(N_STATES - 1):
        lefts = np.hstack([lefts[:, 1:], (lefts[:, 0]).reshape(-1, 1)])
        rights = np.hstack([(rights[:, -1]).reshape(-1, 1), rights[:, 0:-1]])
        ups = np.vstack([ups[1:], ups[0]])
        downs = np.vstack(
            [
                downs[-1],
                downs[0:-1],
            ]
        )

        assert lefts.shape == check_shape
        assert rights.shape == check_shape
        assert ups.shape == check_shape
        assert downs.shape == check_shape

        answer = (
            np.pad(lefts, 1)
            | np.pad(rights, 1)
            | np.pad(ups, 1)
            | np.pad(downs, 1)
            | walls
        )
        assert answer.shape == grid.shape
        states.append(answer)

    # make sure we really are repeating from the beginning here
    lefts = np.hstack([lefts[:, 1:], (lefts[:, 0]).reshape(-1, 1)])
    rights = np.hstack([(rights[:, -1]).reshape(-1, 1), rights[:, 0:-1]])
    ups = np.vstack([ups[1:], ups[0]])
    downs = np.vstack(
        [
            downs[-1],
            downs[0:-1],
        ]
    )
    answer = (
        np.pad(lefts, 1) | np.pad(rights, 1) | np.pad(ups, 1) | np.pad(downs, 1) | walls
    )
    assert np.all(answer == states[0])

    # OK, now that we have all the maps debugged, let's put it in an efficient format
    OPEN_SQUARES = set()
    for time, grid in enumerate(states):
        xs, ys = np.where(grid == False)
        OPEN_SQUARES.update(Coords(x, y, time) for x, y in zip(xs, ys))


def search_map(start_pos, end_set):

    # Part1 : Go to from start to end at time = 0
    visited = {}

    # we took zero steps to get here
    visited[start_pos] = 0
    # bootstrapping
    work_list = deque()

    for move in MOVES:
        proposed_move = start_pos.go(move)
        if (proposed_move in OPEN_SQUARES) and (proposed_move not in visited):
            visited[proposed_move] = 1
            work_list.append(proposed_move)

    while work_list:
        job = work_list.popleft()
        for move in MOVES:
            proposed_move = job.go(move)
            if (proposed_move in OPEN_SQUARES) and (proposed_move not in visited):
                visited[proposed_move] = visited[job] + 1
                work_list.append(proposed_move)
                if proposed_move in end_set:
                    return visited[proposed_move], proposed_move

    raise Exception("oops never reached END_POS")


def search_path(which_part):

    start_pos = Coords(0, 1, 0)
    end_set = set()
    start_set = set()

    for time in range(N_STATES):
        end_set.add(Coords(GRID_ROWS - 1, GRID_COLS - 2, time))
        start_set.add(Coords(0, 1, time))

    # go from start to end
    trip_one, arrival = search_map(start_pos, end_set)
    if which_part == 1:
        return trip_one

    # go back from end to start
    trip_two, arrival = search_map(arrival, start_set)

    # go from start to end again
    trip_three, arrival = search_map(arrival, end_set)

    return trip_one + trip_two + trip_three


def solve(input_data, which_part):
    # initializes global variables
    make_maps(input_data)
    shortest_path = search_path(which_part)
    return shortest_path


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
EXAMPLE = """#.######
#>>.<^<#
#.<..<<#
#>v.><>#
#<^v^^>#
######.#"""


@pytest.mark.parametrize(
    "sample_data,test_part,sample_solution",
    [(EXAMPLE, 1, 18), (EXAMPLE, 2, 54)],
    ids=idfn,
)
def test_samples(sample_data, test_part, sample_solution) -> None:
    assert solve(sample_data, test_part) == sample_solution


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
    result = solve(my_input, 1)
    print("Part 1", result)

    result = solve(my_input, 2)
    print("Part 2", result)
