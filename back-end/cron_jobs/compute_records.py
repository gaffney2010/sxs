"""Compute records

0 5 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging, log_section

configure_logging(SAFE_MODE)
################################################################################

from scripts import compute_records
from tools import date_lib


log_section("compute_records.py")

compute_records.compute_v1_records_for_all(
    start=date_lib.today_plus(-1),
    end=date_lib.today_plus(1),
    safe_mode=SAFE_MODE)
