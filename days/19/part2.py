import sys
from pathlib import Path

import pytest
from icecream import ic
from solution import *

DEADLINE = 32


# --> Test driven development helpers

EXAMPLE = """Blueprint 1: Each ore robot costs 4 ore. Each clay robot costs 2 ore. Each obsidian robot costs 3 ore and 14 clay. Each geode robot costs 2 ore and 7 obsidian.
Blueprint 2: Each ore robot costs 2 ore. Each clay robot costs 3 ore. Each obsidian robot costs 3 ore and 8 clay. Each geode robot costs 3 ore and 12 obsidian."""  # noqa: E501


@pytest.mark.parametrize(
    "blueprint,expected_score",
    [(EXAMPLE.splitlines()[0], 56), (EXAMPLE.splitlines()[1], 62)],
)
def test_one_blueprint(blueprint, expected_score):
    game = Blueprint.from_input_text(blueprint, DEADLINE, 2)
    score = solve_blueprint(game)
    assert score == expected_score


# --> Setup and run

if __name__ == "__main__":

    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys", "--pdb"])
    if ex != pytest.ExitCode.OK and ex != pytest.ExitCode.NO_TESTS_COLLECTED:
        print(f"tests FAILED ({ex})")
        sys.exit(1)
    else:
        print("tests PASSED")

    my_input = Path("input.txt").read_text()
    result = solve(my_input, 2)
    print(result)
