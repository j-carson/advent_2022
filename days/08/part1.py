import sys
from itertools import count
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

EXAMPLE = """30373
25512
65332
33549
35390
"""


# --> Puzzle solution


def parser(input_data):
    return np.array([[int(ch) for ch in line] for line in input_data.splitlines()])


def vis_check(data, vis_counter):
    nrows, ncols = data.shape

    for i, row in enumerate(data):
        if i == 0 or i == nrows - 1:
            continue

        # walk rows from the left
        current = row[0]
        for j, col in enumerate(row[1:], start=1):
            if col > current:
                vis_counter[i, j] = 1
            current = max(current, col)

        # walk row from the right
        right_row = list(reversed(row))
        current = right_row[0]
        for j, col in zip(count(ncols - 2, step=-1), right_row[1:]):
            if col > current:
                vis_counter[i, j] = 1
            current = max(current, col)


def solve(input_data):
    data = parser(input_data)

    ic("Starting rows")
    vis_counter = np.zeros_like(data)
    vis_check(data, vis_counter)

    ic("Starting columns")
    vis_counter = np.rot90(vis_counter)
    vis_check(np.rot90(data), vis_counter)

    vis_counter[:, 0] = 1
    vis_counter[:, -1] = 1
    vis_counter[0, :] = 1
    vis_counter[-1, :] = 1

    ic(data)
    ic(vis_counter)

    return vis_counter.sum()


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 21)], ids=idfn)
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
