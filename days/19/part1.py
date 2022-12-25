import re
import sys
from collections import UserDict, deque
from pathlib import Path
from typing import Literal

import pytest
from icecream import ic

DEADLINE = 24


ROCKS = ["ore", "clay", "obsidian", "geode"]
Rock = Literal["ore", "clay", "obsidian", "geode"]

# the next event to execute could be
# "buy a robot that does (rock) or just
# "run out the clock"
EVENTS = [*ROCKS, "run"]
Event = Literal["ore", "clay", "obsidian", "geode", "run"]


def numbers(string):
    matches = re.findall(r"(\d+)", string)
    return [int(m) for m in matches]


class Assets(UserDict):
    """The cost to buy something, or the total in your purse"""

    def __init__(self, ore=0, clay=0, obsidian=0, geode=0):
        self.data = {"ore": ore, "clay": clay, "obsidian": obsidian, "geode": geode}

    def __repr__(self):
        return self.data.__repr__()


class Purse(Assets):
    """A purse is mutable assets so you can deposit
    your robot production or buy a robot"""

    def add(self, amount: Assets):
        for rock in self.keys():
            self[rock] += amount[rock]

    def remove(self, amount: Assets):
        for rock in self.keys():
            self[rock] -= amount[rock]
            if self[rock] < 0:
                raise ValueError(f"Not enough {rock} in {self} to spend {amount}!")

    def sufficient_funds(self, amount: Assets):
        return all(amount[rock] <= self[rock] for rock in self.keys())


class Robots:
    """A collection of robots producing one type of rock"""

    __slots__ = ["cost", "quantity"]

    def __init__(self, cost: Assets, quantity: int):
        self.cost = cost
        self.quantity = quantity

    def spawn(self, purse):
        purse.remove(self.cost)
        self.quantity += 1

    def copy(self):
        return Robots(cost=self.cost, quantity=self.quantity)

    def __repr__(self):
        return f"(Robots(cost={self.cost},quantity={self.quantity})"


class RobotOverlord(UserDict):
    """Keeps track of all the robots of all types at this point in the game"""

    def __init__(self, ore_cost, clay_cost, obsidian_cost, geode_cost):
        self.data = {
            "ore": Robots(ore_cost, 1),
            "clay": Robots(clay_cost, 0),
            "obsidian": Robots(obsidian_cost, 0),
            "geode": Robots(geode_cost, 0),
        }

    def __repr__(self):
        return self.data.__repr__()

    def produce(self, n_ticks: int = 1):
        production = {key: self[key].quantity * n_ticks for key in ROCKS}
        return Assets(**production)

    def spawn(self, rock: Rock, purse: Purse):
        self[rock].spawn(purse)

    def time_to_newbot(self, orig_purse: Purse, rock: Rock):
        cost_of_bot = self[rock].cost
        production = self.produce()
        purse = orig_purse.copy()

        time = 0
        while not purse.sufficient_funds(cost_of_bot):
            purse.add(production)
            time += 1
            assert time < DEADLINE, "infinite loop check failed"

        return time

    def copy(self):
        new_copy = RobotOverlord(
            ore_cost=self["ore"].cost,
            clay_cost=self["clay"].cost,
            obsidian_cost=self["obsidian"].cost,
            geode_cost=self["geode"].cost,
        )
        for rock in ROCKS:
            new_copy[rock].quantity = self[rock].quantity
        return new_copy


