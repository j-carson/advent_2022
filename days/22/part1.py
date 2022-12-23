import re
import sys
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

STEPS = {
    "north": (-1, 0),  # up one row, over 0
    "south": (1, 0),
    "east": (0, 1),  # same row, over one column
    "west": (0, -1),
}

SCORES = {
    "north": 3,
    "south": 1,
    "east": 0,
    "west": 2,
}

TURN_RESULTS = {
    ("north", "L"): "west",
    ("north", "R"): "east",
    ("south", "L"): "east",
    ("south", "R"): "west",
    ("east", "L"): "north",
    ("east", "R"): "south",
    ("west", "L"): "south",
    ("west", "R"): "north",
}

# --> Puzzle solution


def grid_parser(grid_data):

    rows = grid_data.splitlines()
    grid_width = max(len(r) for r in rows)
    space_padding = " " * grid_width

    return np.array(
        [list((row + space_padding)[:grid_width]) for row in grid_data.splitlines()],
        dtype=str,
    )


def travel_parser(direction_data):
    return list(re.findall(r"\d+|L|R", direction_data))


def take_one_step(grid, position, direction):

    assert grid[position] == "."

    nrows, ncols = grid.shape
    step = STEPS[direction]

    proposed_location = (
        (position[0] + step[0]) % nrows,
        (position[1] + step[1]) % ncols,
    )

    # cross the void steps to wrap around
    while grid[proposed_location] == " ":
        proposed_location = (
            (proposed_location[0] + step[0]) % nrows,
            (proposed_location[1] + step[1]) % ncols,
        )

    # hit a wall, stay where we are
    if grid[proposed_location] == "#":
        return position

    # open space, we're good
    if grid[proposed_location] == ".":
        return proposed_location

    raise Exception("oops!")


def solve(input_data):
    grid_data, travel_data = input_data.split("\n\n")
    grid = grid_parser(grid_data)
    travel = travel_parser(travel_data)

    position = (0, np.where(grid[0] == ".")[0][0])
    direction = "east"
    ic("starting", position, direction, STEPS[direction])

    for step in travel:
        ic(step)
        if step.isdigit():
            for _ in range(int(step)):
                new_position = take_one_step(grid, position, direction)
                if new_position == position:
                    # location didn't update, must have hit a wall
                    break
                position = new_position
            ic("new position", new_position)
        else:
            # turn L or R
            direction = TURN_RESULTS[(direction, step)]
            ic("new direction", direction)

    ic(position)
    return (position[0] + 1) * 1000 + (position[1] + 1) * 4 + SCORES[direction]


# --> Test driven development helpers

EXAMPLE = """        ...#
        .#..
        #...
        ....
...#.......#
........#...
..#....#....
..........#.
        ...#....
        .....#..
        .#......
        ......#.

10R5L5R10L4R5L5
"""

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 6032)], ids=idfn)
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
