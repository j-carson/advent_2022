import sys
from pathlib import Path

import pytest
from icecream import ic


# --> Puzzle solution


class Monkey:
    __slots__ = [
        "idn",
        "items",
        "op",
        "test_val",
        "true_friend",
        "false_friend",
        "activity",
    ]

    def __init__(self, idn):
        self.idn = idn
        self.activity = 0

    def __str__(self):
        return f"Monkey({self.idn}, items={self.items}, test_val={self.test_val}"

    def inspect_and_throw(self):
        starting_items = self.items
        self.items = []

        for item in starting_items:
            worry_level = self.op(item) // 3
            if worry_level % self.test_val:
                # Not evenly divisible
                self.false_friend.items.append(worry_level)
            else:
                self.true_friend.items.append(worry_level)

            self.activity += 1

    def setup(self, input_block, other_monkeys):
        (
            monkey_name,
            starting_items,
            operation,
            test,
            true_,
            false_,
        ) = input_block.splitlines()
        ic(monkey_name)

        assert monkey_name.strip() == f"Monkey {self.idn}:"

        starting_items = eval(starting_items.split(":")[1] + ",")
        ic(starting_items)
        self.items = list(starting_items)

        operation = operation.split(":")[1].replace("new", "old").replace("=", ":")
        self.op = eval(f"lambda {operation}")

        self.test_val = int(test.split()[-1])
        self.true_friend = other_monkeys[int(true_.split()[-1])]
        self.false_friend = other_monkeys[int(false_.split()[-1])]

        ic(self)


def play_round(monkeys):
    for monkey in monkeys:
        monkey.inspect_and_throw()


def solve(input_data):
    blocks = input_data.split("\n\n")
    n_monkeys = len(blocks)
    monkeys = [Monkey(i) for i in range(n_monkeys)]

    for monkey, data in zip(monkeys, blocks):
        monkey.setup(data, monkeys)

    for _ in range(20):
        play_round(monkeys)

    activity = sorted(monkey.activity for monkey in monkeys)
    return activity[-1] * activity[-2]


# --> Test driven development helpers

EXAMPLE = """Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3

Monkey 1:
  Starting items: 54, 65, 75, 74
  Operation: new = old + 6
  Test: divisible by 19
    If true: throw to monkey 2
    If false: throw to monkey 0

Monkey 2:
  Starting items: 79, 60, 97
  Operation: new = old * old
  Test: divisible by 13
    If true: throw to monkey 1
    If false: throw to monkey 3

Monkey 3:
  Starting items: 74
  Operation: new = old + 3
  Test: divisible by 17
    If true: throw to monkey 0
    If false: throw to monkey 1"""

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 10605)], ids=idfn)
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
