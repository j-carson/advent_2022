import sys
from collections import namedtuple
from itertools import combinations
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

DEADLINE = 26
ExplorerState = namedtuple("ExplorerState", "node,travel_time")


class Valve:
    VALVES = {}

    def __init__(self, name, rate):
        self.name = name
        self.rate = rate
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

    return valve_directory


def solve_subpart(states, valves_remaining, time_remaining):

    valves = Valve.VALVES
    best_score = 0
    person, elephant = states

    if person.travel_time != 0 and elephant.travel_time != 0:
        assert person.travel_time > 0
        assert elephant.travel_time > 0
        tick = min(person.travel_time, elephant.travel_time)

        time_remaining -= tick
        assert time_remaining >= 0

        person, elephant = ExplorerState(
            person.node, person.travel_time - tick
        ), ExplorerState(elephant.node, elephant.travel_time - tick)

    # no more valves to turn on or no more time
    if (len(valves_remaining) == 0) or (time_remaining == 0):
        return 0

    if person.travel_time == 0:
        position = valves[person.node]
        other = elephant

        for dest in valves_remaining:
            cost = position.distances[dest] + 1
            if cost < time_remaining:
                subscore = valves[dest].rate * (time_remaining - cost)
                to_explore = [v for v in valves_remaining if v != dest]

                score = subscore + solve_subpart(
                    [ExplorerState(dest, cost), other], to_explore, time_remaining
                )
                best_score = max(best_score, score)

    if elephant.travel_time == 0:
        position = valves[elephant.node]
        other = person

        for dest in valves_remaining:
            cost = position.distances[dest] + 1
            if cost < time_remaining:
                subscore = valves[dest].rate * (time_remaining - cost)
                to_explore = [v for v in valves_remaining if v != dest]

                score = subscore + solve_subpart(
                    [other, ExplorerState(dest, cost)], to_explore, time_remaining
                )
                best_score = max(best_score, score)

    return best_score


def solve(input_data):
    valves = parser(input_data)
    all_points = list(valves.keys())
    worth_turning_on = [key for key in all_points if valves[key].rate > 0]

    best_score = 0
    for dest_1, dest_2 in combinations(worth_turning_on, 2):
        cost_1 = valves["AA"].distances[dest_1] + 1
        cost_2 = valves["AA"].distances[dest_2] + 1

        if cost_1 >= DEADLINE or cost_2 >= DEADLINE:
            continue

        reward_1 = valves[dest_1].rate * (DEADLINE - cost_1)
        reward_2 = valves[dest_2].rate * (DEADLINE - cost_2)

        remaining = [w for w in worth_turning_on if w not in (dest_1, dest_2)]
        states = [ExplorerState(dest_1, cost_1), ExplorerState(dest_2, cost_2)]
        best_score = max(
            best_score, reward_1 + reward_2 + solve_subpart(states, remaining, DEADLINE)
        )

    return best_score


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
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 1707)], ids=idfn)
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
