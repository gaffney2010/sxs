import unittest

from shared_tools.cache import _transform_key
from shared_tools.scraper_tools import *


class ScrapperTest(unittest.TestCase):

    def test(self):
        html = "https://stacksbystacks.com/test_file.txt"
        test_dir = "/home/gaffney/stacks-by-stacks/back-end/test_data"

        with WebDriver() as driver:
            result = read_url_to_string(html, driver, WriteCacher(test_dir))

        # This is written on the test_file.
        self.assertTrue(result.find("ABC123") != -1)

        with open(_transform_key(html, test_dir), "rb") as f:
            cache_contents = pickle.load(f)
        self.assertTrue(cache_contents.find("ABC123") != -1)
