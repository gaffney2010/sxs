"""Script pull_nhl will pull games with start and end dates."""

################################################################################
# Logging logic, must come first
SAFE_MODE = True
from shared_tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

from shared_tools import scraper_tools
from shared_types import *


HR_URL = "https://www.hockey-reference.com/leagues/NHL_{}_games.html"


def get_html_for_dates(start: Date, end: Date)

def pull_nhl(start: Date, end: Date):


scraper_tools.one_day_read()