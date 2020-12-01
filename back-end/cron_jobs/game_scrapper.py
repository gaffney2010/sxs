"""Scrapes game-level info into SQL table game

Schedule:
Daily at 4am
0 4 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from shared_tools.logger import configure_logging
configure_logging(SAFE_MODE)
################################################################################

from nfl_games import *

logging.info("==============")
logging.info("RUN GAMES SCRAPER")

now = datetime.now()
iso_year, iso_week = now.isocalendar()[0], now.isocalendar()[1]
logging.info(f"RUNNING ON: {iso_year}-{iso_week}")

if iso_year != 2020:
    error_msg = "Game scrapper out of bounds!  Not implemented for 2021."
    logging.exception(error_msg)
    raise NotImplementedError(error_msg)

# Update this week and last.
pull_week(iso_year, iso_week-37, prompt_on_miss=False)
pull_week(iso_year, iso_week-36, prompt_on_miss=False)
