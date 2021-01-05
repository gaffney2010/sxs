################################################################################
# Logging logic, must come first
SAFE_MODE = True
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

import enum
import logging

from tools import sql


class TranslationType(enum.Enum):
    SOFT = 1
    HARD = 2


def soft_translate():
    for table in sql.TIMED_TABLES:
        curr = sql.query_df(f"select ts from {table} order by 1 desc;",
                            conn=sql.RemoteSqlConn())
        if curr.shape[0] == 0:
            last_ts = 0
        else:
            last_ts = curr["ts"][0] or 0
        for _, row in sql.pull_everything_from_table(table).iterrows():
            if row["ts"] >= last_ts:
                sql.add_row_to_table(table, row.to_dict(),
                                     conn=sql.RemoteSqlConn())


def hard_translate():
    # Need to first drop old tables, and run scripts to set up.
    for table in sql.ALL_TABLES:
        logging.debug(table)
        sql.batch_add_rows_to_table(table,
                                    sql.pull_everything_from_table(table),
                                    conn=sql.RemoteSqlConn())


def translate(type: TranslationType):
    if type == TranslationType.SOFT:
        soft_translate()
    elif type == TranslationType.HARD:
        hard_translate()
    else:
        raise Exception("UNKNOWN TranslationType encountered.")


translate(TranslationType.HARD)
