import sys
from collections import defaultdict
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

SNAFU2DECIMAL_DIGITS = {
    "=": -2,
    "-": -1,
    "0": 0,
    "1": 1,
    "2": 2,
}

DECIMAL2SNAFU_DIGITS = {
    -2: "=",
    -1: "-",
    0: "0",
    1: "1",
    2: "2",
}

DECIMAL2SNAFU_EXAMPLES = (
    (0, "0"),
    (1, "1"),
    (2, "2"),
    (3, "1="),
    (4, "1-"),
    (5, "10"),
    (6, "11"),
    (7, "12"),
    (8, "2="),
    (9, "2-"),
    (10, "20"),
    (15, "1=0"),
    (20, "1-0"),
    (2022, "1=11-2"),
    (12345, "1-0---0"),
    (314159265, "1121-1110-1=0"),
)

SNAFU2DECIMAL_EXAMPLES = (
    ("1=-0-2", 1747),
    ("12111", 906),
    ("2=0=", 198),
    ("2=-01", 976),
    ("21", 11),
    ("2=01", 201),
    ("111", 31),
    ("20012", 1257),
    ("112", 32),
    ("1=-1=", 353),
    ("1-12", 107),
    ("12", 7),
    ("1=", 3),
    ("122", 37),
)

MAX_PLACES = 20
POWERS_OF_FIVE = {i: 5**i for i in range(MAX_PLACES)}


class SNAFU:
    __slots__ = ["decimal", "snafu"]

    def __init__(self, snafu):
        self.snafu = snafu
        value = 0
        for i, ch in enumerate(reversed(snafu), start=0):
            value += SNAFU2DECIMAL_DIGITS[ch] * POWERS_OF_FIVE[i]
        self.decimal = value

    @staticmethod
    def from_decimal(value):
        if value == 0:
            return SNAFU("0")

        places = defaultdict(int)
        remainder = value
        for i in range(MAX_PLACES - 1, -1, -1):
            if remainder >= POWERS_OF_FIVE[i]:
                places[i] = remainder // POWERS_OF_FIVE[i]
                remainder -= places[i] * POWERS_OF_FIVE[i]
                assert remainder >= 0

        assert remainder == 0
        done = False
        while not done:
            keys = list(places.keys())
            for key in keys:
                if places[key] > 2:
                    places[key + 1] += 1
                    places[key] -= 5
                    break
            else:
                done = True

        n_places = max(places.keys())
        snafu = "".join(
            DECIMAL2SNAFU_DIGITS[places[i]] for i in range(n_places, -1, -1)
        )
        result = SNAFU(snafu)
        assert result.decimal == value
        return result


def solve(input_data):
    total = 0
    for snafu in input_data.splitlines():
        total += SNAFU(snafu.strip()).decimal

    result = SNAFU.from_decimal(total)
    return result.snafu


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("decimal,snafu", DECIMAL2SNAFU_EXAMPLES)
def test_samples(decimal, snafu) -> None:
    assert SNAFU(snafu).decimal == decimal
    assert SNAFU.from_decimal(decimal).snafu == snafu


@pytest.mark.parametrize("snafu,decimal", SNAFU2DECIMAL_EXAMPLES)
def test_samples2(decimal, snafu) -> None:
    assert SNAFU.from_decimal(decimal).snafu == snafu
    assert SNAFU(snafu).decimal == decimal


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
