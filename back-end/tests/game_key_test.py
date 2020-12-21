from collections import defaultdict
import unittest

from shared_tools import game_key


class GameKeyTest(unittest.TestCase):

    def test_game_key_unique(self):
        gks = defaultdict(int)
        for i in range(1, 32):
            for j in range(1, 32):
                if i == j:
                    continue
                gks[game_key.game_key(1, i, j)] += 1

        for _, v in gks.items():
            self.assertEqual(v, 2)
