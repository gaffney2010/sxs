"""Pull games

0 1 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging, log_section

configure_logging(SAFE_MODE)
################################################################################

from cron_jobs.consts import *
from scripts.scrapers import pull_nhl
from tools import date_lib


log_section("pull_nhl.py")

pull_nhl.pull_nhl(date_lib.today_plus(LOOK_BACK), date_lib.today_plus(LOOK_AHEAD), safe_mode=SAFE_MODE)
