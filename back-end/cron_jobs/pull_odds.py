"""Pull games

0 2 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

from scripts import pull_odds


pull_odds.run_odds_scraper(SAFE_MODE)
