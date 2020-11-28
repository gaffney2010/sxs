#########################
# Logging logic
SAFE_MODE = False

from local_config import SXS
LOG_FOLDER = f"{SXS}/back-end/logs/"

from datetime import datetime

now = datetime.now()
today = now.year * 10000 + now.month * 100 + now.day

import logging
if SAFE_MODE:
    # Print to screen
    logging.basicConfig(format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s", level=logging.INFO)
else:
    # Print to file
    logging.basicConfig(format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s", filename=LOG_FOLDER+str(today)+".log", level=logging.INFO)


################################################################################

from typing import List

from shared_tools.scraper_tools import *
from shared_types import *

@attr.s
class Scraper(object):
    getter: Callable[[Period], Url] = attr.ib()
    scraper: Callable[[PageText, Url, Date, Period, SafeMode], None] = attr.ib()


################################################################################
# This section defines specific scrapers.

from stack_scrapers import cbs2020
cbs_scraper = Scraper(getter=cbs2020.getter, scraper=cbs2020.scraper)

from stack_scrapers import nyt2020
nyt_scraper = Scraper(getter=nyt2020.getter, scraper=nyt2020.scraper)


################################################################################

def run_scrapers(scrapers: List[Scraper], periods: List[Period]) -> None:
    global SAFE_MODE
    global today

    for scraper in scrapers:
        for period in periods:
            raw_html_cacher = TimedReadWriteCacher(directory=RAW_HTML_DIR, age_days=1)
            url = scraper.getter(period)
            logging.info(url)
            with WebDriver() as driver:
                page_text = read_url_to_string(url, driver, cacher=raw_html_cacher)
            scraper.scraper(page_text, url, today, period, SAFE_MODE)

