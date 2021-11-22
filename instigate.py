#!/usr/bin/python3

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import core
else:
    import core

if __name__ == '__main__':
    core.runner.main()

