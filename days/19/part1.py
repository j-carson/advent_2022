import sys
from pathlib import Path

import pytest
from icecream import ic
from solution import *

DEADLINE = 24


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE = """Blueprint 1: Each ore robot costs 4 ore. Each clay robot costs 2 ore. Each obsidian robot costs 3 ore and 14 clay. Each geode robot costs 2 ore and 7 obsidian.
Blueprint 2: Each ore robot costs 2 ore. Each clay robot costs 3 ore. Each obsidian robot costs 3 ore and 8 clay. Each geode robot costs 3 ore and 12 obsidian."""  # noqa: E501


def test_detailed_example():
    line = EXAMPLE.splitlines()[0]
    bp = Blueprint.from_input_text(line, 24, 1)

    # can buy clay-bot at minute 3
    bp.run_one_event("clay")

    assert bp.ticks == 3
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 0
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 1

    # buy clay-bot at minute 5
    bp.run_one_event("clay")

    assert bp.ticks == 5
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 2
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 2

    # buy clay-bot at minute 7
    bp.run_one_event("clay")

    assert bp.ticks == 7
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 6
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 3

    # buy obsidian-bot at minute 11
    bp.run_one_event("obsidian")

    assert bp.ticks == 11
    assert bp.purse["ore"] == 2
    assert bp.purse["clay"] == 4
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 3
    assert bp.robots["obsidian"].quantity == 1

    # buy clay-bot at minute 12
    bp.run_one_event("clay")

    assert bp.ticks == 12
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 7
    assert bp.purse["obsidian"] == 1
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 1

    # buy obsidian bot at minute 15
    bp.run_one_event("obsidian")

    assert bp.ticks == 15
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 5
    assert bp.purse["obsidian"] == 4
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 2

    # buy geode bot at minute 18
    bp.run_one_event("geode")

    assert bp.ticks == 18
    assert bp.purse["ore"] == 2
    assert bp.purse["clay"] == 17
    assert bp.purse["obsidian"] == 3
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 2
    assert bp.robots["geode"].quantity == 1

    # buy geode bot at minute 21
    bp.run_one_event("geode")

    assert bp.ticks == 21
    assert bp.purse["ore"] == 3
    assert bp.purse["clay"] == 29
    assert bp.purse["obsidian"] == 2
    assert bp.purse["geode"] == 3
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 2
    assert bp.robots["geode"].quantity == 2

    # run out the clock
    bp.run_one_event("run")
    assert bp.purse["ore"] == 6
    assert bp.purse["clay"] == 41
    assert bp.purse["obsidian"] == 8
    assert bp.purse["geode"] == 9


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 33)], ids=idfn)
def test_full_example(sample_data, sample_solution) -> None:
    assert solve(sample_data, part=1) == sample_solution


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

    #  Actual input data generally has more iterations, turn off log
    my_input = Path("input.txt").read_text()
    result = solve(my_input, part=1)
    print(result)
