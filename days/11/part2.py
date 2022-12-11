import sys
from pathlib import Path

import pytest
from icecream import ic


# --> Puzzle solution


def make_the_rounds(worry_level, monkey, rounds, product_of_primes):
    turn = 0
    while turn < rounds:
        my_level = monkey.idn
        worry_level = monkey.op(worry_level) % product_of_primes
        monkey.activity += 1

        test_result = (worry_level % monkey.test_val) == 0
        if test_result:
            monkey = monkey.true_friend
        else:
            monkey = monkey.false_friend

        if monkey.idn < my_level:
            turn += 1


class Monkey:
    __slots__ = [
        "idn",
        "op",
        "test_val",
        "true_friend",
        "false_friend",
        "activity",
    ]

    def __init__(self, idn):
        self.idn = idn
        self.activity = 0

    def setup(self, input_block, other_monkeys) -> list[int]:
        (
            monkey_name,
            starting_items,
            operation,
            test,
            true_,
            false_,
        ) = input_block.splitlines()
        assert monkey_name.strip() == f"Monkey {self.idn}:"

        operation = operation.split(":")[1].replace("new", "old").replace("=", ":")
        self.op = eval(f"lambda {operation}")

        self.test_val = int(test.split()[-1])
        self.true_friend = other_monkeys[int(true_.split()[-1])]
        self.false_friend = other_monkeys[int(false_.split()[-1])]

        starting_items = eval(starting_items.split(":")[1] + ",")
        ic(starting_items)
        return list(starting_items)


def solve(input_data, nrounds):
    blocks = input_data.split("\n\n")
    n_monkeys = len(blocks)
    all_monkeys = [Monkey(i) for i in range(n_monkeys)]
    items = {}

    product_of_primes = 1
    for monkey, data in zip(all_monkeys, blocks):
        items[monkey] = monkey.setup(data, all_monkeys)
        product_of_primes *= monkey.test_val

    for monkey, todo_list in items.items():
        for worry in todo_list:
            make_the_rounds(worry, monkey, nrounds, product_of_primes)

    ic([monkey.activity for monkey in all_monkeys])
    activity = sorted(monkey.activity for monkey in all_monkeys)
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
@pytest.mark.parametrize(
    "sample_data,n_rounds,sample_solution",
    [(EXAMPLE, 20, 103 * 99), (EXAMPLE, 1000, 5204 * 5192)],
    ids=idfn,
)
def test_samples(sample_data, n_rounds, sample_solution) -> None:
    assert solve(sample_data, n_rounds) == sample_solution


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
    result = solve(my_input, 10_000)
    print(result)
