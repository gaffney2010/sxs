import unittest

from tools import scraper_tools


class StripWhiteSpaceTest(unittest.TestCase):

    def test_trim(self):
        self.assertEqual(scraper_tools.strip_white_space("  ABC "), "ABC")

    def test_consecutive_ws(self):
        self.assertEqual(scraper_tools.strip_white_space("ABC    DEF G  HI"),
                         "ABC DEF G HI")
