import sys
from collections import Counter
from itertools import count
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

PACKET_LENGTH = 14


def solve(input_data):

    start = input_data[:PACKET_LENGTH]
    window = Counter(start)
    the_rest = input_data[PACKET_LENGTH:]

    if max(window.values()) == 1:
        return PACKET_LENGTH

    for index, new_letter, old_letter in zip(
        count(PACKET_LENGTH + 1), the_rest, input_data
    ):
        window[new_letter] += 1
        window[old_letter] -= 1
        if max(window.values()) == 1:
            return index
    raise Exception("oops, fell off the end")


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize(
    "sample_data,sample_solution",
    [
        ("mjqjpqmgbljsphdztnvjfqwrcgsmlb", 19),
        ("bvwbjplbgvbhsrlpgdmjqwftvncz", 23),
        ("nppdvjthqldpwncqszvftbrmjlhg", 23),
        ("nznrnfrfntjfmvfwmzdfjlvtqnbhcprsg", 29),
        ("zcfzfwzzqfrljwzlrfnpqdbhtmscgvjw", 26),
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
