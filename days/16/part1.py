import sys
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

DEADLINE = 30


class Valve:
    VALVES = {}

    def __init__(self, name, rate):
        self.name = name
        self.rate = rate
        self.open = False
        self.VALVES[self.name] = self

    def get_distances(self, connections):
        self.distances = {}

        # it costs 0 to move from self to self
        self.distances[self.name] = 0

        for child in connections[self.name]:
            self.distances[child] = 1

        can_reach = connections[self.name]
        cost = 2
        while len(self.distances) < len(connections):
            reached = []
            for key in can_reach:
                for one_more_hop in connections[key]:
                    if one_more_hop not in self.distances:
                        self.distances[one_more_hop] = cost
                    reached.append(one_more_hop)

            cost += 1
            can_reach = reached

    @classmethod
    def debug_map(self):
        for name, valve in self.VALVES.items():
            if valve.rate > 0:
                ic(
                    valve.name,
                    valve.rate,
                    [
                        (k, v)
                        for k, v in valve.distances.items()
                        if self.VALVES[k].rate > 0
                    ],
                )


def parser(input_data):
    valve_directory = {}
    connections_directory = {}

    for line in input_data.splitlines():
        specs, _ = line.split(";")
        words = specs.split()
        name = words[1]
        rate = int(words[-1].split("=")[1])
        valve_directory[name] = Valve(name, rate)

    for line in input_data.splitlines():
        split_attempt1 = line.split("valves")
        if len(split_attempt1) == 2:
            specs, tunnels = split_attempt1
        else:
            specs, tunnels = line.split("valve")

        words = specs.split()
        name = words[1]

        child_valves = tunnels.split(",")
        connections_directory[name] = [c.strip() for c in child_valves]

    for valve in valve_directory.values():
        valve.get_distances(connections_directory)

    Valve.debug_map()

    return valve_directory


def solve_subpart(start, valves_remaining, time_remaining):

    if len(valves_remaining) == 0:
        return 0

    valves = Valve.VALVES
    position = valves[start]
    scores = {}

    for candidate in valves_remaining:
        cost = position.distances[candidate] + 1
        if cost <= time_remaining:
            scores[candidate] = valves[candidate].rate * (
                time_remaining - cost
            ) + solve_subpart(
                candidate,
                [v for v in valves_remaining if v != candidate],
                time_remaining - cost,
            )
    if scores:
        ic(scores)
        return max(scores.values())
    return 0


def solve(input_data):
    valves = parser(input_data)
    all_points = list(valves.keys())
    worth_turning_on = [key for key in all_points if valves[key].rate > 0]

    return solve_subpart("AA", worth_turning_on, DEADLINE)


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE = """Valve AA has flow rate=0; tunnels lead to valves DD, II, BB
Valve BB has flow rate=13; tunnels lead to valves CC, AA
Valve CC has flow rate=2; tunnels lead to valves DD, BB
Valve DD has flow rate=20; tunnels lead to valves CC, AA, EE
Valve EE has flow rate=3; tunnels lead to valves FF, DD
Valve FF has flow rate=0; tunnels lead to valves EE, GG
Valve GG has flow rate=0; tunnels lead to valves FF, HH
Valve HH has flow rate=22; tunnel leads to valve GG
Valve II has flow rate=0; tunnels lead to valves AA, JJ
Valve JJ has flow rate=21; tunnel leads to valve II"""


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 1651)], ids=idfn)
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
