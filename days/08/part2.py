import sys
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


def look_out(height, view):
    score = 0
    for tree in view:
        score += 1
        if tree >= height:
            break
    return score


def solve(input_text):

    data = parser(input_text)
    nrows, ncols = data.shape

    left_scores = np.zeros_like(data)
    right_scores = np.zeros_like(data)
    up_scores = np.zeros_like(data)
    down_scores = np.zeros_like(data)

    for i in range(nrows):
        for j in range(ncols):
            data_value = data[i, j]
            left_scores[i, j] = look_out(data_value, reversed(data[i, :j]))
            right_scores[i, j] = look_out(data_value, data[i, j + 1 :])
            up_scores[i, j] = look_out(data_value, reversed(data[:i, j]))
            down_scores[i, j] = look_out(data_value, data[i + 1 :, j])

    ic(left_scores)
    ic(right_scores)
    ic(up_scores)
    ic(down_scores)

    ic(left_scores * right_scores * up_scores * down_scores)

    return np.max(left_scores * right_scores * up_scores * down_scores)


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 8)], ids=idfn)
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
