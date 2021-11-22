from context import RunCtx
from text import Text, from_str

class Result:
    def text(self) -> Text:
        raise NotImplementedError()

    # If dependent tasks should continue after this result
    def allow_continue(self, ctx: RunCtx) -> bool:
        raise NotImplementedError

# Completed and/or already done
class SuccessResult(Result):
    def text(self) -> Text:
        return from_str('success')

    def allow_continue(self, ctx: RunCtx) -> bool:
        return True

# Not in the correct state and no attempt was made to correct it
class UndoneResult(Result):
    def __init__(self, reason: Text) -> None:
        self.reason = reason

    def text(self) -> Text:
        return from_str('undone: ') + self.reason

    def allow_continue(self, ctx: RunCtx) -> bool:
        return not ctx.execute

# There was an error performing this task
class FailedResult(Result):
    def __init__(self, reason: Text) -> None:
        self.reason = reason

    def text(self) -> Text:
        return from_str('failed: ') + self.reason

    def allow_continue(self, ctx: RunCtx) -> bool:
        return False
