"""Scrapes game-level info into SQL table game

Schedule:
every six hours
0 0 * * *
0 6 * * *
0 12 * * *
0 18 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from shared_tools.logger import configure_logging
configure_logging(SAFE_MODE)
################################################################################

import logging

import pull_odds

logging.info("==============")
logging.info("RUN ODDS SCRAPER")
pull_odds.run_odds_scraper(SAFE_MODE)
