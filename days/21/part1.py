import sys
from collections import defaultdict
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


class Monkey:
    SOLVED_MONKEYS = {}
    DEPENDENT_MONKEYS = defaultdict(list)
    UPDATE_MONKEYS = []

    __slots__ = ["name", "value", "code", "depcount"]

    def __init__(self, line):
        name, code = line.split(":")
        self.name = name
        try:
            self.value = int(code)
            self.SOLVED_MONKEYS[self.name] = self.value
        except ValueError:
            self.value = None
            self.code = code
            monkey_1, op, monkey_2 = code.split()
            self.DEPENDENT_MONKEYS[monkey_1].append(self)
            self.DEPENDENT_MONKEYS[monkey_2].append(self)
            self.depcount = 2

    @classmethod
    def solve(cls):
        # go through all the dependent monkeys and update
        # depcount based on all the now-known constant-value monkeys
        for name in cls.SOLVED_MONKEYS.keys():
            for monkey in cls.DEPENDENT_MONKEYS[name]:
                monkey.depcount -= 1
                if monkey.depcount == 0:
                    cls.UPDATE_MONKEYS.append(monkey)

        while cls.UPDATE_MONKEYS:
            job = cls.UPDATE_MONKEYS.pop()

            monkey_1, op, monkey_2 = job.code.split()
            code = job.code.replace(
                monkey_1, str(cls.SOLVED_MONKEYS[monkey_1])
            ).replace(monkey_2, str(cls.SOLVED_MONKEYS[monkey_2]))
            job.value = eval(code)

            cls.SOLVED_MONKEYS[job.name] = job.value

            for monkey in cls.DEPENDENT_MONKEYS[job.name]:
                monkey.depcount -= 1
                if monkey.depcount == 0:
                    cls.UPDATE_MONKEYS.append(monkey)


def solve(input_data):
    for line in input_data.splitlines():
        Monkey(line)
    Monkey.solve()
    return Monkey.SOLVED_MONKEYS["root"]


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE = """root: pppw + sjmn
dbpl: 5
cczh: sllz + lgvd
zczc: 2
ptdq: humn - dvpt
dvpt: 3
lfqf: 4
humn: 5
ljgn: 2
sjmn: drzm * dbpl
sllz: 4
pppw: cczh / lfqf
lgvd: ljgn * ptdq
drzm: hmdt - zczc
hmdt: 32
"""

# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 152)], ids=idfn)
def test_samples(sample_data, sample_solution) -> None:
    assert solve(sample_data) == 152


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
