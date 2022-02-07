import re
import os
import traceback
from helper.tracker import Tracker
from helper.database import Database
from helper.utils import cls
'''UI for this app.'''


CURRENT_INDEX = ''
db = Database()
db.open()


def execute(command: str):
    global CURRENT_INDEX
    # INDEX AS
    pattern = r'(index|init|add|import) (.+) as (.+)'
    match = re.compile(pattern).fullmatch(command)
    if match:
        path = match.group(2)
        name = match.group(3)
        if not os.path.exists(path):
            print('Invalid path.')
            return
        if db.is_added(path=path):
            print('This path is already being tracked.')
            return
        if db.is_added(index_name=name):
            print('This name is already used.')
            return
        print('Indexing...')
        log = Tracker.gen_log(path)
        db.add_log(name, path, log)
        print('Indexed Successfully.')
        return

    # LIST
    if command == 'list':
        indexes = db.list_indexes()
        for i, index in enumerate(indexes):
            print(f'{i+1}. {index} - {db.get_path(index)}')
        print(f'Found {len(indexes)} indexes.')
        return

    # LOAD
    pattern = r'(load|use|check|checkout) (.+)'
    match = re.compile(pattern).fullmatch(command)
    if match:
        name = match.group(2)
        if name not in db.list_indexes():
            print('invalid name.')
            return
        CURRENT_INDEX = name
        return

    # UNLOAD
    if command == 'unload':
        CURRENT_INDEX = ''
        print('Unloaded successfully.')
        return

    # DIFF
    pattern = r'(diff|changes)( added| renamed| moved| deleted| modified){0,1}'
    match = re.compile(pattern).fullmatch(command)

    if match:
        if not CURRENT_INDEX:
            print('Load an index first.')
            return
        print('Compairing...')
        logs = db.list_logs(CURRENT_INDEX)
        old_log = db.get_log(logs[-1])
        new_log = Tracker.gen_log(db.get_path(CURRENT_INDEX))
        changes = Tracker.compare(old_log, new_log)
        if match.group(2):
            ch_type = match.group(2).strip()
            map = {'added': changes.ADDED, 'deleted': changes.DELETED,
                   'renamed': changes.RENAMED, 'moved': changes.MOVED,
                   'modified': changes.MODIFIED}
            changes = changes.filter(map[ch_type])
        changes.human_readable()
        return

    # OVERWRITE
    if command == 'overwrite':
        if not CURRENT_INDEX:
            print('Load an index first.')
            return
        last_log = db.list_logs(CURRENT_INDEX)[-1]
        print('Overwriting...')
        log = Tracker.gen_log(db.get_path(CURRENT_INDEX))
        db.overwrite_log(last_log, log)
        print('Overwritten successfully.')
        return

    # REMOVE
    pattern = r'(delete|del|remove|rem) (.+)'
    match = re.compile(pattern).fullmatch(command)
    if match:
        index_name = match.group(2)
        if index_name not in db.list_indexes():
            print('Invalid index name.')
            return
        db.rem_index(index_name)
        if CURRENT_INDEX == index_name:
            CURRENT_INDEX = ''
        print('removed successfully.')
        return

    # CLS
    if command.lower() in ('cls', 'clear'):
        cls()
        return

    # HELP
    if command.lower() in ('help', '?', '/?'):
        simple_help()
        return

    # SUDO HELP
    if command.lower() in ('sudo help', 'sudo ?', 'sudo /?'):
        advance_help()
        return

    print('Invalid command.')


def simple_help():
    command_desc = {
        'index [path] as [index_name]': 'Indexes specified folder and adds it to database.',
        'list': 'Lists all added indexes.',
        'remove [index_name]': 'Removes index from database.',
        'load [index_name]': 'Loads index to memory.',
        'unload': 'Unloads index from memory.',
        'diff [added|renamed|moved|deleted|modified]': 'Displays changes occured since index was added.',
        'overwrite': 'Overwrite current changes into database.',
        'help': 'Displays simple help screen.',
        'sudo help': 'Displays advance help screen.'
    }
    for command, desc in command_desc.items():
        print(f'{command} --> {desc}')
    print()


def advance_help():
    command_desc = {
        '(index|init|add|import) [path] as [index_name]': 'Indexes specified folder and adds it to database.',
        'list': 'Lists all added indexes.',
        '(remove|delete|del|rem) [index_name]': 'Removes index from database.',
        '(load|use|check|checkout) [index_name]': 'Loads index to memory.',
        'unload': 'Unloads index from memory.',
        '(diff|changes) [added|renamed|moved|deleted|modified]': 'Displays changes occured since index was added.',
        'overwrite': 'Overwrite current changes into database.',
        '(help|?|/?)': 'Displays simple help screen.',
        'sudo (help|?|/?)': 'Displays advance help screen.'
    }
    for command, desc in command_desc.items():
        print(f'{command} --> {desc}')
    print()


while True:
    try:
        command = input(f'{CURRENT_INDEX}>>> ')
        if command.lower() in ('exit', 'quit'):
            break
        execute(command)
        print()
    except Exception:
        db.close()
        print('An error occurred!')
        traceback.print_exc()
        break
