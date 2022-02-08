import sqlite3 as sql
from time import time
from typing import List

from .utils import milis_to_alpha
from .models import Log, Info


class Database:
    def __init__(self) -> None:
        self.__db = 'cache.db'
        self.__con = None
        self.__cur = None

    def open(self):
        if self.__con:
            return
        self.__con = sql.Connection(self.__db)
        self.__cur = self.__con.cursor()
        self.__create_info_table()

    def close(self):
        if self.__con:
            self.__con.close()
            self.__con = None

    # LOG
    def add_log(self, index_name: str, path: str, log: Log):
        curr_time = int(time())
        curr_time = milis_to_alpha(curr_time)
        self.__create_log_tables(curr_time)

        self.__cur.execute('''INSERT INTO info (index_name, path, log_name) VALUES (?, ?, ?)''',
                           (index_name, path, curr_time))
        for info in log.infos:
            self.__cur.execute(f'''INSERT INTO {curr_time} (inode, mtime, path, name, isfile) VALUES (?, ?, ?, ?, ?)''',
                               info.to_tuple())
        self.__con.commit()

    def list_logs(self, index_name: str) -> List[str]:
        log_names = self.__cur.execute('''SELECT log_name FROM info
                    WHERE index_name=? ORDER BY row_id''', (index_name, )).fetchall()
        log_names = [log_name[0] for log_name in log_names]
        return log_names

    def get_log(self, log_name: str) -> Log:
        logs = self.__cur.execute(
            f'''SELECT inode, mtime, path, name, isfile FROM {log_name}''').fetchall()
        log = Log(log_name)
        for elem in logs:
            log.add_info(Info(*elem))
        return log

    def overwrite_log(self, log_name: str, new_log: Log):
        self.__cur.execute(f'''DELETE FROM {log_name}''')
        for info in new_log.infos:
            self.__cur.execute(f'''INSERT INTO {log_name} (inode, mtime, path, name, isfile) VALUES (?, ?, ?, ?, ?)''',
                               info.to_tuple())
        self.__con.commit()

    def rem_log(self, log_name: str):
        self.__cur.execute(f'''DROP TABLE {log_name}''')
        self.__con.commit()

    # INDEX
    def get_path(self, index_name: str):
        path = self.__cur.execute('''SELECT path FROM info
                    WHERE index_name=?''', (index_name, )).fetchone()
        return path[0]

    def is_added(self, path: str = None, index_name: str = None) -> bool:
        '''Pass any of the parameter to check if it's already present in database.'''
        if path:
            exists = self.__cur.execute('SELECT * FROM info WHERE path=?',
                                        (path, )).fetchone()
            return bool(exists)
        if index_name:
            exists = self.__cur.execute('SELECT * FROM info WHERE index_name=?',
                                        (index_name, )).fetchone()
            return bool(exists)

    def list_indexes(self) -> List[str]:
        names = self.__cur.execute('''SELECT DISTINCT(index_name) FROM info
                    ORDER BY row_id''').fetchall()
        names = [name[0] for name in names]
        return names

    def rem_index(self, index_name: str):
        log_names = self.list_logs(index_name)
        for log_name in log_names:
            self.rem_log(log_name)
        self.__cur.execute(
            f'''DELETE FROM info WHERE index_name=?''', (index_name, ))
        self.__con.commit()

    # MISC
    def __create_info_table(self):
        self.__cur.execute('''CREATE TABLE IF NOT EXISTS info (
            row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            index_name TEXT,
            path TEXT,
            log_name TEXT
        )''')
        self.__con.commit()

    def __create_log_tables(self, table_name: str):
        statement = f'''CREATE TABLE IF NOT EXISTS {table_name} (
            row_id INTEGER PRIMARY KEY AUTOINCREMENT,
            inode TEXT UNIQUE,
            mtime INTEGER,
            path TEXT,
            name TEXT,
            isfile INTEGER
        )'''
        self.__cur.execute(statement)
        self.__con.commit()
