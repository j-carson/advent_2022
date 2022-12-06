import sys
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

object_scores = {"Rock": 1, "Paper": 2, "Scissors": 3}

outcome_scores = {"lost": 0, "draw": 3, "won": 6}

opponent_key = {"A": "Rock", "B": "Paper", "C": "Scissors"}

my_key = {"X": "Rock", "Y": "Paper", "Z": "Scissors"}

game_results = {
    # opponent, self
    ("Rock", "Rock"): "draw",
    ("Rock", "Scissors"): "lost",
    ("Rock", "Paper"): "won",
    ("Scissors", "Rock"): "won",
    ("Scissors", "Scissors"): "draw",
    ("Scissors", "Paper"): "lost",
    ("Paper", "Rock"): "lost",
    ("Paper", "Scissors"): "won",
    ("Paper", "Paper"): "draw",
}


def solve(input_data):
    score = 0
    for line in input_data.splitlines():
        opp, me = line.split()
        score += object_scores[my_key[me]]
        score += outcome_scores[game_results[(opponent_key[opp], my_key[me])]]
    return score


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
            """A Y
B X
C Z""",
            15,
        )
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
