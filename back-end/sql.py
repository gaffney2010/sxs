import functools
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import MySQLdb
import pandas as pd
import retrying

from sql_config import SQL_CONFIG

INF = 10000  # Must exceed the number of rows for every table.
NO_TABLES = 10  # For caching
NFL_TEAMS = 32

TEAM_CW_TABLE = "team_cw"
TEAM_TEXT_COLUMN = "team_text"
TEAM_ID_COLUMN = "team_id"


@functools.lru_cache(1)
def table_cache() -> Dict[str, pd.DataFrame]:
    """Hacky singleton"""
    return dict()


@functools.lru_cache(1)
def _sql_connection():
    """Connect to SQL with SQL_CONFIG settings."""
    return MySQLdb.connect(**SQL_CONFIG)


@retrying.retry(wait_random_min=0, wait_random_max=300,
                stop_max_attempt_number=3)
def _sql_query(query: str) -> List[Tuple]:
    """Low-level SQL query."""
    print(f"Query: {query}")

    sxsql = _sql_connection()
    cur = sxsql.cursor()
    cur.execute(query)
    return cur.fetchall()


@retrying.retry(wait_random_min=0, wait_random_max=100,
                stop_max_attempt_number=3)
def _sql_execute(command: str) -> None:
    """Low-level SQL execute."""
    print(f"Execute: {command}")

    sxsql = _sql_connection()
    sxsql.cursor().execute(command)
    sxsql.commit()


@functools.lru_cache(NO_TABLES)
def _column_names(table_name: str) -> List[str]:
    """Get the column names for a table as they are in SQL."""
    # Set up server
    column_query = f"select column_name from information_schema.columns where table_name='{table_name}';"
    return [x[0] for x in _sql_query(column_query)]


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
    _sql_execute(f"replace into {db}.{table_name} values ({value_clause});")


def pull_everything_from_table(table_name: str,
                               read_from_cache: bool = True) -> pd.DataFrame:
    if read_from_cache:
        if table_name in table_cache():
            return table_cache()[table_name]

    # Set up server
    sxsql = MySQLdb.connect(**SQL_CONFIG)

    # Get data
    data = list()
    for result in _sql_query(f"select * from {table_name};"):
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


print(_column_names("team_cw"))
# print(get_team_id("green bay"))
# print(get_team_id("packers"))
# print(get_team_id("green bay packers"))
# print(get_team_id("gb"))
