"""Release script."""
import re

from typing import List


VERSION = '1.0.2'


def readlines(filename: str) -> List[str]:
    """Read a file as a list of lines."""
    with open(filename) as in_f:
        return in_f.readlines()


def writelines(filename: str, lines: List[str]) -> None:
    """Write a list of lines to a file."""
    with open(filename, 'w') as out_f:
        out_f.write(''.join(lines))


def update_version(filename: str, pattern: str, version: str) -> None:
    """Update the version in a file."""
    def replace_version(line: str) -> str:
        if re.match(pattern, line):
            return re.sub(pattern, fr'\g<1>{version}\g<2>', line)
        else:
            return line

    writelines(filename, map(replace_version, readlines(filename)))


update_version('pyproject.toml', r'(^version = ")[0-9]+\.[0-9]+\.[0-9]+("$)',  VERSION)
update_version('docs/conf.py', r"(^.*release = ')[0-9]+\.[0-9]+\.[0-9]+('$)", VERSION)
update_version('CHANGES.md', r'(## )Dev($)',  VERSION)
