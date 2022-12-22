import sys
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


class Item:
    __slots__ = ["fwd", "back", "value"]

    def __init__(self, value):
        self.fwd = None
        self.back = None
        self.value = value

    def extract(self):
        self.back.fwd = self.fwd
        self.fwd.back = self.back


class Cycler:
    __slots__ = ["items", "zero", "size"]

    def __init__(self, numbers):
        self.items = [Item(num) for num in numbers]

        for item, fwd in zip(self.items, self.items[1:]):
            item.fwd = fwd
            fwd.back = item
            if item.value == 0:
                self.zero = item

        self.items[-1].fwd = self.items[0]
        self.items[0].back = self.items[-1]

        if self.items[-1].value == 0:
            self.zero = self.items[-1]

        self.size = len(self.items)
        self.debug()

    def debug(self):
        start = ptr = self.items[0]
        data = []
        for i in range(self.size):
            data.append(ptr.value)
            ptr = ptr.fwd
        ic(data)
        assert start is ptr

    def mix(self):
        for item in self.items:

            if item.value < 0:
                spaces = -item.value
                next_ = item.back
                item.extract()
                for _ in range(spaces - 1):
                    next_ = next_.back
                prev = next_.back

                item.fwd = next_
                item.back = prev

                next_.back = item
                prev.fwd = item
                self.debug()

            elif item.value > 0:
                spaces = item.value
                prev = item.fwd
                item.extract()
                for _ in range(spaces - 1):
                    prev = prev.fwd
                next_ = prev.fwd

                item.fwd = next_
                item.back = prev

                next_.back = item
                prev.fwd = item
                self.debug()

    def score(self):
        result = []
        item = self.zero
        for n in range(3):
            for j in range(1000):
                item = item.fwd
            result.append(item.value)
        ic(result)
        return sum(result)


def parse(input_data):
    for line in input_data.splitlines():
        yield int(line)


def solve(input_data):
    numbers = parse(input_data)
    game = Cycler(numbers)
    game.mix()
    return game.score()


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
EXAMPLE = """1
2
-3
3
-2
0
4"""


@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 3)], ids=idfn)
def test_samples(sample_data, sample_solution) -> None:
    assert sample_solution == solve(sample_data)


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
