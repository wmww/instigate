from instigate import task, RunCtx, Result, SuccessResult, FailedResult, UndoneResult

import subprocess
from typing import Optional, Dict, Sequence
import logging

def _stringify_arg(arg: str) -> str:
    arg = arg.replace('\n', '\\n')
    if ' ' in arg or '\t' in arg:
        if "'" not in arg:
            return "'" + arg + "'"
        elif '"' not in arg:
            return '"' + arg + '"'
        else:
            arg = arg.replace("'", "'\"'\"'")
            return "'" + arg + "'"
    else:
        return arg

def _run_task(args: Sequence[str], run_in_scout: bool, **kwargs) -> None:
    if 'capture_output' not in kwargs:
        kwargs['capture_output'] = True
    def fn(ctx: RunCtx) -> Result:
        if run_in_scout or ctx.execute:
            result = subprocess.run(args, **kwargs)
            if result.returncode == 0:
                return SuccessResult()
            else:
                return FailedResult('exited with code ' + str(result.returncode))
        else:
            return UndoneResult('not run')
    name = '$ ' + ' '.join(_stringify_arg(arg) for arg in args)
    task(name, fn)

def execute_run(args: Sequence[str], **kwargs) -> None:
    _run_task(args, False, **kwargs)

def scout_run(args: Sequence[str], **kwargs) -> None:
    _run_task(args, False, **kwargs)
