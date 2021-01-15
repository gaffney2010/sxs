"""We keep this as _test, because we don't want to run this in every environment."""

import pickle
import unittest

from configs import *
from tools import cache
from tools import scraper_tools


class ScrapperTest(unittest.TestCase):

    def test(self):
        html = "https://stacksbystacks.com/test_file.txt"
        test_dir = f"{SXS}/back-end/test_data"

        with scraper_tools.WebDriver() as driver:
            result = scraper_tools.read_url_to_string(html, driver, cache.WriteCacher(test_dir))

        # This is written on the test_file.
        self.assertTrue(result.find("ABC123") != -1)

        with open(cache._transform_key(html, test_dir), "rb") as f:
            cache_contents = pickle.load(f)
        self.assertTrue(cache_contents.find("ABC123") != -1)
