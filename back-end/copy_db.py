import argparse

from sql import *


# TODO: I can probably share some logic.
class TablePuller(object):
    """A pull-only version, where version can be specified."""

    def __init__(self, version):
        self._sqlite_conn = sqlite3.connect(
            f"{SXS}/back-end/data/local_db/{version}.db")
        self.columns = None

    def sql_query(self, query: str) -> List[Tuple]:
        cur = self._sqlite_conn.cursor()
        cur.execute(query)
        self.columns = None  # Clear old.
        if cur.description:
            self.columns = [d[0] for d in cur.description]
        return cur.fetchall()


class TablePusher(object):
    """A version that only writes remotely to avoid a circular write."""

    def __init__(self):
        self._mysql_conn = MySQLdb.connect(**SQL_CONFIG)

    def _retry_mysql_with_reopen(self, f: Callable):
        recent_exception = None
        for _ in range(NO_RETRY):
            try:
                return f()
            except Exception as e:
                recent_exception = e
                self._mysql_conn = MySQLdb.connect(**SQL_CONFIG)

        raise (recent_exception)

    def sql_execute(self, command: str) -> None:
        def execute_instructions():
            self._mysql_conn.cursor().execute(command)
            self._mysql_conn.commit()

        self._retry_mysql_with_reopen(execute_instructions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DB Copier")
    parser.add_argument("--version", required=True)
    parser.add_argument("--table", required=True)
    args = parser.parse_args()

    in_conn = TablePuller(args.version)
    out_conn = TablePusher()
    for _, row in pull_everything_from_table(args.table,
                                             conn=in_conn).iterrows():
        add_row_to_table(args.table, row.to_dict(), conn=out_conn)
