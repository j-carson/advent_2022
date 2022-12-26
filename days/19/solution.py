import re
import sys
from collections import UserDict, deque
from pathlib import Path
from typing import Literal

import pytest
from icecream import ic

DEADLINE = 999
PART = 0


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

    def hashkey(self):
        return tuple(self.values())


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

    def hashkey(self):
        # no need to save the robot cost in the visit cache -
        # it doesn't change
        return tuple(self[bot].quantity for bot in ROCKS)


class Blueprint:
    __slots__ = ["id", "purse", "robots", "ticks", "deadline", "scoremethod"]

    def __init__(
        self,
        blueprint_id: int,
        robots: RobotOverlord,
        deadline,
        scoremethod,
        purse=None,
        ticks=0,
    ):
        self.id = blueprint_id
        self.robots = robots
        if purse is not None:
            self.purse = purse
        else:
            self.purse = Purse()
        self.ticks = ticks
        self.deadline = deadline
        self.scoremethod = scoremethod

    def __repr__(self):
        return f"Blueprint(id={self.id}, robots={self.robots}, purse={self.purse}, ticks={self.ticks})"  # noqa: E501

    def copy(self):
        return Blueprint(
            blueprint_id=self.id,
            robots=self.robots.copy(),
            purse=self.purse.copy(),
            ticks=self.ticks,
            deadline=self.deadline,
            scoremethod=self.scoremethod,
        )

    def hashkey(self):
        return (*self.robots.hashkey(), *self.purse.hashkey(), self.ticks)

    def purse_robot_adjustment(self, rock):
        # Example: If I have 5 rocks in my purse, and 5 ticks on the
        # clock left, the rocks in my purse are equivalent to putting
        # 1 robot online right now: The purse value reduces the max amount
        # of robots worth buying by 1. If there are 10 rocks in my purse,
        # and 5 ticks, that's equivalent to having two bots-worth of
        # rocks in my purse
        assert rock != "geode"
        if self.purse[rock] > 0:
            time_to_purse_worthless = self.bot_ready_deadline(rock) - self.ticks
            if time_to_purse_worthless > 0:
                return self.purse[rock] // time_to_purse_worthless
            # we're past the time when purse turns worthless: adjust purchase
            # hard enough that we will never buy
            return 999
        else:
            # if we have no rocks, the rocks are equivalent to 0 bots
            return 0

    def bot_purchase_deadline(self, rock):
        # If we buy a bot at time n, it starts producing at time n +1
        # and we have a rock to spend at time n+2
        # if the rock is geode, we need to buy that bot at DEADLINE -2
        # to have more geodes at DEADLINE
        # if the bot is obsidian, we need to buy that bot two earlier:
        # an obsidian bot is only useful if we can use it's output to
        # buy a geode bot before new geode bots are worthless
        # and for clay and ore, it's two earlier still: those bots are
        # only going to increase the final score if they can purchase
        # an obsidian bot before the obsidian bot deadline
        match rock:
            case "geode":
                return self.deadline - 2
            case "obsidian":
                return self.deadline - 4
            case "ore" | "clay":
                return self.deadline - 6

    # following above, there is a bot-online deadline that is
    # one tick AFTER the bot purchase deadline
    def bot_ready_deadline(self, rock):
        return self.bot_purchase_deadline(rock) + 1

    def need_more_bots(self, rock):
        if self.ticks + self.robots.time_to_newbot(
            self.purse, rock
        ) > self.bot_purchase_deadline(rock):
            return False

        match rock:
            case "ore":
                hard_limit = max(self.robots[rock].cost["ore"] for rock in ROCKS)
            case "clay":
                hard_limit = self.robots["obsidian"].cost["clay"]
            case "obsidian":
                hard_limit = self.robots["geode"].cost["obsidian"]
            case "geode":
                # No hard limit on number of useful geode bots, just
                # the purchase deadline counts
                return True

        return (
            self.robots[rock].quantity + self.purse_robot_adjustment(rock) < hard_limit
        )

    @staticmethod
    def from_input_text(line, deadline, scoremethod):
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
        return Blueprint(
            blueprint_id, robots, deadline=deadline, scoremethod=scoremethod
        )

    @property
    def score(self):
        if self.scoremethod == 1:
            return self.id * self.purse["geode"]
        if self.scoremethod == 2:
            return self.purse["geode"]
        raise Exception("oops")

    @property
    def theoretical_max_geodes(self):
        # what is the theoretical max number of geodes we could end with
        # if we bought a geode-bot every turn from now until the end of time,
        ticks_left = self.deadline - self.ticks
        minimum_score = self.purse["geode"] + self.robots.produce(ticks_left)["geode"]

        return minimum_score + (ticks_left * (ticks_left - 1)) // 2

    @property
    def theoretical_best_score(self):
        if self.scoremethod == 1:
            return self.id * self.theoretical_max_geodes
        if self.scoremethod == 2:
            return self.theoretical_max_geodes
        raise Exception("oops")

    def run_one_event(self, next_move: Event):
        # figure out how much clock to use
        if next_move != "run":
            # buy a robot event
            new_ticks = self.robots.time_to_newbot(self.purse, next_move)
        else:
            # run out the clock event
            new_ticks = self.deadline - self.ticks
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

        # if we have an obsidian bot, we can maybe buy a geode one
        if self.robots["obsidian"].quantity > 0 and self.need_more_bots("geode"):
            found_move = True
            yield "geode"

        # if we have a clay bot, we can maybe buy an obsidian one
        if self.robots["clay"].quantity > 0 and self.need_more_bots("obsidian"):
            found_move = True
            yield "obsidian"

        # ore and clay bots can be purchased using bootstrap ore bot
        if self.need_more_bots("clay"):
            found_move = True
            yield "clay"

        if self.need_more_bots("ore"):
            found_move = True
            yield "ore"

        # if we haven't yielded any bot-purchase-plans, but we have geode-bots, run out the clock
        if (not found_move) and (self.robots["geode"].quantity > 0):
            yield "run"


