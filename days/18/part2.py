import sys
from pathlib import Path

import pytest
from icecream import ic

from collections import Counter
from typing import NamedTuple

DIRECTIONS = ["north", "south", "east", "west", "up", "down"]
OPPOSITE_DIRECTION = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
    "up": "down",
    "down": "up",
}
PERPENDICULAR_DIRECTIONS = {
    "north": ["up", "down", "east", "west"],
    "south": ["up", "down", "east", "west"],
    "east": ["up", "down", "north", "south"],
    "west": ["up", "down", "north", "south"],
    "up": ["north", "south", "east", "west"],
    "down": ["north", "south", "east", "west"],
}


class Point3D(NamedTuple):
    x: int
    y: int
    z: int

    def neighbor_cube(self, direction):
        x, y, z = self.x, self.y, self.z
        match direction:
            case "east":
                return Point3D(x + 1, y, z)
            case "west":
                return Point3D(x - 1, y, z)
            case "north":
                return Point3D(x, y + 1, z)
            case "south":
                return Point3D(x, y - 1, z)
            case "up":
                return Point3D(x, y, z + 1)
            case "down":
                return Point3D(x, y, z - 1)
        raise ValueError(f"{direction} is not a direction name")

    def neighbor_cubes(self):
        for direction in DIRECTIONS:
            yield self.neighbor_cube(direction), direction

    def __repr__(self):
        return f"Point3D({self.x},{self.y},{self.z})"


class Face:
    __slots__ = ["point", "side"]

    def __init__(self, point, side):
        self.point = point
        self.side = side

    def get_alias(self):
        """The WEST face of cube(x,y,z) is co-located
        with the EAST face of cube(x-1,y,z)"""

        neighbor = self.point.neighbor_cube(self.side)
        return Face(neighbor, OPPOSITE_DIRECTION[self.side])

    @property
    def key(self):
        return (*self.point, self.side)

    def __repr__(self):
        return f"Face({self.point},side={self.side})"


class ExposedFace(Face):
    __slots__ = ["color"]
    CATALOG = {}

    def __repr__(self):
        return f"ExposedFace({self.point},{self.side},color={self._color})"

    def __init__(self, point, side):
        super().__init__(point, side)
        self.color = 0
        self.CATALOG[self.key] = self

    @classmethod
    def lookup(cls, item):
        if item.key in cls.CATALOG:
            return cls.CATALOG[item.key]
        return None

    @classmethod
    def reset(cls):
        """Reset between tests"""
        cls.CATALOG = {}

    def neighbor_faces(self):
        candidates = []

        perp_dirs = PERPENDICULAR_DIRECTIONS[self.side]
        for pdir in perp_dirs:
            worklist = [
                Face(self.point.neighbor_cube(self.side), pdir),
                Face(self.point.neighbor_cube(pdir), self.side),
                Face(self.point, pdir),
            ]
            for face in worklist:
                alias = face.get_alias()
                if candidate := ExposedFace.lookup(face):
                    candidates.append(candidate)
                    assert ExposedFace.lookup(alias) is None
                    break
                if candidate := ExposedFace.lookup(alias):
                    candidates.append(candidate)
                    break

        assert len(candidates) == 4
        return candidates

    def unvisited_neighbors(self):
        return [face for face in self.neighbor_faces() if face.color == 0]


def parse(input_data):
    result = set()
    for line in input_data.splitlines():
        nums = [int(n) for n in line.split(",")]
        result.add(Point3D(*nums))
    return result


def solve(input_data):
    points = parse(input_data)
    exposed = 0

    ExposedFace.reset()
    assert len(ExposedFace.CATALOG) == 0

    # find the points for part 1, but this time
    # keep track of adjoining faces
    for point in points:
        for cube, side in point.neighbor_cubes():
            if cube not in points:
                exposed += 1
                ExposedFace(point, side)

    color = 0
    for item in ExposedFace.CATALOG.values():
        if item.color == 0:
            color = color + 1
            item.color = color
            worklist = item.unvisited_neighbors()

            while worklist:
                job = worklist.pop()
                if job.color == 0:
                    job.color = color
                    worklist.extend(job.unvisited_neighbors())
                else:
                    assert job.color == color, "one node has two colors"

    counts = Counter((item.color for item in ExposedFace.CATALOG.values()))
    assert counts[0] == 0
    return counts.most_common(1)[0][1]


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


EXAMPLE_1 = """1,1,1\n2,1,1"""
EXAMPLE_2 = """2,2,2
1,2,2
3,2,2
2,1,2
2,3,2
2,2,1
2,2,3
2,2,4
2,2,6
1,2,5
3,2,5
2,1,5
2,3,5"""


# Test any examples given in the problem
@pytest.mark.parametrize(
    "sample_data,sample_solution", [(EXAMPLE_1, 10), (EXAMPLE_2, 58)], ids=idfn
)
def test_samples(sample_data, sample_solution) -> None:
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
    ic.disable()
    my_input = Path("input.txt").read_text()
    result = solve(my_input)
    print(result)
