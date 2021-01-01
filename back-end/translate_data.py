import enum
import logging
from typing import Callable, List, Tuple

import MySQLdb

from configs import *

TIMED_TABLES = ["game", "team_cw", "stack", "odd", "records"]
ALL_TABLES = ["expert", "expert_cw", "team"] + TIMED_TABLES

NO_RETRY = 3


class RemoteSqlConn(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(RemoteSqlConn, cls).__new__(cls, *args,
                                                              **kwargs)

            # Connect to SQL with SQL_CONFIG settings.
            cls._instance._mysql_conn = MySQLdb.connect(**SQL_CONFIG)
            cls._instance.columns = None

        return cls._instance

    def _retry_mysql_with_reopen(self, f: Callable):
        """Retry, opening _conn between."""
        recent_exception = None
        for _ in range(NO_RETRY):
            try:
                return f()
            except Exception as e:
                recent_exception = e
                logging.debug("Initializing new RemoteSqlConn.")
                self._mysql_conn = MySQLdb.connect(**SQL_CONFIG)

        raise (recent_exception)

    def sql_query(self, query: str) -> List[Tuple]:
        logging.info(f"Query: {query}")

        cur = self._mysql_conn.cursor()
        cur.execute(query)
        self.columns = None  # Clear old.
        if cur.description:
            self.columns = [d[0] for d in cur.description]
        return cur.fetchall()

    def sql_execute(self, command: str, safe_mode: bool = False) -> None:
        logging.info(f"Execute: {command}")

        if safe_mode:
            # In this case, print only.
            return

        def execute_instructions():
            self._mysql_conn.cursor().execute(command)
            self._mysql_conn.commit()

        self._retry_mysql_with_reopen(execute_instructions)


class TranslationType(enum.Enum):
    SOFT = 1
    HARD = 2


def soft_translate():
    for table in TIMED_TABLES:
        

def hard_translate():
    pass


def translate(type: TranslationType):
    if type == TranslationType.SOFT:
        soft_translate()
    elif type == TranslationType.HARD:
        hard_translate()
    else:
        raise Exception("UNKNOWN TranslationType encountered.")
