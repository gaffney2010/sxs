"""Scrapes game-level info into SQL table game

Schedule:
weekly, monday at 6am
0 6 * * 1
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

import shutil

DB_NAME = "v1.db"

shutil.copyfile(src=f"{SXS}/data/localdb/{DB_NAME}", dst=f"{SXS}/data/backup_db/{data}_{DB_NAME}")
