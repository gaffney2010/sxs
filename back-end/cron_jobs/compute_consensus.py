"""Compute consensus

30 5 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging, log_section

configure_logging(SAFE_MODE)
################################################################################

from scripts import compute_consensus
from tools import date_lib


log_section("compute_consensus.py")

compute_consensus.compute_consensus(
    start=date_lib.today_plus(-2),
    end=date_lib.today_plus(2),
    safe_mode=SAFE_MODE)
