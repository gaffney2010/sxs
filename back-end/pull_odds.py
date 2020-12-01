import json
import os
from datetime import datetime

import numpy as np
import requests

from configs import ODDS_API_KEY
from sql import *

RAW_ODDS_DIR = f"{SXS}/back-end/data/raw_odds"
URL = "https://api.the-odds-api.com/v3/odds/"

H2H_PARAMS = {"apiKey": ODDS_API_KEY, "sport": "americanfootball_nfl",
              "region": "us", "mkt": "h2h"}
SPREADS_PARAMS = {"apiKey": ODDS_API_KEY, "sport": "americanfootball_nfl",
                  "region": "us", "mkt": "spreads"}

now = datetime.now()
date = 20201127  # now.year * 10000 + now.month * 100 + now.day
hour = 0  # now.hour

for params, type, get_from_odds in [
    (H2H_PARAMS, "h2h", lambda odds: odds["h2h"]),
    (SPREADS_PARAMS, "spread", lambda odds: odds["spreads"]["points"])]:
    full_file = os.path.join(RAW_ODDS_DIR, f"{date}-{hour}-{type}")
    if os.path.exists(full_file):
        with open(full_file, "r") as f:
            data = json.load(f)
    else:
        r = requests.get(url=URL, params=params)
        data = r.json()
        with open(full_file, 'w') as f:
            json.dump(data, f)

    game_date = datetime.fromtimestamp(data["data"][0]["commence_time"])
    game_date_int = game_date.year * 10000 + game_date.month * 100 + game_date.day

    home_team = data["data"][0]["home_team"]
    teams = data["data"][0]["teams"]
    home_team_id = get_team_id(home_team)

    home_team_index = 0 if teams[0] == home_team else 1
    away_team_index = 1 - home_team_index

    odd_home, odd_away = list(), list()
    for site in data["data"][0]["sites"]:
        odd_pair = get_from_odds(site["odds"])
        odd_home.append(float(odd_pair[home_team_index]))
        odd_away.append(float(odd_pair[away_team_index]))
    odds_home = np.mean(odd_home)
    odds_away = np.mean(odd_away)

    odds_type = type.upper()
