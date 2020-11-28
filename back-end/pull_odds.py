from datetime import datetime
import json
import os

import requests

from configs import ODDS_API_KEY
from local_config import SXS

RAW_ODDS_DIR = f"{SXS}/back-end/data/raw_odds"
URL = "https://api.the-odds-api.com/v3/odds/"

H2H_PARAMS = {"apiKey": ODDS_API_KEY, "sport": "americanfootball_nfl", "region": "us", "mkt": "h2h"}
SPREADS_PARAMS = {"apiKey": ODDS_API_KEY, "sport": "americanfootball_nfl", "region": "us", "mkt": "spreads"}


now = datetime.now()
date = 20201127 # now.year * 10000 + now.month * 100 + now.day
hour = 0 # now.hour
h2h_file = f"{date}-{hour}-h2h"
spreads_file = f"{date}-{hour}-spreads"


for params, file in [(H2H_PARAMS, h2h_file), (SPREADS_PARAMS, spreads_file)]:
    full_file = os.path.join(RAW_ODDS_DIR, file)
    if os.path.exists(full_file):
        with open(full_file, "r") as f:
            data = json.load(f)
    else:
        r = requests.get(url=URL, params=params)
        data = r.json()
        with open(full_file, 'w') as f:
            json.dump(data, f)
    if file == spreads_file:
        game_date = datetime.fromtimestamp(data["data"][0]["commence_time"])
        game_date_int = game_date.year * 10000 + game_date.month * 100 + game_date.day
        print(game_date_int)