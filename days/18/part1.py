import sys
from collections import namedtuple
from pathlib import Path

import pytest
from icecream import ic

Point3D = namedtuple("Point3D", "x,y,z")

# --> Puzzle solution


def parse(input_data):
    result = []
    for line in input_data.splitlines():
        nums = [int(n) for n in line.split(",")]
        result.append(Point3D(*nums))
    return set(result)


def neighbors(point):
    x, y, z = point
    return [
        Point3D(x - 1, y, z),
        Point3D(x + 1, y, z),
        Point3D(x, y - 1, z),
        Point3D(x, y + 1, z),
        Point3D(x, y, z - 1),
        Point3D(x, y, z + 1),
    ]


def solve(input_data):
    points = parse(input_data)
    exposed = 0
    for point in points:
        for neighbor in neighbors(point):
            if neighbor not in points:
                exposed += 1
    return exposed


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE_1 = """1,1,1\n2,1,1"""
EXAMPLE_2 = """2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5"""


# Test any examples given in the problem
@pytest.mark.parametrize(
    "sample_data,sample_solution", [(EXAMPLE_1, 10), (EXAMPLE_2, 64)], ids=idfn
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
