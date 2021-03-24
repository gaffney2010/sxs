"""Run various scrapers

0 2 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging, log_section

configure_logging(SAFE_MODE)
################################################################################

from cron_jobs.consts import *
from scripts.scrapers import pull_david_mj, scrape_cbs, scrape_doc_sports, scrape_picks_and_parlays
from tools import date_lib

log_section("picks_and_parlays")
scrape_picks_and_parlays.pull_all_starting_with_page(
    pg_no=0,
    start=date_lib.today_plus(LOOK_BACK),
    end=date_lib.today_plus(LOOK_AHEAD),
    safe_mode=SAFE_MODE)

log_section("doc_sports")
scrape_doc_sports.pull_all_starting_with_page(
    pg_no=0,
    start=date_lib.today_plus(LOOK_BACK),
    end=date_lib.today_plus(LOOK_AHEAD),
    safe_mode=SAFE_MODE)

log_section("cbs")
scrape_cbs.pull_all_pages(
    start=date_lib.today_plus(LOOK_BACK),
    end=date_lib.today_plus(LOOK_AHEAD),
    safe_mode=SAFE_MODE)

log_section("david-mj")
pull_david_mj.pull_all_comments(
    start=date_lib.today_plus(LOOK_BACK),
    end=date_lib.today_plus(LOOK_AHEAD),
    safe_mode=SAFE_MODE)
