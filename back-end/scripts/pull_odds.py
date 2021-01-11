################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

import json
import os
from datetime import datetime

import numpy as np
import requests

from configs import *
from tools import game_key, sql

RAW_ODDS_DIR = f"{SXS}/back-end/data/raw_odds"
URL = "https://api.the-odds-api.com/v3/odds/"

ODDS_TABLE = "odd"

H2H_PARAMS = {"apiKey": ODDS_API_KEY, "sport": "icehockey_nhl", "region": "us",
              "mkt": "h2h", "oddsFormat": "american"}


def run_odds_scraper(safe_mode: bool) -> None:
    now = datetime.now()
    date = now.year * 10000 + now.month * 100 + now.day
    hour = now.hour

    full_file = os.path.join(RAW_ODDS_DIR, f"{date}-{hour}")
    if os.path.exists(full_file):
        with open(full_file, "r") as f:
            data = json.load(f)
    else:
        r = requests.get(url=URL, params=H2H_PARAMS)
        data = r.json()
        with open(full_file, 'w') as f:
            json.dump(data, f)

    for datum in data["data"]:
        game_date = datetime.fromtimestamp(datum["commence_time"])
        game_date_int = game_date.year * 10000 + game_date.month * 100 + game_date.day

        teams = datum["teams"]
        team_inds = [sql.get_team_id(x) for x in teams]

        gk = game_key.get_unique_game_key(game_date_int, team_inds[0],
                                          team_inds[1])

        ml_1, ml_2 = list(), list()
        for site in datum["sites"]:
            odd_pair = site["odds"]["h2h"]
            if len(odd_pair) != 2:
                # Includes tie odds
                continue
            ml_1.append(odd_pair[0])
            ml_2.append(odd_pair[1])

        new_row = {
            "game_key": gk,
            "pull_date": date,
            "pull_hour": hour,
            "team_1": team_inds[0],
            "money_line_1": int(np.mean(ml_1)),
            "team_2": team_inds[1],
            "money_line_2": int(np.mean(ml_2)),
        }
        sql.add_row_to_table(ODDS_TABLE, new_row, safe_mode=safe_mode)


run_odds_scraper(SAFE_MODE)
