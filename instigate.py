#!/usr/bin/python3

from core.mission import mission
from core.result import SuccessResult, UndoneResult, FailedResult
from core.task import task
from core.context import info, Info, RunCtx

if __name__ == '__main__':
    import core
    core.runner.main()
