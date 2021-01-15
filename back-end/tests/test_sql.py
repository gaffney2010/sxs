import unittest
from typing import List, Tuple
from unittest.mock import patch

import pandas as pd
import psycopg2
import testing.postgresql

from tools import sql


class TestConn(sql.SqlConnection):
    def __init__(self, engine):
        self._engine = engine
        self.queries = list()
        self.executions = list()

    def sql_query(self, query: str) -> List[Tuple]:
        self.queries.append(query)

        cur = self._engine.cursor()
        cur.execute(query)
        self.columns = None  # Clear old.
        if cur.description:
            self.columns = [d[0] for d in cur.description]
        return cur.fetchall()

    def sql_execute(self, command: str, safe_mode: bool = False) -> None:
        self.executions.append(command)

        self._engine.cursor().execute(command)
        self._engine.commit()


class BatchAddRowsToTableTest(unittest.TestCase):

    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.postgresql.dsn())
        self.conn = TestConn(conn)

    def tearDown(self):
        self.postgresql.stop()

    def test_batch_add_rows_to_table(self):
        # First build the table that we will dump data into.
        self.conn.sql_execute("""
            create table XYZ (
                a int,
                b varchar(255)
            );
        """)

        # Add the values
        table_name = "XYZ"
        values_df = pd.DataFrame({"a": [1, 2, 3], "b": ["hi", "T.J.", "test"]})
        sql.batch_add_rows_to_table(table_name, values_df, conn=self.conn,
                                    replace=False)

        # Check the values
        pd.testing.assert_frame_equal(
            sql.query_df("select * from XYZ;", conn=self.conn), values_df)

    def test_safe_mode_checks_invalid_columns(self):
        # First build the table that we will dump data into.
        self.conn.sql_execute("""
            create table XYZ (
                a int,
                b varchar(255)
            );
        """)

        table_name = "XYZ"
        values_df = pd.DataFrame({"a": [1, 2, 3], "c": ["hi", "T.J.", "test"]})
        with self.assertRaisesRegex(Exception, "Column c is not valid."):
            sql.batch_add_rows_to_table(table_name, values_df, safe_mode=True,
                                        conn=self.conn, replace=False)

    def test_non_safe_mode_ignores_invalid_columns(self):
        # First build the table that we will dump data into.
        self.conn.sql_execute("""
            create table XYZ (
                a int,
                b varchar(255)
            );
        """)

        table_name = "XYZ"
        values_df = pd.DataFrame({"a": [1, 2, 3], "c": ["hi", "T.J.", "test"]})
        sql.batch_add_rows_to_table(table_name, values_df, conn=self.conn,
                                    replace=False)

        pd.testing.assert_frame_equal(
            sql.query_df("select * from XYZ;", conn=self.conn),
            pd.DataFrame({"a": [1, 2, 3]}))

    def test_adds_timestamp(self):
        # First build the table that we will dump data into.
        self.conn.sql_execute("""
            create table stack (
                a int,
                b varchar(255),
                ts int
            );
        """)

        table_name = "stack"  # This is a timed table
        values_df = pd.DataFrame({"a": [1, 2, 3], "b": ["hi", "T.J.", "test"]})
        sql.batch_add_rows_to_table(table_name, values_df, conn=self.conn,
                                    replace=False)

        fetched_table = sql.query_df("select * from stack;", conn=self.conn)

        self.assertListEqual(list(fetched_table.columns), ["a", "b", sql.TS])
        for v in fetched_table[sql.TS]:
            self.assertGreater(v, 0)

    # def test_cache(self):
    #     # First build the table that we will dump data into.
    #     self.conn.sql_execute("""
    #         create table XYZ (
    #             a int,
    #             b varchar(255)
    #         );
    #     """)
    #
    #     table_name = "XYZ"
    #     values_df = pd.DataFrame({"a": [1, 2, 3], "b": ["hi", "T.J.", "test"]})
    #     sql.batch_add_rows_to_table(table_name, values_df, conn=self.conn, replace=False)
    #
    #     cache = sql.table_cache()
    #
    #     self.assertTrue("XYZ" in cache)


class BatchAddRowsToTableTest(unittest.TestCase):

    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.postgresql.dsn())
        self.conn = TestConn(conn)

    def tearDown(self):
        self.postgresql.stop()

    def test_add_row_to_table(self):
        # First build the table that we will dump data into.
        self.conn.sql_execute("""
            create table XYZ (
                a int,
                b varchar(255)
            );
        """)

        table_name = "XYZ"
        new_row = {"a": 100, "b": "one hundred"}
        sql.add_row_to_table(table_name, new_row, conn=self.conn, replace=False)

        fetched_table = sql.query_df("select * from XYZ;", conn=self.conn)

        pd.testing.assert_frame_equal(fetched_table, pd.DataFrame([new_row]))


class QueryDfTest(unittest.TestCase):

    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.postgresql.dsn())
        self.conn = TestConn(conn)

    def tearDown(self):
        self.postgresql.stop()

    def test_empty_table(self):
        # First build the table that we will dump data into.
        self.conn.sql_execute("""
            create table XYZ (
                a int,
                b varchar(255)
            );
        """)

        pd.testing.assert_frame_equal(
            sql.query_df("select * from XYZ;", conn=self.conn),
            pd.DataFrame(columns=["a", "b"]))

    # Other cases are tested through other tests.


