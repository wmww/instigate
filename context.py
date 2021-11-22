from typing import Optional
from text import TextCtx

class Info:
    def __init__(self, text: TextCtx) -> None:
        self.text = text

info_instance: Optional[Info] = None

def set_info(instance: Info) -> None:
    global info_instance
    info_instance = instance

def info() -> Info:
    assert info_instance is not None, 'no Info instance'
    return info_instance

class RunCtx:
    def __init__(self, execute: bool) -> None:
        # If to make changes to the system, in scout mode this is false
        self.execute = execute
