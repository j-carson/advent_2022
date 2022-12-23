import sys
from collections import defaultdict
from pathlib import Path
from typing import NamedTuple

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


# --> Puzzle solution


def parse(input_data):
    elf_positions = set()
    for x, row in enumerate(input_data.splitlines()):
        for y, ch in enumerate(row):
            if ch == "#":
                elf_positions.add(Position(x, y))
    ic(elf_positions)
    return elf_positions


def solve(input_data):
    elf_positions = parse(input_data)
    consider_order = ["N", "S", "W", "E"]
    move_list = {
        "N": ["N", "NE", "NW"],
        "S": ["S", "SE", "SW"],
        "E": ["E", "NE", "SE"],
        "W": ["W", "NW", "SW"],
    }
    all_sides = ["N", "S", "E", "W", "NE", "NW", "SE", "SW"]

    rounds = 10
    stable = False
    while not stable:
        ic(rounds)
        stable = True
        # key = dest, value = elf/elves proposing to move there
        proposed_moves = defaultdict(list)

        # -- first half of round ---
        for elf in elf_positions:
            neighbors = {side: elf.neighbor(side) for side in all_sides}
            is_filled = {side: (neighbors[side] in elf_positions) for side in all_sides}
            # make sure I got 8 unique neighbors
            assert len(set(neighbors.values())) == 8

            if any(is_filled.values()):
                stable = False
                for direction in consider_order:
                    check_list = [is_filled[side] for side in move_list[direction]]
                    if not any(check_list):
                        proposed_moves[elf.neighbor(direction)].append(elf)
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
        assert len(new_elf_positions) == len(elf_positions)
        elf_positions = new_elf_positions
        consider_order = consider_order[1:] + [consider_order[0]]
        ic(consider_order)

        rounds -= 1
        if rounds == 0:
            break

    min_x = 99999999999
    max_x = -99999999999
    min_y = 99999999999
    max_y = -99999999999

    for item in elf_positions:
        min_x = min(min_x, item.x)
        max_x = max(max_x, item.x)
        min_y = min(min_y, item.y)
        max_y = max(max_y, item.y)

    full_tiles = len(elf_positions)
    n_tiles = (max_x - min_x + 1) * (max_y - min_y + 1)
    return n_tiles - full_tiles


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


@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 110)], ids=idfn)
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
