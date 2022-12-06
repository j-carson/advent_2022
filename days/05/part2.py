import re
import sys
from collections import namedtuple
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


Instruction = namedtuple("Instruction", "move_qty,source,dest")


def crates(line):
    ic(line)
    while line:
        yield (line[:4]).strip()
        line = line[4:]


def parser(input_text):
    config, instructions = input_text.split("\n\n")

    config_lines = list(reversed(config.splitlines()))
    nstacks = int(config_lines[0].split()[-1])
    stacks = [[] for _ in range(nstacks)]

    for line in config_lines[1:]:
        for i, crate in enumerate(crates(line)):
            if crate:
                stacks[i].append(crate[1])

    ic(stacks)

    todo_list = [
        Instruction(*(int(num) for num in re.findall(r"\d+", line)))
        for line in instructions.splitlines()
    ]
    ic(todo_list)

    return stacks, todo_list


def solve(input_data):
    stacks, todo_list = parser(input_data)
    for item in todo_list:
        source = stacks[item.source - 1]
        dest = stacks[item.dest - 1]

        removed, remaining = source[-item.move_qty :], source[: -item.move_qty]
        stacks[item.source - 1] = remaining
        dest.extend(removed)
        ic(stacks)
    return "".join((s[-1] for s in stacks))


# --> Test driven development helpers

EXAMPLE = """    [D]
[N] [C]
[Z] [M] [P]
 1   2   3

move 1 from 2 to 1
move 3 from 1 to 3
move 2 from 2 to 1
move 1 from 1 to 2"""

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, "MCD")], ids=idfn)
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
