import functools
import pandas as pd

from MySQLdb import _mysql

from sql_config import SQL_CONFIG

INF = 10000  # Must exceed the number of rows for every table.
NO_TABLES = 10  # For caching

TEAM_CW_TABLE = "team_cw"
TEAM_TEXT_COLUMN = "team_text"
TEAM_ID_COLUMN = "team_id"


@functools.lru_cache(NO_TABLES)
def _pull_everything_from_table(table_name: str) -> pd.DataFrame:
    # Set up server
    sxsql = _mysql.connect(**SQL_CONFIG)

    # Get column names
    sxsql.query(
        f"select column_name from information_schema.columns where table_name='{table_name}';")
    column_name_results = sxsql.use_result()
    column_names = [x[0].decode() for x in
                    column_name_results.fetch_row(maxrows=INF)]

    # Get data
    data = list()
    sxsql.query(
        f"select * from {table_name};")
    results = sxsql.use_result()
    for result in results.fetch_row(maxrows=INF):
        result_values = [v.decode() for v in result]
        data.append({k: v for k, v in zip(column_names, result_values)})

    # Convert to a pandas dataframe
    return pd.DataFrame(data)


def _clean_text(txt: str) -> str:
    """Standard cleaning."""
    return txt.lower().strip()


# TODO: Specify an exception type.
def get_team_id(team_text: str) -> int:
    """Given a string that represents a team, find the ID.

    Searches known team texts.

    Args:
        team_text: Represents the team.

    Returns:
        Our internal ID.

    Raises:
        Exception: If the text is not known.
    """
    cw = _pull_everything_from_table(TEAM_CW_TABLE)

    filtered = cw[cw[TEAM_TEXT_COLUMN]==team_text]
    if filtered.empty:
        raise Exception(f"Unknown text: {team_text}.")

    return filtered[TEAM_ID_COLUMN][0]


print(get_team_id("packers"))
