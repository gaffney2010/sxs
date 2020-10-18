""" These are some functions to aid in the scraping of a general webpage."""
import functools

import retrying
import selenium.webdriver

from shared_tools.logger import *

DRIVER_DELAY_SEC = 3
WebDriver = Any  # TODO


@functools.lru_cache(1)
def web_driver() -> WebDriver:
    """ Loads up a Firefox webdriver."""
    options = selenium.webdriver.FirefoxOptions()
    options.add_argument('--headless')
    return selenium.webdriver.Firefox(
        options=options,
        service_log_path="{}/geckodriver.log".format(LOG_DIR))


def close_driver() -> None:
    web_driver().quit()


def read_url_to_string(url: str, web_driver: WebDriver,
                       cacher: Optional[Cacher],
                       error_logger: Optional[ErrorLogger] = None) -> str:
    """ Read from a url and print to a string, after fully buffering.

    If errors after three tries, then will return an empty string.

    Args:
        url: The URL to read.
        web_driver: A web driver.
        cacher: A strategy for caching.
        error_logger: A function that takes strings and outputs to a log or
            screen.

    Returns:
         The body of the resulting HTML in a flat string.
    """
    if cacher is None:
        # Default does nothing.
        cacher = Cacher()

    @memoize(url, cacher)
    @swallow_error("", error_logger=error_logger)
    @retrying.retry(wait_random_min=200, wait_random_max=400,
                    stop_max_attempt_number=3)
    def read_url_to_string_helper(help_url):
        web_driver.get(help_url)
        time.sleep(DRIVER_DELAY_SEC)
        return web_driver.page_source

    return read_url_to_string_helper(url)
