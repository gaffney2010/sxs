import traceback
from typing import Callable, List

from shared_tools.scraper_tools import *
from shared_types import *


@attr.s
class Scraper(object):
    name: str = attr.ib()
    getter: Callable[[Period], List[Url]] = attr.ib()
    scraper: Callable[[PageText, Url, Date, Period, SafeMode], None] = attr.ib()


################################################################################
# This section defines specific scrapers.

from stack_scrapers import cbs2020

cbs_scraper = Scraper(name="CBS", getter=cbs2020.getter,
                      scraper=cbs2020.scraper)

from stack_scrapers import nyt2020

nyt_scraper = Scraper(name="NYT", getter=nyt2020.getter,
                      scraper=nyt2020.scraper)

from stack_scrapers import lvsuntimes2020

lvsuntimes_scraper = Scraper(name="LVST", getter=lvsuntimes2020.getter,
                             scraper=lvsuntimes2020.scraper)

from stack_scrapers import cfn2020

cfn_scraper = Scraper(name="CFN", getter=cfn2020.getter,
                      scraper=cfn2020.scraper)

ALL_SCRAPERS = [
    cbs_scraper,
    nyt_scraper,
    lvsuntimes_scraper,
    cfn_scraper,
]


################################################################################

def run_scrapers(scrapers: List[Scraper], periods: List[Period],
                 safe_mode: bool = True) -> None:
    now = datetime.now()
    today = now.year * 10000 + now.month * 100 + now.day

    for scraper in scrapers:
        urls = list()
        for period in periods:
            try:
                raw_html_cacher = TimedReadWriteCacher(directory=RAW_HTML_DIR,
                                                       age_days=1)
                urls += scraper.getter(period)
            except:
                logging.error(
                    "Unhandled exception for scraper: {} in period: {}".format(
                        scraper.name, str(period)))
                logging.error(traceback.format_exc())

        for url in urls:
            try:
                logging.info(url)
                with WebDriver() as driver:
                    page_text = read_url_to_string(url, driver,
                                                   cacher=raw_html_cacher)
                scraper.scraper(page_text, url, today, period, safe_mode)
            except:
                logging.error(
                    "Unhandled exception for scraper: {} in url: {}".format(
                        scraper.name, url))
                logging.error(traceback.format_exc())


def run_all_known_scrapers_for_period(period: Period, safe_mode: bool) -> None:
    global ALL_SCRAPERS
    run_scrapers(ALL_SCRAPERS, [period], safe_mode=safe_mode)
