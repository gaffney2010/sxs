"""Script pull_nhl will pull games with start and end dates."""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

import logging
import pandas as pd
from typing import Iterator, Set

import bs4

from tools import game_key, scraper_tools, date_lib, sql
from shared_types import *

HR_URL = "https://www.hockey-reference.com/leagues/NHL_{}_games.html"


def get_html_for_dates(start: Date, end: Date) -> Iterator[str]:
    start_year, end_year = start // 10000, end // 10000
    # Some 20XX games will be in the 20(XX+1) season.
    for yr in range(start_year, end_year + 2):
        yield scraper_tools.one_day_read(HR_URL.format(yr))


def parse_df(df: pd.DataFrame, start: Date, end: Date,
             unique_games: Set[GameKey], safe_mode: bool) -> None:
    for _, row in df.iterrows():
        date = date_lib.full_parse_date(row["Date"])
        if date < start or date > end:
            continue

        away, home = row["Visitor"], row["Home"]
        away_id, home_id = sql.get_team_id(away), sql.get_team_id(home)
        gk = game_key.game_key(date, away_id, home_id)
        n = 1
        while gk in unique_games:
            n += 1
            gk = game_key.game_key(date, away_id, home_id, n)
            logging.debug("Added double header.")
        unique_games.add(gk)

        game_row = {
            "game_key": gk,
            "game_date": date,
            "play_status": "PAST" if date < date_lib.today() else "UPCOMING",
            "home_team_id": home_id,
            "away_team_id": away_id,
            "home_score": row["G.1"],
            "away_score": row["G"],
        }
        sql.add_row_to_table("Game", game_row, safe_mode=safe_mode)


def pull_nhl(start: Date, end: Date, safe_mode: bool = SAFE_MODE) -> None:
    for html in get_html_for_dates(start, end):
        soup = bs4.BeautifulSoup(html, features="html5lib")
        for table in soup.findAll("table", {"class": "sortable stats_table"}):
            table_html = f"<table>{table}</table>"
            unique_games = set()  # For double-headers
            for df in pd.read_html(table_html, flavor="bs4"):
                parse_df(df, start, end, unique_games, safe_mode)


# pull_nhl(20210113, 20210117)
