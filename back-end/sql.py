import functools
import logging
import sqlite3
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

if sys.platform != "darwin":
    # Doesn't work on my mac.
    import MySQLdb
import pandas as pd

from configs import DB_VERSION, SQL_CONFIG
from local_config import SXS
from shared_types import *

LOCAL_DB = f"{SXS}/back-end/data/local_db/{DB_VERSION}.db"

INF = 10000  # Must exceed the number of rows for every table.
NO_TABLES = 10  # For caching
NFL_TEAMS = 32
NO_RETRY = 3

TEAM_CW_TABLE = "team_cw"
TEAM_ID_TABLE = "team"
TEAM_TEXT_COLUMN = "team_text"
TEAM_ID_COLUMN = "team_id"
EXPERT_CW_TABLE = "expert_cw"
EXPERT_ID_TABLE = "expert"
EXPERT_TEXT_COLUMN = "expert_text"
EXPERT_ID_COLUMN = "expert_id"


@functools.lru_cache(1)
def table_cache() -> Dict[str, pd.DataFrame]:
    """Hacky singleton"""
    return dict()


class SqlConn(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SqlConn, cls).__new__(cls, *args, **kwargs)

            # Connect to SQL with SQL_CONFIG settings.
            logging.debug("Initializing new SqlConn.")
            if sys.platform != "darwin":
                cls._instance._mysql_conn = MySQLdb.connect(**SQL_CONFIG)
            cls._instance._sqlite_conn = sqlite3.connect(LOCAL_DB)
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
                logging.debug("Initializing new SqlConn.")
                self._mysql_conn = MySQLdb.connect(**SQL_CONFIG)

        raise (recent_exception)

    def sql_query(self, query: str) -> List[Tuple]:
        """Low-level SQL query.

        Reads from local (sqlite) database only.

        As a side-effect, this sets columns to the column names.  This allows
        the function to be more general than table reads.

        Args:
            query: The query to do the read.

        Returns:
            A list of tuples, which represent the fields in order.  Can use
                helper functions to join this with the column names.
        """
        logging.info(f"Query: {query}")

        cur = self._sqlite_conn.cursor()
        cur.execute(query)
        self.columns = None  # Clear old.
        if cur.description:
            self.columns = [d[0] for d in cur.description]
        return cur.fetchall()

    def sql_execute(self, command: str, safe_mode: bool = False) -> None:
        """Low-level SQL execute.

        This will get run both locally (sqlite) and remotely (mysql).

        Should always be idempotent, but we leave that to callers.

        Args:
            command: The statement to execute
            safe_mode: If true, don't actually make any changes to the table.
        """
        logging.info(f"Execute: {command}")

        if safe_mode:
            # In this case, print only.
            return

        self._sqlite_conn.cursor().execute(command)
        self._sqlite_conn.commit()

        def execute_instructions():
            self._mysql_conn.cursor().execute(command)
            self._mysql_conn.commit()

        if sys.platform != "darwin":
            self._retry_mysql_with_reopen(execute_instructions)


def _get_columns_for_table(table: str) -> List[str]:
    SqlConn().sql_query(f"select * from {table} limit 1")
    return SqlConn().columns


