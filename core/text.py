from typing import Tuple

class TextCtx:
    def __init__(self, color: bool) -> None:
        self.color = color

class Text:
    def to_str(self, ctx: TextCtx) -> str:
        raise NotImplementedError()

    def to_basic_str(self) -> str:
        return self.to_str(TextCtx(False))

    def __add__(self, rhs) -> 'Text':
        if isinstance(self, SeqText) and isinstance(rhs, SeqText):
            return SeqText(self.seq + rhs.seq)
        elif isinstance(self, SeqText):
            return SeqText(self.seq + (rhs,))
        elif isinstance(rhs, SeqText):
            return SeqText((self,) + rhs.seq)
        else:
            return SeqText((self, rhs))

class SeqText(Text):
    def __init__(self, seq: Tuple[Text, ...]) -> None:
        self.seq = seq

    def to_str(self, ctx: TextCtx) -> str:
        result = ''
        for i in self.seq:
            result += i.to_str(ctx)
        return result

class StrText(Text):
    def __init__(self, inner: str) -> None:
        self.inner = inner

    def to_str(self, ctx: TextCtx) -> str:
        return self.inner

def from_str(s: str) -> Text:
    return StrText(s)
