################################################################################
# Logging logic, must come first
# SAFE_MODE = True
# from tools.logger import configure_logging
#
# configure_logging(SAFE_MODE)
################################################################################

import logging

from tools import sql


def _replace_nonish(x, replace_with=0):
    if x is None:
        return replace_with
    if x != x:
        return replace_with
    return x


def soft_translate():
    for table in sql.TIMED_TABLES:
        curr = sql.query_df(
            f"select ts from {table} order by 1 desc;",
            conn=sql.RemoteSqlConn(), silent_mode=True
        )
        if curr.shape[0] == 0:
            last_ts = 0
        else:
            last_ts = _replace_nonish(curr["ts"][0])
        for _, row in sql.pull_everything_from_table(table).iterrows():
            row_ts = _replace_nonish(row["ts"])
            if row_ts >= last_ts:
                sql.add_row_to_table(table, row.to_dict(),
                                     conn=sql.RemoteSqlConn(), silent_mode=True)


def hard_translate():
    # Need to manually first drop old tables, and run scripts to set up.
    for table in sql.ALL_TABLES:
        logging.debug(table)
        sql.batch_add_rows_to_table(
            table, sql.pull_everything_from_table(table),
            conn=sql.RemoteSqlConn()
        )
