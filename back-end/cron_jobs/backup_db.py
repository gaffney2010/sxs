"""Backup the local DB file

Once a week.
30 0 * * 0
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = True
from tools.logger import configure_logging, log_section

configure_logging(SAFE_MODE)
################################################################################

import logging
import shutil

from configs import *
from tools import date_lib, sql

log_section("backup_db.py")

backup_location = f"{DROPBOX}/{DB_VERSION}_{date_lib.today()}.db"

shutil.copyfile(sql.LOCAL_DB, backup_location)
