import unittest

from shared_tools.cache import _esc_key
from shared_tools.scraper_tools import *


class ScrapperTest(unittest.TestCase):

    def test(self):
        html = "https://stacksbystacks.com/test_file.txt"
        test_dir = "/home/gaffney/stacks-by-stacks/back-end/test_data"

        result = read_url_to_string(html, web_driver(), WriteCacher(test_dir))

        web_driver().close()

        # This is written on the test_file.
        self.assertTrue(result.find("ABC123") != -1)

        with open(os.path.join(test_dir, _esc_key(html)), "rb") as f:
            cache_contents = pickle.load(f)
        self.assertTrue(cache_contents.find("ABC123") != -1)
