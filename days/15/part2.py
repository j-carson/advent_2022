import sys
from collections import namedtuple
from pathlib import Path

import pytest
from icecream import ic

# --> Puzzle solution

Point = namedtuple("Point", "x,y")


class Range:
    def __init__(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max

    def __lt__(self, other):
        if self.x_min != other.x_min:
            return self.x_min < other.x_min
        return self.x_max < other.x_max

    def __repr__(self):
        return f"Range({self.x_min},{self.x_max})"


class SensorReading:
    def __init__(self, sensor, closest_beacon):
        self.sensor = sensor
        self.closest_beacon = closest_beacon

    def __repr__(self):
        return f"sensor={self.sensor} nearby={self.closest_beacon}"

    @property
    def manhattan_distance(self):
        return abs(self.sensor.x - self.closest_beacon.x) + abs(
            self.sensor.y - self.closest_beacon.y
        )

    @property
    def max_depth(self):
        return self.sensor.y + self.manhattan_distance

    @property
    def min_depth(self):
        return self.sensor.y - self.manhattan_distance

    def eval_row(self, row):
        if row < self.sensor.y:
            if row < self.min_depth:
                return None
            width = self.manhattan_distance - (self.sensor.y - row)
            return Range(self.sensor.x - width, self.sensor.x + width)

        if row > self.sensor.y:
            if row > self.max_depth:
                return None
            width = self.manhattan_distance - (row - self.sensor.y)
            return Range(self.sensor.x - width, self.sensor.x + width)

        width = self.manhattan_distance
        return Range(self.sensor.x - width, self.sensor.x + width)


def parser(input_text):
    def x(word):
        return int(word[2:-1])

    def y(word):
        if word[-1] == ":":
            return int(word[2:-1])
        return int(word[2:])

    result = []

    for line in input_text.splitlines():
        words = line.split()
        result.append(
            SensorReading(
                sensor=Point(x(words[2]), y(words[3])),
                closest_beacon=Point(x(words[8]), y(words[9])),
            )
        )
    return result


class Accumulator:
    def __init__(self, clip_low, clip_high):
        self.clip_low = clip_low
        self.clip_high = clip_high
        self.filled = []

    def add_range(self, rng):
        if rng.x_min < self.clip_low:
            rng.x_min = self.clip_low
        if rng.x_max > self.clip_high:
            rng.x_max = self.clip_high

        for fill in self.filled:
            if (fill.x_min <= rng.x_min <= fill.x_max) or (
                rng.x_min <= fill.x_min <= rng.x_max
            ):
                ic("merging", fill, rng)
                fill.x_min = min(fill.x_min, rng.x_min)
                fill.x_max = max(fill.x_max, rng.x_max)
                ic(self.filled)
                return

        ic("appending", rng)
        self.filled.append(rng)
        ic(self.filled)


def solve(input_data, key_range):
    sensor_data = parser(input_data)

    for key_row in range(key_range[0], key_range[1] + 1):
        ranges = []

        for reading in sensor_data:
            covered = reading.eval_row(key_row)
            if covered is not None:
                ic(covered)
                ranges.append(covered)

        acc = Accumulator(key_range[0], key_range[1])
        sorted_ranges = sorted(ranges)
        for r in sorted_ranges:
            acc.add_range(r)

        if len(acc.filled) > 1:
            return 4000000 * (acc.filled[0].x_max + 1) + key_row

    raise Exception("oops")


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE = """Sensor at x=2, y=18: closest beacon is at x=-2, y=15
Sensor at x=9, y=16: closest beacon is at x=10, y=16
Sensor at x=13, y=2: closest beacon is at x=15, y=3
Sensor at x=12, y=14: closest beacon is at x=10, y=16
Sensor at x=10, y=20: closest beacon is at x=10, y=16
Sensor at x=14, y=17: closest beacon is at x=10, y=16
Sensor at x=8, y=7: closest beacon is at x=2, y=10
Sensor at x=2, y=0: closest beacon is at x=2, y=10
Sensor at x=0, y=11: closest beacon is at x=2, y=10
Sensor at x=20, y=14: closest beacon is at x=25, y=17
Sensor at x=17, y=20: closest beacon is at x=21, y=22
Sensor at x=16, y=7: closest beacon is at x=15, y=3
Sensor at x=14, y=3: closest beacon is at x=15, y=3
Sensor at x=20, y=1: closest beacon is at x=15, y=3"""

# Test any examples given in the problem
@pytest.mark.parametrize(
    "sample_data,key_range,sample_solution", [(EXAMPLE, (0, 20), 56000011)], ids=idfn
)
def test_samples(sample_data, key_range, sample_solution) -> None:
    assert solve(sample_data, key_range) == sample_solution


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
    result = solve(my_input, (0, 4000000))
    print(result)
