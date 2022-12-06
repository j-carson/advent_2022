import sys
from pathlib import Path

import pytest
from icecream import ic


# --> Puzzle solution


def parser(data):
    current = 0
    for line in data.splitlines():
        if not line:
            yield current
            current = 0
        else:
            current += int(line)
    if current:
        yield current


def solve(input_data):
    return max(parser(input_data))


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
        (
            """1000
2000
3000

4000

5000
6000

7000
8000
9000

10000""",
            24000,
        )
    ],
    ids=idfn,
)
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


# --> Setup and run

if __name__ == "__main__":

    # set up a debug log to hold icecream output
    with Path("debug.log").open("w") as debug_log:

        def debug_logger(stuff):
            debug_log.write(stuff)
            debug_log.write("\n")

        ic.configureOutput(outputFunction=debug_logger)

        #  Run the test examples with icecream debug-trace turned on
        ic.enable()
        ex = pytest.main([__file__, "-v", "--pdb"])
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
