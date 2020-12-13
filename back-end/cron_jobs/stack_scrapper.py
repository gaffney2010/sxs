"""Scrapes "stacks" or experts

Schedule:
Daily at 5am
0 5 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from shared_tools.logger import configure_logging
configure_logging(SAFE_MODE)
################################################################################

from datetime import datetime
import logging

from all_scrapers import run_all_known_scrapers_for_period
from shared_types import *

logging.info("==============")
logging.info("RUN STACK SCRAPER")

now = datetime.now()
iso_year, iso_week = now.isocalendar()[0], now.isocalendar()[1]
logging.info(f"RUNNING ON: {iso_year}-{iso_week-37}")

if iso_year != 2020:
    error_msg = "Game scrapper out of bounds!  Not implemented for 2021."
    logging.exception(error_msg)
    raise NotImplementedError(error_msg)

# Update this week and last.
run_all_known_scrapers_for_period(Period(iso_year, iso_week-36), SAFE_MODE)