class Blueprint:
    __slots__ = [
        "id",
        "purse",
        "robots",
        "ticks",
    ]

    def __init__(self, blueprint_id: int, robots: RobotOverlord, purse=None, ticks=0):
        self.id = blueprint_id
        self.robots = robots
        if purse is not None:
            self.purse = purse
        else:
            self.purse = Purse()
        self.ticks = ticks

    def __repr__(self):
        return f"Blueprint(id={self.id}, robots={self.robots}, purse={self.purse}, ticks={self.ticks})"  # noqa: E501

    def copy(self):
        return Blueprint(
            blueprint_id=self.id,
            robots=self.robots.copy(),
            purse=self.purse.copy(),
            ticks=self.ticks,
        )

    # you don't want any more harvest than you can spend in
    # one cycle, because you can only make one bot per cycle
    # in addition, if you have some unspent rocks in your purse, those
    # count as output to reduce the number of bots needed
    @property
    def max_ore_bots(self):
        return max(self.robots[rock].cost["ore"] for rock in ROCKS) - (
            self.purse["ore"] // max(1, DEADLINE - self.ticks - 5)
        )

    @property
    def max_clay_bots(self):
        return self.robots["obsidian"].cost["clay"] - (
            self.purse["clay"] // max(1, DEADLINE - self.ticks - 5)
        )

    @property
    def max_obsidian_bots(self):
        return self.robots["geode"].cost["obsidian"] - (
            self.purse["obsidian"] // max(1, DEADLINE - self.ticks - 3)
        )

    @staticmethod
    def from_input_text(line):
        ic(line)
        blueprint, clay, obsidian, geode, _ = line.split(".")
        blueprint, ore = blueprint.split(":")

        blueprint_id = numbers(blueprint)[0]

        ore_cost = numbers(ore)[0]
        ore_robot_cost = Assets(ore=ore_cost)

        clay_cost = numbers(clay)[0]
        clay_robot_cost = Assets(ore=clay_cost)

        obsidian_ore, obsidian_clay = numbers(obsidian)
        obsidian_robot_cost = Assets(ore=obsidian_ore, clay=obsidian_clay)

        geode_ore, geode_obsidian = numbers(geode)
        geode_robot_cost = Assets(ore=geode_ore, obsidian=geode_obsidian)

        robots = RobotOverlord(
            ore_cost=ore_robot_cost,
            clay_cost=clay_robot_cost,
            obsidian_cost=obsidian_robot_cost,
            geode_cost=geode_robot_cost,
        )
        return Blueprint(blueprint_id, robots)

    @property
    def score(self):
        return self.id * self.purse["geode"]

    def run_one_event(self, next_move: Event):
        # figure out how much clock to use
        if next_move != "run":
            # buy a robot event
            new_ticks = self.robots.time_to_newbot(self.purse, next_move)
        else:
            # run out the clock event
            new_ticks = DEADLINE - self.ticks
            assert new_ticks > 0

        # produce output for that many ticks
        self.purse.add(self.robots.produce(new_ticks))
        self.ticks += new_ticks

        # if it was a 'buy a bot' event, buy the bot
        if next_move != "run":
            # the robot doesn't produce the turn where it is bought
            # so produce output with current bots, then add new
            # bot to the pool for the next tick
            production = self.robots.produce(1)
            self.robots.spawn(next_move, self.purse)
            self.purse.add(production)
            self.ticks += 1

    def feasible_next_event(self) -> Event:
        found_move = False

        # magic number 2:
        # we can get enough assets to buy the bot in n ticks
        # which we can spend at the beginning of turn n + 1
        # and we get our first output in turn n + 2
        # if a geode-robot can't produce output before deadline, no sense in buying it
        # an obsidian bot needs to produce output one earlier, because it needs to
        # go into a geode-purchase in order to increase score
        # and an ore or clay needs to produce outputs two earlier than the
        # geode bot deadline

        # if we have an obsidian bot, we can maybe buy a geode one
        if self.robots["obsidian"].quantity > 0:
            ticks = self.robots.time_to_newbot(self.purse, "geode")
            if (self.ticks + ticks + 2) <= DEADLINE:
                found_move = True
                yield "geode"

        # if we have a clay bot, we can maybe buy an obsidian one
        if (
            self.robots["clay"].quantity > 0
            and self.robots["obsidian"].quantity < self.max_obsidian_bots
        ):
            ticks = self.robots.time_to_newbot(self.purse, "obsidian")
            if (self.ticks + ticks + 4) <= DEADLINE:
                found_move = True
                yield "obsidian"

        # ore and clay bots can be purchased using bootstrap ore bot
        if self.robots["clay"].quantity < self.max_clay_bots:
            ticks = self.robots.time_to_newbot(self.purse, "clay")
            if (self.ticks + ticks + 6) <= DEADLINE:
                found_move = True
                yield "clay"

        if self.robots["ore"].quantity < self.max_ore_bots:
            ticks = self.robots.time_to_newbot(self.purse, "ore")
            if (self.ticks + ticks + 6) <= DEADLINE:
                found_move = True
                yield "ore"

        # if we haven't yielded anythiny yet, but we have geode-bots, run out the clock
        if (not found_move) and (self.robots["geode"].quantity > 0):
            yield "run"


