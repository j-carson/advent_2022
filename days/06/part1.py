import sys
from collections import deque
from pathlib import Path

import pytest
from icecream import ic


# --> Puzzle solution


def solve(input_data):

    ic(input_data)
    window = deque(input_data[:4], maxlen=4)

    if len(set(window)) == 4:
        return 4

    for index, letter in enumerate(input_data[4:], start=5):
        window.append(letter)
        if len(set(window)) == 4:
            return index

    raise Exception("oops, fell off the end")


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    else:
        return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize(
    "sample_data,sample_solution",
    [
        ("mjqjpqmgbljsphdztnvjfqwrcgsmlb", 7),
        ("bvwbjplbgvbhsrlpgdmjqwftvncz", 5),
        ("nppdvjthqldpwncqszvftbrmjlhg", 6),
        ("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg", 10),
        ("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw", 11),
    ],
    ids=idfn,
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
