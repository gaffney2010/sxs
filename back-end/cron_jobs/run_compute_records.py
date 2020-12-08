"""Scrapes game-level info into SQL table game

Schedule:
weekly, monday at 7am
0 7 * * 1
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from shared_tools.logger import configure_logging
configure_logging(SAFE_MODE)
################################################################################

from compute_records import *

logging.info("==============")
logging.info("RUN COMPUTE RECORDS")
compute_records(v1_score, safe_mode=SAFE_MODE)