class SqlExistsTest(unittest.TestCase):

    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.postgresql.dsn())
        self.conn = TestConn(conn)

        self.conn.sql_execute("""
            create table XYZ (
                a int
            );
        """)
        self.conn.sql_execute("""
            insert into XYZ values (1), (1), (2);
        """)

    def tearDown(self):
        self.postgresql.stop()

    def test_does_exist(self):
        self.assertTrue(sql.sql_exists("select * from XYZ where a=1;",
                                       conn=self.conn))
        self.assertTrue(sql.sql_exists("select * from XYZ where a=2;",
                                       conn=self.conn))

    def test_does_not_exist(self):
        self.assertFalse(sql.sql_exists("select * from XYZ where a=3;",
                                        conn=self.conn))


class PullEverythingTest(unittest.TestCase):

    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.postgresql.dsn())
        self.conn = TestConn(conn)

    def tearDown(self):
        self.postgresql.stop()

    def test_pull_everything_from_table(self):
        # Prep data
        self.conn.sql_execute("""
            create table XYZ (
                a int,
                b varchar(255)
            );
        """)
        table_name = "XYZ"
        values_df = pd.DataFrame({"a": [1, 2, 3], "b": ["hi", "T.J.", "test"]})
        sql.batch_add_rows_to_table(table_name, values_df, conn=self.conn,
                                    replace=False)

        fetched_table = sql.pull_everything_from_table("XYZ", conn=self.conn)

        pd.testing.assert_frame_equal(fetched_table, values_df)


class GetTeamIdTest(unittest.TestCase):

    def setUp(self):
        self.postgresql = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.postgresql.dsn())
        self.conn = TestConn(conn)

        self.conn.sql_execute(f"""
            create table {sql.TEAM_CW_TABLE} (
                {sql.TEAM_TEXT_COLUMN} varchar(255),
                {sql.TEAM_ID_COLUMN} int,
                ts int
            );
        """)
        self.conn.sql_execute(f"""
            insert into {sql.TEAM_CW_TABLE} values
            ('lions', 1, 0), ('tigers', 2, 0), ('bears', 3, 0);
        """)  # Oh my
        self.conn.sql_execute(f"""
            create table {sql.TEAM_ID_TABLE} (
                {sql.TEAM_ID_COLUMN} int,
                short_name varchar(255)
            );
        """)
        self.conn.sql_execute(f"""
            insert into {sql.TEAM_ID_TABLE} values
            (1, 'L'), (2, 'T'), (3, 'B');
        """)  # Oh my

    def tearDown(self):
        self.postgresql.stop()

    def test_get_team_id_finds_id(self):
        self.assertEqual(
            sql.get_team_id("tigers", prompt_on_miss=False, conn=self.conn), 2)

    def test_get_team_id_ignores_case(self):
        self.assertEqual(
            sql.get_team_id("TiGeRs", prompt_on_miss=False, conn=self.conn), 2)

    def test_missing_id_without_prompt_fails(self):
        with self.assertRaisesRegex(ValueError,
                                    "Unknown text representing team: wizards."):
            self.assertEqual(sql.get_team_id("wizards", prompt_on_miss=False,
                                             conn=self.conn), 2)

    @patch("time.time")
    @patch("tools.sql.stack_input")
    def test_missing_id_with_prompt(self, mock_input, mock_time):
        mock_input.return_value = 1
        mock_time.return_value = 0

        result = sql.get_team_id("Wizards", prompt_on_miss=True, conn=self.conn,
                                 test_mode=True)

        self.assertEqual(result, 1)
        mock_input.assert_called_once_with(
            "Unknown text representing team: wizards.  Enter team ID or 0 to fail or 4 for new ID:")

        pd.testing.assert_frame_equal(
            sql.pull_everything_from_table(sql.TEAM_CW_TABLE), pd.DataFrame(
                {sql.TEAM_TEXT_COLUMN: ["lions", "tigers", "bears", "wizards"],
                 sql.TEAM_ID_COLUMN: [1, 2, 3, 1],
                 "ts": [0, 0, 0, 0]}))

    @patch("time.time")
    @patch("tools.sql.stack_input")
    def test_missing_id_with_prompt_n_minus_one(self, mock_input, mock_time):
        """We do a special test because of an error."""
        mock_input.return_value = 3
        mock_time.return_value = 0

        result = sql.get_team_id("Wizards", prompt_on_miss=True, conn=self.conn,
                                 test_mode=True)

        self.assertEqual(result, 3)
        mock_input.assert_called_once_with(
            "Unknown text representing team: wizards.  Enter team ID or 0 to fail or 4 for new ID:")

        pd.testing.assert_frame_equal(
            sql.pull_everything_from_table(sql.TEAM_CW_TABLE), pd.DataFrame(
                {sql.TEAM_TEXT_COLUMN: ["lions", "tigers", "bears", "wizards"],
                 sql.TEAM_ID_COLUMN: [1, 2, 3, 3],
                 "ts": [0, 0, 0, 0]}))

    @patch("time.time")
    @patch("tools.sql.stack_input")
    def test_add_new_team(self, mock_input, mock_time):
        """We do a special test because of an error."""
        mock_input.side_effect = [4, "W"]
        mock_time.return_value = 0

        sql.get_team_id("Wizards", prompt_on_miss=True, conn=self.conn,
                                 test_mode=True)

        pd.testing.assert_frame_equal(
            sql.pull_everything_from_table(sql.TEAM_CW_TABLE), pd.DataFrame(
                {sql.TEAM_TEXT_COLUMN: ["lions", "tigers", "bears", "wizards"],
                 sql.TEAM_ID_COLUMN: [1, 2, 3, 4],
                 "ts": [0, 0, 0, 0]}))

        pd.testing.assert_frame_equal(
            sql.pull_everything_from_table(sql.TEAM_ID_TABLE), pd.DataFrame(
                {sql.TEAM_ID_COLUMN: [1, 2, 3, 4],
                 "short_name": ["L", "T", "B", "W"]}))


# I don't test get_expert_id, because it's similar enough.
