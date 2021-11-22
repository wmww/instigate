from typing import List, Tuple, Callable
from argparse import ArgumentParser, Namespace
import logging

from .mission import mission_list_instance, MissionList
from .context import RunCtx, info, Info, set_info
from .text import TextCtx

# TODO:
# - persistant logging

class UserError(Exception):
    pass

def parse_args() -> Namespace:
    parser = ArgumentParser(description='Idempotently initialize a system')
    parser.add_argument('scripts', nargs='+', help=
        'list of mission scripts to run. ' +
        'May include relative and absolute paths. ' +
        'WARNING: mission scripts may execute arbitrary code. Only run trusted scripts.'
    )
    parser.add_argument('-x', '--execute', action='store_true', help='make changes to the system if needed')
    parser.add_argument('-s', '--scout', action='store_true', help='check which tasks are done without making changes to the system')
    parser.add_argument('-l', '--list', action='store_true', help='show missions and tasks that would be performed')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose output')
    # parser.add_argument('--no-color', action='store_true', help='disable colored output')
    return parser.parse_args()

def show_missions(missions: MissionList, ctx: RunCtx) -> None:
    print(missions.text(ctx).to_str(info().text))

def execute_action(missions: MissionList) -> None:
    ctx = RunCtx(True)
    missions.run(ctx)
    show_missions(missions, ctx)

def scout_action(missions: MissionList) -> None:
    ctx = RunCtx(False)
    missions.run(ctx)
    show_missions(missions, ctx)

def list_action(missions: MissionList) -> None:
    ctx = RunCtx(True)
    show_missions(missions, ctx)

def get_action(args: Namespace) -> Callable[[MissionList], None]:
    action_fns = {
        'execute': execute_action,
        'scout': scout_action,
        'list': list_action,
    }
    actions: List[str] = []
    for name, fn in action_fns.items():
        if getattr(args, name):
            actions.append(name)
    if len(actions) == 0:
        raise UserError(
            'no action specified, use one of: ' +
            ', '.join('--' + name for name, fn in action_fns.items())
        )
    elif len(actions) > 1:
        raise UserError(
            'multiple actions specified: ' +
            ', '.join('--' + name for name in actions)
        )
    return action_fns[actions[0]]

def load_scripts(script_list: List[str]):
    for script in script_list:
        mission_list_instance.load_mission(script)
    if mission_list_instance.error:
        raise UserError('faild to load missions')
    mission_list_instance.sort_missions()
    if mission_list_instance.error:
        raise UserError('faild to order missions')

def main() -> None:
    try:
        args = parse_args()
        log_level = logging.DEBUG if args.verbose else logging.WARNING
        logging.basicConfig(level=log_level)
        set_info(Info(TextCtx(False)))
        action = get_action(args)
        load_scripts(args.scripts)
        action(mission_list_instance)
    except UserError as e:
        logging.error('%s', str(e))
        exit(1)
