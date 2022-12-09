import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest
from icecream import ic

EXAMPLE = """R 4
U 4
L 3
D 1
R 4
D 1
L 5
R 2"""

LARGER_EXAMPLE = """R 5
U 8
L 8
D 3
R 17
D 10
L 25
U 20
"""

# --> Puzzle solution

TOO_FAR = 2


@dataclass
class Position:
    row: int = 0
    col: int = 0

    def log(self, trail):
        trail[(self.row, self.col)] = 1

    def touches(self, other):
        return (abs(self.col - other.col) <= 1) and (abs(self.row - other.row) <= 1)


class Rope:
    def __init__(self):
        self.rope = [Position() for _ in range(10)]
        self.trail = {}
        self.log()

    def log(self):
        self.rope[-1].log(self.trail)

    def move_tail(self):
        for leader, follower in zip(self.rope, self.rope[1:]):
            if leader.touches(follower):
                continue

            follower.col += np.sign(leader.col - follower.col)
            follower.row += np.sign(leader.row - follower.row)

        self.log()

    @property
    def visit_count(self):
        return len(self.trail)

    def L(self, count):
        for i in range(count):
            self.rope[0].col -= 1
            self.move_tail()

    def R(self, count):
        for i in range(count):
            self.rope[0].col += 1
            self.move_tail()

    def U(self, count):
        for i in range(count):
            self.rope[0].row += 1
            self.move_tail()

    def D(self, count):
        for i in range(count):
            self.rope[0].row -= 1
            self.move_tail()


def solve(input_data):
    rope = Rope()
    for line in input_data.splitlines():
        point_dir, dist = line.split()
        ic(line)
        go_func = rope.__getattribute__(point_dir)
        go_func(int(dist))

    return rope.visit_count


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize(
    "sample_data,sample_solution", [(EXAMPLE, 1), (LARGER_EXAMPLE, 36)], ids=idfn
)
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
