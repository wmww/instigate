from context import RunCtx
from result import Result, SuccessResult, FailedResult, UndoneResult
from context import info
from text import from_str, Text

from typing import Callable, Optional, List, Set
import logging
import traceback

TaskFn = Callable[[RunCtx], Result]

class Task:
    def __init__(self, name: str) -> None:
        self.name = name
        self.result: Optional[Result] = None

    def run(self, ctx: RunCtx) -> None:
        raise NotImplementedError()

    def mark_result(self, result: Result) -> None:
        raise NotImplementedError()

    def result_text(self) -> Text:
        if self.result is not None:
            return self.result.text()
        else:
            return from_str('(not run)')

    def name_result_text(self) -> Text:
        result = from_str(self.name)
        if self.result is not None:
            result += from_str(': ') + self.result.text()
        return result

    def text(self) -> Text:
        raise NotImplementedError()

class SequenceTask(Task):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.tasks: List[Task] = []

    def add_task(self, task: Task) -> None:
        assert self.result is None, 'add_task() after SequenceTask has result'
        self.tasks.append(task)

    def run(self, ctx: RunCtx) -> None:
        failed_task: Optional[Task] = None
        for task in self.tasks:
            if failed_task is None:
                task.run(ctx)
                assert task.result is not None, 'task result None after being run'
                if not task.result.allow_continue(ctx):
                    failed_task = task
            else:
                task.mark_result(UndoneResult(from_str(failed_task.name + ' failed')))
        if failed_task is None:
            self.result = SuccessResult()
        else:
            self.result = FailedResult(from_str(failed_task.name + ' failed'))

    def mark_result(self, result: Result) -> None:
        assert self.result is None, 'mark_result() called after task already had result'
        for task in self.tasks:
            task.mark_result(UndoneResult(from_str('sequence skipped')))
        self.result = result

    def text(self) -> Text:
        result = self.name_result_text() + from_str(':\n')
        for task in self.tasks:
            result += from_str('  - ') + task.text() + from_str('\n')
        return result

class FnTask(Task):
    def __init__(self, name: str, fn: TaskFn) -> None:
        super().__init__(name)
        self.fn = fn

    def run(self, ctx: RunCtx) -> None:
        logging.info('running task %s', self.name)
        try:
            result = self.fn(ctx)
        except Exception as e:
            result = FailedResult(from_str(str(e)))
            logging.info('failed to run task: %s', traceback.format_exc())
        self.result = result
        logging.info('task %s done with result %s',  result.text().to_basic_str())

    def mark_result(self, result: Result) -> None:
        assert self.result is None, 'mark_result() called after task already had result'
        self.result = result

    def text(self) -> Text:
        return self.name_result_text()

def task(name: str, fn: TaskFn) -> None:
    from mission import add_task_to_current
    add_task_to_current(FnTask(name, fn))
