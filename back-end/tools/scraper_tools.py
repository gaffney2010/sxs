""" These are some functions to aid in the scraping of a general webpage."""

import logging
import time
from typing import Optional

import retrying
import selenium.webdriver

from configs import *
from shared_types import *
from tools.cache import Cacher, memoize, TimedReadWriteCacher

DRIVER_DELAY_SEC = 3


def strip_white_space(x: str) -> str:
    x = x.strip().replace("\n", " ")
    # Remove consecutive whitespace
    result = list()
    mode = "TEXT"
    for ch in x:
        if mode == "WS":
            if ch != " ":
                mode = "TEXT"
                result.append(" ")
        if mode == "TEXT":
            if ch == " ":
                mode = "WS"
                continue
            result.append(ch)
    return "".join(result)


class WebDriver(object):
    """Used for convenient open and closing.

    This will handle closing for you, but will close as soon as the driver
    leaves scope.
    """

    def __init__(self):
        self._driver = None

    def __enter__(self):
        """We just need this, so that we can have the exit semantic."""
        return self

    def driver(self):
        """Get the main object, loading if necessary."""
        # Lazy load
        if self._driver is None:
            logging.debug("Initializing driver.")
            options = selenium.webdriver.FirefoxOptions()
            options.add_argument('--headless')
            self._driver = selenium.webdriver.Firefox(
                options=options,
                service_log_path="{}/geckodriver.log".format(LOG_DIR))
            logging.debug("Finished initializing driver.")
        return self._driver

    def __exit__(self, type, value, tb):
        """Clean-up on exit."""
        if self._driver:
            self._driver.quit()
        self._driver = None


def read_url_to_string(url: str, web_driver: WebDriver,
                       cacher: Optional[Cacher]) -> str:
    """ Read from a url and print to a string, after fully buffering.

    If errors after three tries, then will return an empty string.

    Args:
        url: The URL to read.
        web_driver: A web driver.
        cacher: A strategy for caching.

    Returns:
         The body of the resulting HTML in a flat string.
    """
    if cacher is None:
        # Default does nothing.
        cacher = Cacher()

    @memoize(url, cacher)
    # @swallow_error("")
    @retrying.retry(wait_random_min=200, wait_random_max=400,
                    stop_max_attempt_number=3)
    def read_url_to_string_helper(help_url):
        web_driver.driver().get(help_url)
        time.sleep(DRIVER_DELAY_SEC)
        return web_driver.driver().page_source

    return read_url_to_string_helper(url)


def one_day_read(url: Url) -> str:
    """Reads with a TimedReadWriteCacher with 1 day.

    This is the default option.  Handles opening and closing the driver.

    Args:
        url: The URL to read.

    Returns:
         The body of the resulting HTML in a flat string.
    """
    logging.info(f"Reading URL: {url}")
    raw_html_cacher = TimedReadWriteCacher(ttl=23)
    with WebDriver() as driver:
        page_text = read_url_to_string(url, driver, cacher=raw_html_cacher)
    logging.info("Finished pulling URL.")
    return page_text


def zero_day_read(url: Url) -> str:
    """Reads with a TimedReadWriteCacher with 1 day.

    This is the default option.  Handles opening and closing the driver.

    Args:
        url: The URL to read.

    Returns:
         The body of the resulting HTML in a flat string.
    """
    logging.info(f"Reading URL: {url}")
    with WebDriver() as driver:
        page_text = read_url_to_string(url, driver, cacher=None)
    logging.info("Finished pulling URL.")
    return page_text
