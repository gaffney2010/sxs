"""Scrapes game-level info into SQL table game

Schedule:
Daily at 4am
0 4 * * *
"""

#########################
# Logging logic
from local_config import SXS
LOG_FOLDER = f"{SXS}/back-end/logs/"

from datetime import datetime

now = datetime.now()
date = now.year * 10000 + now.month * 100 + now.day

import logging
logging.basicConfig(format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s", filename=LOG_FOLDER+str(date)+".log", level=logging.INFO)

#########################

from nfl_games import *

iso_year, iso_week = now.isocalendar()[0], now.isocalendar()[1]
logging.info(f"RUNNING ON: {iso_year}-{iso_week}")

if iso_year != 2020:
    error_msg = "Game scrapper out of bounds!  Not implemented for 2021."
    logging.exception(error_msg)
    raise NotImplementedError(error_msg)

# Update this week and last.
pull_week(iso_year, iso_week-37, prompt_on_miss=False)
pull_week(iso_year, iso_week-36, prompt_on_miss=False)
