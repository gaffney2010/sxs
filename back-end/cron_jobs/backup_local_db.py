"""Scrapes game-level info into SQL table game

Schedule:
weekly, monday at 6am
0 6 * * 1
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from shared_tools.logger import configure_logging
configure_logging(SAFE_MODE)
################################################################################

from datetime import datetime
import logging

import shutil

from configs import SXS


logging.info("==============")
logging.info("RUN LOCAL_DB BACKUP")

now = datetime.now()
date = now.year * 10000 + now.month * 100 + now.day

DB_NAME = "v1.db"

shutil.copyfile(src=f"{SXS}/back-end/data/local_db/{DB_NAME}", dst=f"{SXS}/back-end/data/backup_db/{date}_{DB_NAME}")
