from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from icecream import ic


def solve(input_data):
    return 0


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [("first_example", 0)])
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


if __name__ == "__main__":
    with Path("debug.log").open("w") as debug_log:

        def debug_logger(stuff):
            debug_log.write(stuff)
            debug_log.write("\n")

        ic.configureOutput(outputFunction=debug_logger)

        #  Run the test examples with icecream debug-trace turned on
        ic.enable()
        ex = pytest.main(["wip.py"])
        if ex != pytest.ExitCode.OK and ex != pytest.ExitCode.NO_TESTS_COLLECTED:
            print(f"tests FAILED ({ex})")
            exit(1)
        else:
            print("tests PASSED")

        #  Actual input data generally as more iterations, turn off log
        ic.disable()
        my_input = Path("input.txt").read_text()
        result = solve(my_input)
        print(result)