# --> Puzzle solution
def solve_blueprint(bp):
    best_score = 0

    worklist = deque()
    already_tried = set()
    job_count = 0
    cache_hit = 0
    theory_hit = 0

    for event in bp.feasible_next_event():
        job = bp.copy()
        job.run_one_event(event)

        hashkey = job.hashkey()
        assert hashkey not in already_tried
        already_tried.add(hashkey)
        worklist.append(job)
        job_count += 1

    assert len(worklist) > 0

    while worklist:
        job = worklist.pop()
        assert job.ticks < bp.deadline
        if job.theoretical_best_score < best_score:
            theory_hit += 1
            continue

        for event in job.feasible_next_event():
            newjob = job.copy()
            newjob.run_one_event(event)

            if newjob.ticks == bp.deadline:
                best_score = max(newjob.score, best_score)
            else:
                hashkey = newjob.hashkey()
                if hashkey not in already_tried:
                    already_tried.add(hashkey)
                    worklist.append(newjob)
                    job_count += 1
                else:
                    cache_hit += 1

    # stats note: cache_hit means it never hit job list
    # theory_hit: it was in the job list but was not useful by the time we went to run it
    ic(job_count)
    ic(cache_hit)
    ic(theory_hit)
    return best_score


def solve(input_data, part):
    if part == 1:
        total_score = 0
        for line in input_data.splitlines():
            game = Blueprint.from_input_text(line, deadline=24, scoremethod=1)
            score = solve_blueprint(game)
            total_score += score
        return total_score

    assert part == 2
    total_score = 1
    for line in input_data.splitlines()[:3]:
        game = Blueprint.from_input_text(line, deadline=32, scoremethod=2)
        score = solve_blueprint(game)
        total_score *= score
    return total_score