def _convert_field_to_sql(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


def add_row_to_table(
    table_name: str, values: Dict[str, Any], safe_mode: bool = False, conn=None
) -> None:
    """Add the given values to the table.

    Technically executes a replace, which will delete old values if the primary
    key already exists for the row.

    Args:
        table_name: The name of the table in the default DB.
        values: A dict where the keys are the row names.  Will ignore any
            invalid keys.
        safe_mode: If true, don't actually make any changes to the table.
        conn: If set use for reads.  Otherwise use default.
    """
    if conn is None:
        conn = SqlConn()

    # Update cache
    if table_name in table_cache():
        table_cache()[table_name] = table_cache()[table_name].append(
            values, ignore_index=True
        )

    # Start building the SQL instruction
    column_strings, values_strings = list(), list()
    for column, value in values.items():
        column_strings.append(column)
        values_strings.append(_convert_field_to_sql(value))
    column_clause = ", ".join(column_strings)
    value_clause = ", ".join(values_strings)

    # Execute SQL instruction
    conn.sql_execute(
        f"replace into {table_name} ({column_clause}) values ({value_clause});",
        safe_mode=safe_mode,
    )


def pull_everything_from_table(
    table_name: str, read_from_cache: bool = True, conn=None
) -> pd.DataFrame:
    """Pulls the entire thing at once.

    Args:
        table_name: The table to read
        read_from_cache: If true read from local variable
        conn: If set use for reads.  Otherwise use default.

    Returns:
        A dataframe with the data.
    """
    if conn is None:
        conn = SqlConn()

    if read_from_cache:
        if table_name in table_cache():
            return table_cache()[table_name]

    # Get data
    data = list()
    for result in conn.sql_query(f"select * from {table_name};"):
        assert len(conn.columns) == len(result)
        data.append({k: v for k, v in zip(conn.columns, result)})

    # Convert to a pandas dataframe
    if len(data) == 0:
        # Handle the empty case special.
        result = pd.DataFrame(columns=conn.columns)
    else:
        result = pd.DataFrame(data)

    table_cache()[table_name] = result
    return result


def _clean_text(txt: str) -> str:
    """Standard cleaning."""
    return txt.lower().replace(",", "").strip()


def _get_id(
    lookup_value: str,
    cw_table: str,
    text_column: str,
    id_column: str,
    cache: bool,
) -> Optional[int]:
    """Given a string that represents a team, find the ID.

    Searches known team texts.

    Args:
        lookup_value: The value that we want to find the ID for.
        cw_table: Name of cross-walk table to use.
        text_column: Name of the column with the lookupable values.
        id_column: Name of the column with the IDs.
        cache: If to read from the cached version of TEAM_CW_TABLE.

    Returns:
        Our internal ID or None if key is not found.
    """
    cw = pull_everything_from_table(cw_table, read_from_cache=cache)
    filtered = cw[cw[text_column] == lookup_value]
    if filtered.empty:
        return None
    return filtered.iloc[0][id_column]


def _get_or_prompt_id(
    lookup_value: str,
    id_table: str,
    cw_table: str,
    text_column: str,
    id_column: str,
    id_type: str,
    prompt_on_miss: bool = True,
) -> int:
    """Given a string, lookup the ID.

    Searches the passed table name.  If missed from local cache, look up on
    remote table, then potentially prompt on miss.

    Args:
        lookup_value: The value that we want to find the ID for.
        id_table: The source of truth for IDs.  Creates new row if new ID is
            entered.
        cw_table: Name of cross-walk table to use.
        text_column: Name of the column with the lookupable values.
        id_column: Name of the column with the IDs.
        id_type: What we're pulling, for use in error messages.
        prompt_on_miss: Ask the user to enter the team ID.  If they do, then
            will update the TEAM_CW table.

    Returns:
        Our internal ID.

    Raises:
        ValueError: If the text is not known or prompt is not a team ID
    """
    lookup_value = _clean_text(lookup_value)

    # Pull from remote on miss
    result = _get_id(lookup_value, cw_table, text_column, id_column, cache=True)
    if not result:
        result = _get_id(
            lookup_value, cw_table, text_column, id_column, cache=False
        )

    if result:
        return result

    if prompt_on_miss:
        new_cw_row = {text_column: lookup_value}  # For CW
        new_id_row = {text_column: lookup_value}  # For id_table
        id_table_needs_update = False
        known_ids = pull_everything_from_table(id_table)[id_column]

        # Get ID from user
        id = input(
            "Unknown text representing {}: {}.  Enter {} ID or 0 to fail or {} for new ID:".format(
                id_type, lookup_value, id_type, max(known_ids) + 1
            )
        )
        id = int(id)
        if id <= 0:
            raise ValueError(f"Unknown {id_type} ID: {id}.")
        new_cw_row[id_column] = id
        new_id_row[id_column] = id

        # Try to find in ID table, and create new row on miss.
        if id not in known_ids:
            logging.info(f"Unknown ID {id}.")
            id_table_needs_update = True
            for column in _get_columns_for_table(id_table):
                if column in (id_column, text_column):
                    continue
                value = input(f"Enter value for {column}:")
                new_id_row[column] = value

        # Keep all writes at the end, so that a fail above will not write any.
        add_row_to_table(cw_table, new_cw_row)
        if id_table_needs_update:
            add_row_to_table(id_table, new_id_row)
        logging.info(f"Saving {id_type} {lookup_value} with ID {id}.")

        # TODO(#25): Return the entire row from the ID table.
        return id

    raise ValueError(f"Unknown text representing team: {lookup_value}.")


def get_team_id(team_text: str, prompt_on_miss: bool = True) -> int:
    """Given a string that represents a team, find the ID."""
    return _get_or_prompt_id(
        lookup_value=team_text,
        cw_table=TEAM_CW_TABLE,
        id_table=TEAM_ID_TABLE,
        text_column=TEAM_TEXT_COLUMN,
        id_column=TEAM_ID_COLUMN,
        id_type="team",
        prompt_on_miss=prompt_on_miss,
    )


def get_expert_id(expert_text: str, prompt_on_miss: bool = True) -> int:
    """Given a string that represents a team, find the ID."""
    return _get_or_prompt_id(
        lookup_value=expert_text,
        cw_table=EXPERT_CW_TABLE,
        id_table=EXPERT_ID_TABLE,
        text_column=EXPERT_TEXT_COLUMN,
        id_column=EXPERT_ID_COLUMN,
        id_type="expert",
        prompt_on_miss=prompt_on_miss,
    )


def get_date_from_week_hometeam(period: Period, hometeam: int) -> int:
    results = SqlConn().sql_query(
        "select game_date from game where home_team_id={} and season={} and week={}".format(
            hometeam, period.year, period.week
        )
    )
    assert len(results) == 1
    assert len(results[0]) == 1
    return results[0][0]
