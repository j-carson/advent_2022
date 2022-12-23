from collections import defaultdict
from pathlib import Path

from sympy import Eq, Symbol, sympify
from sympy import solve as sympy_solve

# --> Puzzle solution


class Monkey:
    SOLVED_MONKEYS = {}
    DEPENDENT_MONKEYS = defaultdict(list)
    UPDATE_MONKEYS = []
    ALL_MONKEYS = {}

    __slots__ = ["name", "value", "code", "depcount"]

    def __init__(self, line):
        name, code = line.split(":")
        self.name = name
        try:
            self.value = int(code)
            self.code = code.strip()
            self.SOLVED_MONKEYS[self.name] = self.value
        except ValueError:
            self.value = None
            self.code = code.strip()
            monkey_1, op, monkey_2 = self.code.split()
            self.DEPENDENT_MONKEYS[monkey_1].append(self)
            self.DEPENDENT_MONKEYS[monkey_2].append(self)
            self.depcount = 2

        self.ALL_MONKEYS[self.name] = self

    def decode(self):
        if self.name in self.SOLVED_MONKEYS:
            return str(int(self.SOLVED_MONKEYS[self.name]))

        m1, op, m2 = self.code.split()
        if m1 != "humn":
            m1 = self.ALL_MONKEYS[m1].decode()
        else:
            m1 = "x"
        if m2 != "humn":
            m2 = self.ALL_MONKEYS[m2].decode()
        else:
            m2 = "x"

        return f"({m1} {op} {m2})"

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
        if not line.startswith("humn:"):
            Monkey(line)

    Monkey.solve()
    monkey_1, op, monkey_2 = Monkey.ALL_MONKEYS["root"].code.split()

    left_side = Monkey.ALL_MONKEYS[monkey_1].decode()
    right_side = Monkey.ALL_MONKEYS[monkey_2].decode()

    x = Symbol("x")
    result = Eq(sympify(left_side), sympify(right_side))
    answer = sympy_solve(result, x)

    return answer[0]


# --> Setup and run

if __name__ == "__main__":

    my_input = Path("input.txt").read_text()
    answer = solve(my_input)
    print(answer)
