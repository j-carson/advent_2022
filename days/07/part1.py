import sys
from collections import namedtuple
from pathlib import Path

import pytest
from icecream import ic

EXAMPLE = """$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""


class Directory:
    def __init__(self, name):
        self.files = []
        self.subdirectories = []
        self.parent = None
        self.name = name

    @property
    def size(self):
        return sum((d.size for d in self.subdirectories)) + sum(
            (f.size for f in self.files)
        )

    def add_file(self, f):
        self.files.append(f)

    def add_subdirectory(self, name):
        child = Directory(name)
        child.parent = self
        self.subdirectories.append(child)

    def iter_subdirectories(self):
        for d in self.subdirectories:
            yield from d.iter_subdirectories()
        yield self

    def find_deep_subdirectory(self, name):
        for d in self.iter_subdirectories():
            if d.name == name:
                return d
        raise Exception("oooops, fell off the end")

    def find_child_directory(self, name):
        for d in self.subdirectories:
            if d.name == name:
                return d
        raise Exception("ooops, fell off the end")


File = namedtuple("File", "size,name")


# --> Puzzle solution


def parser(input_data):
    root = Directory("/")
    current_location = None

    command_outputs = input_data.split("$")
    for block in command_outputs:
        # $ is first char and yields empty block
        if not block:
            continue

        lines = block.splitlines()
        command = lines[0].strip()

        command_type = command[:2]
        assert command_type in ("cd", "ls")

        if command_type == "cd":
            cd, dest = command.strip().split()
            if dest == "/":
                current_location = root
            elif dest == "..":
                current_location = current_location.parent
            else:
                current_location = current_location.find_child_directory(dest)
        else:
            for line in lines[1:]:
                word1, word2 = line.strip().split()
                if word1 == "dir":
                    # dir directory_name
                    current_location.add_subdirectory(word2)
                else:
                    # 1234 file_name
                    current_location.add_file(File(int(word1), word2))
    return root


def solve(input_data):
    root_directory = parser(input_data)
    return sum(d.size for d in root_directory.iter_subdirectories() if d.size <= 100000)


# --> Test driven development helpers

# keep pytest ids smaller
def idfn(maybe_string):
    if isinstance(maybe_string, str):
        # chop off long input strings in test name output
        return maybe_string[:5].strip()
    return str(maybe_string)


# Test any examples given in the problem
@pytest.fixture(scope="module")
def sample_tree():
    return parser(EXAMPLE)


@pytest.mark.parametrize(
    "dirname,size", [("e", 584), ("a", 94853), ("d", 24933642), ("/", 48381165)]
)
def test_directory_examples(sample_tree, dirname, size) -> None:
    d = sample_tree.find_deep_subdirectory(dirname)
    assert d.size == size


def test_sample():
    assert solve(EXAMPLE) == 95437


# --> Setup and run

if __name__ == "__main__":

    #  Run the test examples with icecream debug-trace turned on
    ic.enable()
    ex = pytest.main([__file__, "--capture=tee-sys"])
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
