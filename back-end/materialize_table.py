################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

from tools import sql


def mat():
    sql.RemoteSqlConn().sql_execute("truncate table swsws_table;")
    sql.batch_add_rows_to_table(
        "swsws_table",
        sql.pull_everything_from_table(
            "stacks_with_stacks_with_stacks", conn=sql.RemoteSqlConn()
        ),
        conn=sql.RemoteSqlConn(),
        silent_mode=True,
    )
