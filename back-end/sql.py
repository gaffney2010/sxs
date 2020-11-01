import functools
import logging
from enum import Enum
import sqlite3
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple

if sys.platform != "darwin":
    # Doesn't work on my mac.
    import MySQLdb
import pandas as pd

from sql_config import DB_VERSION, SQL_CONFIG

INF = 10000  # Must exceed the number of rows for every table.
NO_TABLES = 10  # For caching
NFL_TEAMS = 32
NO_RETRY = 3

TEAM_CW_TABLE = "team_cw"
TEAM_TEXT_COLUMN = "team_text"
TEAM_ID_COLUMN = "team_id"

LOCAL_DB = f"/home/gaffney/stacks-by-stacks/back-end/data/local_db/{DB_VERSION}.db"


@functools.lru_cache(1)
def table_cache() -> Dict[str, pd.DataFrame]:
    """Hacky singleton"""
    return dict()


class SqlConn(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SqlConn, cls).__new__(
                cls, *args, **kwargs)

            # Connect to SQL with SQL_CONFIG settings.
            logging.debug("Initializing new SqlConn.")
            if sys.platform != "darwin":
                cls._instance._mysql_conn = MySQLdb.connect(**SQL_CONFIG)
            cls._instance._sqlite_conn = sqlite3.connect(LOCAL_DB)

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

        raise(recent_exception)

    def sql_query(self, query: str) -> List[Tuple]:
        """Low-level SQL query.

        Reads from local (sqlite) database only.

        Args:
            query: The query to do the read.

        Returns:
            A list of tuples, which represent the fields in order.  Can use
                helper functions to join this with the column names.
        """
        logging.info(f"Query: {query}")

        cur = self._sqlite_conn.cursor()
        cur.execute(query)
        return cur.fetchall()

    def sql_execute(self, command: str) -> None:
        """Low-level SQL execute.

        This will get run both locally (sqlite) and remotely (mysql).

        Should always be idempotent, but we leave that to callers.

        Args:
            command: The statement to execute
        """
        logging.info(f"Execute: {command}")

        self._sqlite_conn.cursor().execute(command)
        self._sqlite_conn.commit()

        def execute_instructions():
            self._mysql_conn.cursor().execute(command)
            self._mysql_conn.commit()

        if sys.platform != "darwin":
            self._retry_mysql_with_reopen(execute_instructions)


@functools.lru_cache(NO_TABLES)
def _column_names(table_name: str) -> List[str]:
    """Get the column names for a table as they are in SQL."""
    # Set up server
    column_query = f"select column_name from information_schema.columns where table_name='{table_name}';"
    return [x[0] for x in SqlConn().sql_query(column_query)]


def _convert_field_to_sql(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, str):
        return f"\"{value}\""
    return str(value)


def add_row_to_table(table_name: str, values: Dict[str, Any]) -> None:
    """Add the given values to the table.

    Technically executes a replace, which will delete old values if the primary
    key already exists for the row.

    Args:
        table_name: The name of the table in the default DB.
        values: A dict where the keys are the row names.  Will ignore any
            invalid keys.
    """
    # Update cache
    if table_name in table_cache():
        table_cache()[table_name] = table_cache()[table_name].append(
            values, ignore_index=True)

    # Start building the SQL instruction
    values_strings = list()
    for column in _column_names(table_name):  # Canonical order
        value = None
        if column in values:
            value = values[column]
        values_strings.append(_convert_field_to_sql(value))
    value_clause = ", ".join(values_strings)
    db = SQL_CONFIG["db"]

    # Execute SQL instruction
    SqlConn().sql_execute(f"replace into {db}.{table_name} values ({value_clause});")


def pull_everything_from_table(table_name: str,
                               read_from_cache: bool = True) -> pd.DataFrame:
    if read_from_cache:
        if table_name in table_cache():
            return table_cache()[table_name]

    # Set up server
    sxsql = MySQLdb.connect(**SQL_CONFIG)

    # Get data
    data = list()
    for result in SqlConn().sql_query(f"select * from {table_name};"):
        data.append(
            {k: v for k, v in zip(_column_names(table_name), result)})

    # Convert to a pandas dataframe
    if len(data) == 0:
        # Handle the empty case special.
        result = pd.DataFrame(columns=_column_names(table_name))
    else:
        result = pd.DataFrame(data)

    table_cache()[table_name] = result
    return result


def _clean_text(txt: str) -> str:
    """Standard cleaning."""
    return txt.lower().strip()


def _get_team_id(team_text: str, cache: bool) -> Optional[int]:
    """Given a string that represents a team, find the ID.

    Searches known team texts.

    Args:
        team_text: Represents the team.
        cache: If to read from the cached version of TEAM_CW_TABLE.

    Returns:
        Our internal ID or None if key is not found.
    """
    cw = pull_everything_from_table(TEAM_CW_TABLE, read_from_cache=cache)
    filtered = cw[cw[TEAM_TEXT_COLUMN] == team_text]
    if filtered.empty:
        return None
    return filtered.iloc[0][TEAM_ID_COLUMN]


class CacheStrategy(Enum):
    # Read from the local cache only
    FROM_CACHE = 1
    # Read from the SQL table only
    FROM_TABLE = 2
    # Read from the SQL table if not in the cache.
    FROM_TABLE_ON_MISS = 3


# TODO: Specify an exception type.
def get_team_id(
        team_text: str,
        cache_strategy: CacheStrategy = CacheStrategy.FROM_TABLE_ON_MISS,
        prompt_on_miss: bool = True) -> int:
    """Given a string that represents a team, find the ID.

    Searches known team texts.  Caching strategy and prompt on miss describe how
    to handle cache misses.

    Args:
        team_text: Represents the team.
        cache_strategy: How to handle misses.
        prompt_on_miss: Ask the user to enter the team ID.  If they do, then
            will update the TEAM_CW table.

    Returns:
        Our internal ID.

    Raises:
        Exception: If the text is not known or prompt is not a team ID
    """
    team_text = _clean_text(team_text)

    if cache_strategy == CacheStrategy.FROM_CACHE:
        result = _get_team_id(team_text, True)
    if cache_strategy == CacheStrategy.FROM_TABLE:
        result = _get_team_id(team_text, False)
    if cache_strategy == CacheStrategy.FROM_TABLE_ON_MISS:
        result = _get_team_id(team_text, True)
        if not result:
            result = _get_team_id(team_text, False)

    if result:
        return result

    if prompt_on_miss:
        team_id = input(
            f"Unknown text representing team: {team_text}.  Enter team ID or 0 to fail:")
        team_id = int(team_id)
        if 1 <= team_id <= NFL_TEAMS:
            add_row_to_table(TEAM_CW_TABLE, {TEAM_TEXT_COLUMN: team_text,
                                             TEAM_ID_COLUMN: team_id})
            return team_id
        raise Exception(f"Unknown team ID: {team_id}.")

    raise Exception(f"Unknown text representing team: {team_text}.")


logging.debug(_column_names("team_cw"))
logging.debug(get_team_id("green bay"))
logging.debug(get_team_id("packers"))
logging.debug(get_team_id("green bay packers"))
logging.debug(get_team_id("gb"))