# --> Puzzle solution
def solve_blueprint(bp):
    best_score = 0

    worklist = deque()

    for event in bp.feasible_next_event():
        job = bp.copy()
        job.run_one_event(event)
        worklist.append(job)

    assert len(worklist) > 0

    while worklist:
        job = worklist.popleft()
        assert job.ticks < DEADLINE

        for event in job.feasible_next_event():
            newjob = job.copy()
            newjob.run_one_event(event)

            if newjob.ticks == DEADLINE:
                best_score = max(newjob.score, best_score)
            else:
                worklist.append(newjob)

    return best_score


def solve(input_data):
    total_score = 0
    for line in input_data.splitlines():
        game = Blueprint.from_input_text(line)
        score = solve_blueprint(game)
        total_score += score
    return total_score


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE = """Blueprint 1: Each ore robot costs 4 ore. Each clay robot costs 2 ore. Each obsidian robot costs 3 ore and 14 clay. Each geode robot costs 2 ore and 7 obsidian.
Blueprint 2: Each ore robot costs 2 ore. Each clay robot costs 3 ore. Each obsidian robot costs 3 ore and 8 clay. Each geode robot costs 3 ore and 12 obsidian."""  # noqa: E501


def test_detailed_example():
    line = EXAMPLE.splitlines()[0]
    bp = Blueprint.from_input_text(line)

    # can buy clay-bot at minute 3
    bp.run_one_event("clay")

    assert bp.ticks == 3
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 0
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 1

    # buy clay-bot at minute 5
    bp.run_one_event("clay")

    assert bp.ticks == 5
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 2
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 2

    # buy clay-bot at minute 7
    bp.run_one_event("clay")

    assert bp.ticks == 7
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 6
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 3

    # buy obsidian-bot at minute 11
    bp.run_one_event("obsidian")

    assert bp.ticks == 11
    assert bp.purse["ore"] == 2
    assert bp.purse["clay"] == 4
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 3
    assert bp.robots["obsidian"].quantity == 1

    # buy clay-bot at minute 12
    bp.run_one_event("clay")

    assert bp.ticks == 12
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 7
    assert bp.purse["obsidian"] == 1
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 1

    # buy obsidian bot at minute 15
    bp.run_one_event("obsidian")

    assert bp.ticks == 15
    assert bp.purse["ore"] == 1
    assert bp.purse["clay"] == 5
    assert bp.purse["obsidian"] == 4
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 2

    # buy geode bot at minute 18
    bp.run_one_event("geode")

    assert bp.ticks == 18
    assert bp.purse["ore"] == 2
    assert bp.purse["clay"] == 17
    assert bp.purse["obsidian"] == 3
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 2
    assert bp.robots["geode"].quantity == 1

    # buy geode bot at minute 21
    bp.run_one_event("geode")

    assert bp.ticks == 21
    assert bp.purse["ore"] == 3
    assert bp.purse["clay"] == 29
    assert bp.purse["obsidian"] == 2
    assert bp.purse["geode"] == 3
    assert bp.robots["ore"].quantity == 1
    assert bp.robots["clay"].quantity == 4
    assert bp.robots["obsidian"].quantity == 2
    assert bp.robots["geode"].quantity == 2

    # run out the clock
    bp.run_one_event("run")
    assert bp.purse["ore"] == 6
    assert bp.purse["clay"] == 41
    assert bp.purse["obsidian"] == 8
    assert bp.purse["geode"] == 9


# Test any examples given in the problem
@pytest.mark.parametrize("sample_data,sample_solution", [(EXAMPLE, 33)], ids=idfn)
def test_full_example(sample_data, sample_solution) -> None:
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
    my_input = Path("input.txt").read_text()
    result = solve(my_input)
    print(result)
