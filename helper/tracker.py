from .models import Changes, Info, Log
import os


class Tracker:
    def gen_log(path: str) -> Log:
        '''Returns info generated from get_info() for each file and folder within given path. Excluding path itself.
        * Retuns None when path is not found or IO exception occurs.'''
        try:
            log = Log()
            for root, dirs, files in os.walk(path):
                for dir in dirs:
                    info = Tracker.__gen_info(os.path.join(root, dir))
                    log.add_info(info)
                for file in files:
                    info = Tracker.__gen_info(os.path.join(root, file))
                    log.add_info(info)
            return log
        except:
            return None

    def compare(old_log: Log, new_log: Log) -> Changes:
        '''TODO'''
        if not (old_log and new_log):
            return

        changes = Changes()
        renamed_dirs = []
        for new_info in new_log.infos:
            old_info = old_log.find(new_info.inode)
            if old_info:
                if new_info.name != old_info.name:
                    changes.renamed(old_info, new_info)
                    if not old_info.isfile:
                        renamed_dirs.append((old_info.fullpath, new_info.fullpath))
                if new_info.path != old_info.path:
                    if not Tracker.__is_false_move(old_info, new_info, renamed_dirs):
                        changes.moved(old_info, new_info)
                if new_info.mtime != old_info.mtime:
                    if old_info.isfile:
                        changes.modified(old_info, new_info)
            else:
                changes.added(new_info.fullpath)

        for old_info in old_log.infos:
            if not new_log.find(old_info.inode):
                changes.deleted(old_info.fullpath)

        return changes

    def __is_false_move(old_info: Info, new_info: Info, renamed_dirs: list[tuple[str, str]]) -> bool:
        for old_name, new_name in renamed_dirs:
            if old_info.path == old_name:
                return new_info.path == new_name

    def __gen_info(file: str) -> Info:
        '''Returns stats of a single files/folders.
        Keys    Description
        =====   ============
        inode   inode number
        mtime   modification time in seconds
        path    path of file
        name    filename
        isfile  stores boolean value

        * Size of a folder is always 0.
        * Returns None if file not found or IO exception occurs.'''
        try:
            stats = os.stat(file)
            inode = str(stats.st_ino) # converting to string to avoid OverflowError in sqlite
            # size = stats.st_size ;because it's of no use.
            # ctime = int(stats.st_ctime); because it's of no use.
            mtime = int(stats.st_mtime)
            sep_index = file.rfind(os.path.sep)
            if sep_index == -1:
                path = ''
            else:
                path = file[:sep_index]
            name = file[sep_index + 1:]
            isfile = os.path.isfile(file)
            info = Info(inode, mtime, path, name, isfile)
            return info
        except:
            pass
