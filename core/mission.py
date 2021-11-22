from .task import SequenceTask, Task
from .context import RunCtx
from .result import UndoneResult
from .text import Text, from_str

from collections import OrderedDict
from typing import List, Optional
import importlib.util
import os
import logging

class Mission:
    def __init__(self, name: str) -> None:
        self.name = name
        self.depends: 'OrderedDict[Mission, None]' = OrderedDict()
        self.task = SequenceTask('tasks')

    def add_depend(self, task: 'Mission') -> None:
        assert self.task.result is None, 'add_depend() after Mission has result'
        self.depends[task] = None

    def text(self) -> Text:
        result = from_str(self.name + ':\n')
        result += from_str('depends:\n')
        for depend, none in self.depends.items():
            result += from_str('  - ' + depend.name + '\n')
        result += self.task.text()
        return result

    def __str__(self) -> str:
        return self.name

current_mission: Optional[Mission] = None
current_task: Optional[SequenceTask] = None

def _load_mission(path: str, name: str) -> Mission:
    global current_mission
    global current_task
    mission = Mission(name)
    prev_mission = current_mission
    prev_task = current_task
    current_mission = mission
    current_task = mission.task
    try:
        path = os.path.expanduser(path)
        spec = importlib.util.spec_from_file_location('mission_mod', path)
        assert spec is not None, path + ' failed to load as python module'
        mod = importlib.util.module_from_spec(spec)
        assert isinstance(spec.loader, importlib.abc.Loader)
        spec.loader.exec_module(mod)
        return mission
    finally:
        assert current_mission == mission, (
            'current_mission incorrect ' +
            '(it is ' + str(current_mission) + ' instead of ' + str(mission) + ')'
        )
        assert current_task == mission.task, (
            'current_task incorrect ' +
            '(it is ' + str(current_task) + ' instead of ' + str(mission.task) + ')'
        )
        current_mission = prev_mission
        current_task = prev_task

def canonicalize_name(path: str) -> str:
    path = os.path.abspath(os.path.realpath(os.path.expanduser(path)))
    user = os.path.expanduser('~')
    if path.startswith(user):
        path = '~' + path[len(user):]
    assert path.endswith('.py'), 'mission path ' + path + ' does not end with .py'
    return path

class MissionList:
    def __init__(self) -> None:
        self.missions: 'OrderedDict[str, Mission]' = OrderedDict()
        self.error = False

    def load_mission(self, path: str) -> Optional[Mission]:
        try:
            name = canonicalize_name(path)
            mission = self.missions.get(name)
            if mission is not None:
                return mission
            mission = _load_mission(path, name)
            self.missions[name] = mission
            return mission
        except Exception as e:
            logging.error('failed to load mission: %s', str(e))
            self.error = True
            return None

    def sort_missions(self) -> None:
        logging.error('MissionList.sort_missions() not implemented')
        return

    def run(self, ctx: RunCtx) -> None:
        for name, mission in self.missions.items():
            failed_depends: List[Mission] = []
            for depend, none in mission.depends.items():
                assert depend.task.result is not None, (
                    mission.name + ' depends on ' + depend.name + ', which has not run ' +
                    '(probably bug in MissionList.sort_missions())'
                )
                if not depend.task.result.allow_continue(ctx):
                    failed_depends.append(depend)
            if len(failed_depends) == 0:
                logging.info('running %s…')
                mission.task.run(ctx)
                logging.info('%s done with result %s', mission.name, mission.task.result_text())
            else:
                message = ', '.join(depend.name for depend in failed_depends) + ' failed'
                mission.task.mark_result(UndoneResult(from_str(message)))

    def text(self, ctx: RunCtx) -> Text:
        result = from_str('Missions:\n')
        for name, mission in self.missions.items():
            result += mission.text()
        return result

mission_list_instance = MissionList()

def mission(name: str) -> None:
    global mission_list_instance
    global current_mission
    sub_mission = mission_list_instance.load_mission(name)
    assert current_mission is not None, 'mission() should only be called while loading a mission'
    if sub_mission is not None:
        current_mission.add_depend(sub_mission)

def add_task_to_current(task: Task):
    assert current_task is not None, 'add_task_to_current() called with no current task'
    current_task.add_task(task)
