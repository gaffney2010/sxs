################################################################################
# Logging logic, must come first
SAFE_MODE = False
from shared_tools.logger import configure_logging
configure_logging(SAFE_MODE)
################################################################################

from typing import Callable, List

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

    now = datetime.now()
    today = now.year * 10000 + now.month * 100 + now.day

    for scraper in scrapers:
        for period in periods:
            raw_html_cacher = TimedReadWriteCacher(directory=RAW_HTML_DIR, age_days=1)
            url = scraper.getter(period)
            logging.info(url)
            with WebDriver() as driver:
                page_text = read_url_to_string(url, driver, cacher=raw_html_cacher)
            scraper.scraper(page_text, url, today, period, SAFE_MODE)

