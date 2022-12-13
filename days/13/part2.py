import sys
from enum import Enum
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution


class FuzzyLogic(Enum):
    TRUE = 1
    FALSE = 2
    NOT_SURE_YET = 3


def listify(thing):
    if isinstance(thing, list):
        return thing
    return [thing]


def both_integers(item1, item2):
    return isinstance(item1, int) and isinstance(item2, int)


def both_lists(item1, item2):
    return isinstance(item1, list) and isinstance(item2, list)


def compare_terms(item1, item2):
    if both_integers(item1, item2):
        if item1 < item2:
            return FuzzyLogic.TRUE
        if item1 > item2:
            return FuzzyLogic.FALSE
        return FuzzyLogic.NOT_SURE_YET

    if both_lists(item1, item2):
        shorter = min(len(item1), len(item2))
        for left, right in zip(item1[:shorter], item2[:shorter]):
            result = compare_terms(left, right)
            if result != FuzzyLogic.NOT_SURE_YET:
                return result
        if len(item1) < len(item2):
            return FuzzyLogic.TRUE
        if len(item1) > len(item2):
            return FuzzyLogic.FALSE
        return FuzzyLogic.NOT_SURE_YET

    return compare_terms(listify(item1), listify(item2))


def parse(input_data):
    result = []
    for line in input_data.splitlines():
        if line:
            result.append(eval(line))
    result.extend([[[2]], [[6]]])
    return result


def swap(items, index1, index2):
    item1 = items[index1]
    item2 = items[index2]
    items[index1] = item2
    items[index2] = item1


def sort_list(items):
    size = len(items)
    done = False
    while not done:
        done = True
        for i in range(size - 1):
            if compare_terms(items[i], items[i + 1]) != FuzzyLogic.TRUE:
                swap(items, i, i + 1)
                done = False


def solve(input_data):
    all_the_packets = parse(input_data)
    sort_list(all_the_packets)
    index1 = all_the_packets.index([[2]]) + 1
    index2 = all_the_packets.index([[6]]) + 1
    return index1 * index2


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


SAMPLE = """[1,1,3,1,1]
[1,1,5,1,1]

[[1],[2,3,4]]
[[1],4]

[9]
[[8,7,6]]

[[4,4],4,4]
[[4,4],4,4,4]

[7,7,7,7]
[7,7,7]

[]
[3]

[[[]]]
[[]]

[1,[2,[3,[4,[5,6,7]]]],8,9]
[1,[2,[3,[4,[5,6,0]]]],8,9]"""


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(SAMPLE, 140)], ids=idfn)
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
