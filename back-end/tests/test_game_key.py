import unittest
from collections import defaultdict
from typing import List, Tuple

import psycopg2
import testing.postgresql

from tools import game_key, sql


class TestConn(sql.SqlConnection):
    def __init__(self, engine):
        self._engine = engine

    def sql_query(self, query: str) -> List[Tuple]:
        cur = self._engine.cursor()
        cur.execute(query)
        self.columns = None  # Clear old.
        if cur.description:
            self.columns = [d[0] for d in cur.description]
        return cur.fetchall()


class GameKeyTest(unittest.TestCase):

    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.postgresql.dsn())
        conn.cursor().execute("""
            create table game (
                game_key varchar(255)
            );
        """)
        _1v3 = game_key.game_key(19990101, 1, 3, 1)
        _1v2_1 = game_key.game_key(19990101, 1, 2, 1)
        _1v2_2 = game_key.game_key(19990101, 1, 2, 2)
        conn.cursor().execute(f"""
            insert into game values ('{_1v3}'), ('{_1v2_1}'), ('{_1v2_2}');
        """)
        conn.commit()
        self.conn = TestConn(conn)

    def tearDown(self):
        self.postgresql.stop()

    def test_game_key_unique(self):
        gks = defaultdict(int)
        for i in range(1, 32):
            for j in range(1, 32):
                if i == j:
                    continue
                gks[game_key.game_key(1, i, j)] += 1

        for _, v in gks.items():
            self.assertEqual(v, 2)

    def test_get_unique(self):
        expected_key = game_key.game_key(19990101, 1, 3, 1)
        actual_key = game_key.get_unique_game_key(19990101, 1, 3,
                                                  conn=self.conn)
        self.assertEqual(actual_key, expected_key)

    def test_get_unique_fails_when_not_found(self):
        with self.assertRaises(game_key.NoHeaderException):
            game_key.get_unique_game_key(19990101, 2, 3, conn=self.conn)

    def test_get_unique_fails_when_not_unique(self):
        with self.assertRaises(game_key.DoubleHeaderException):
            game_key.get_unique_game_key(19990101, 1, 2, conn=self.conn)
