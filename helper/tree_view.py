import os
from typing import List


class TreeView:
    '''Displays tree structure for list of paths.'''

    def __init__(self, sort: bool = False) -> None:
        self.data = {'.': []}
        self.sort = sort

    def add_path(self, path: str):
        paths = path.split(os.path.sep)
        data_ref = self.data
        for e in paths:
            if e not in data_ref['.']:
                data_ref['.'].append(e)
                data_ref[e] = {'.': []}
            data_ref = data_ref[e]

    def add_paths(self, paths: List[str]):
        for path in paths:
            self.add_path(path)

    def _display(ref: dict, sort: bool = False, spaces: int = 0, indent: int = 3, lines_on: list = []):
        ''' ├ ─ └ │ '''
        def _print_spacing():
            for i in range(spaces):
                if i in lines_on:
                    print('│', end='')
                else:
                    print(' ', end='')

        i = 0
        names = sorted(ref['.']) if sort else ref['.']
        while i < len(names) - 1:
            name = names[i]
            _print_spacing()
            print(f'├──{name}')
            if ref[name]['.']:
                lines_on.append(spaces)
                TreeView._display(ref[name], sort, spaces+indent, indent)
            i += 1
        if spaces in lines_on:
            lines_on.remove(spaces)

        _print_spacing()
        print(f'└──{names[i]}')
        name = names[i]
        if ref[name]['.']:
            TreeView._display(ref[name], sort, spaces+indent, indent)

    def display(self):
        print(self.data)
        if len(self.data['.']) == 0:
            print('Nothing to display.')
            return

        ref = self.data
        name = ref['.'][0]
        if name == '':
            ref = ref[name]

        if len(ref['.']) == 1:
            name = ref['.'][0]
            print(name)
            TreeView._display(ref[name], self.sort)
        else:
            print('.')
            TreeView._display(ref, self.sort)
