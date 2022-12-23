import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

import numpy as np
import pytest
from icecream import ic


class Position(NamedTuple):
    x: int
    y: int

    def neighbor(self, lookdir):
        offsets = {
            "N": Position(-1, 0),
            "S": Position(1, 0),
            "E": Position(0, 1),
            "W": Position(0, -1),
            "NE": Position(-1, 1),
            "NW": Position(-1, -1),
            "SE": Position(1, 1),
            "SW": Position(1, -1),
        }

        return Position(self.x + offsets[lookdir].x, self.y + offsets[lookdir].y)

    def is_in(self, pos_set):
        return self in pos_set


# --> Puzzle solution


class Puzzle:
    __slots__ = ["elf_positions", "rounds"]

    BLOCKERS = {
        "N": np.array([[1, 1, 1], [0, 0, 0], [0, 0, 0]], dtype=bool),
        "S": np.array([[0, 0, 0], [0, 0, 0], [1, 1, 1]], dtype=bool),
        "E": np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]], dtype=bool),
        "W": np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0]], dtype=bool),
    }

    def __init__(self, elf_positions):
        self.elf_positions = elf_positions
        self.rounds = 0

    @classmethod
    def parse(cls, input_data):
        elf_positions = set()
        for x, row in enumerate(input_data.splitlines()):
            for y, ch in enumerate(row):
                if ch == "#":
                    elf_positions.add(Position(x, y))
        return Puzzle(elf_positions)

    def neighbors(self, elf):
        positions = self.elf_positions
        neighbor = elf.neighbor
        return np.array(
            [
                [
                    neighbor("NW").is_in(positions),
                    neighbor("N").is_in(positions),
                    neighbor("NE").is_in(positions),
                ],
                [
                    neighbor("W").is_in(positions),
                    False,
                    elf.neighbor("E").is_in(positions),
                ],
                [
                    neighbor("SW").is_in(positions),
                    neighbor("S").is_in(positions),
                    neighbor("SE").is_in(positions),
                ],
            ],
            dtype=bool,
        )

    def blocked(self, neighbors, direction):
        return np.any(neighbors & self.BLOCKERS[direction])

    def solve(self):
        consider_order = ["N", "S", "W", "E"]
        self.rounds = 0
        stable = False

        while not stable:
            self.rounds += 1
            stable = True
            # key = destination, value = list of elves proposing to move there
            proposed_moves = defaultdict(list)

            # -- first half of round ---
            for elf in self.elf_positions:
                neighbors = self.neighbors(elf)
                if np.any(neighbors):
                    for direction in consider_order:
                        if not self.blocked(neighbors, direction):
                            stable = False
                            dest = elf.neighbor(direction)
                            proposed_moves[dest].append(elf)
                            break
                    else:
                        assert (
                            len(proposed_moves[elf]) == 0
                        ), "nobody should propose moving into an occupied space"
                        proposed_moves[elf].append(elf)
                else:
                    # this elf has space so proposes staying put
                    assert (
                        len(proposed_moves[elf]) == 0
                    ), "nobody should propose moving into an occupied space"
                    proposed_moves[elf].append(elf)

            # -- second half of round --
            new_elf_positions = set()
            for dest, proposers in proposed_moves.items():
                if len(proposers) == 1:
                    new_elf_positions.add(dest)
                else:
                    new_elf_positions.update(proposers)

            # -- reset for next round
            assert len(new_elf_positions) == len(self.elf_positions)
            self.elf_positions = new_elf_positions
            consider_order = consider_order[1:] + [consider_order[0]]


def solve(input_data):
    puzzle = Puzzle.parse(input_data)
    puzzle.solve()
    return puzzle.rounds


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
EXAMPLE = """....#..
..###.#
#...#.#
.#...##
#.###..
##.#.##
.#..#.."""


@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 20)], ids=idfn)
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == sample_solution


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
    ic.disable()
    my_input = Path("input.txt").read_text()
    result = solve(my_input)
    print(result)
