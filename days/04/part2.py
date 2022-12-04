import re
import sys
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

EXAMPLE = """2-4,6-8
2-3,4-5
5-7,7-9
2-8,3-7
6-6,4-6
2-6,4-8"""


def parse(input_data):
    for line in input_data.splitlines():
        numbers = [int(d) for d in re.findall(r"\d+", line)]
        yield numbers[:2], numbers[2:]


def overlap(b1, b2):
    return (b2[0] <= b1[0] <= b2[1]) or (b1[0] <= b2[0] <= b1[1])


def solve(input_data):
    return sum((overlap(bounds1, bounds2) for bounds1, bounds2 in parse(input_data)))


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    else:
        return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 4)], ids=idfn)
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
