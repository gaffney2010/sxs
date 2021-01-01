################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

from typing import Dict

import numpy as np

from shared_types import *
from tools import sql


class RecordCalcInterface(object):
    def __init__(self, expert_id: ExpertId, version: int, conn=None,
                 safe_mode: bool = SAFE_MODE):
        self.expert_id = expert_id
        self.version = version
        self.conn = conn
        if conn is None:
            self.conn = sql.SqlConn()
        self.safe_mode = safe_mode

    def load_stacks_and_games(self) -> None:
        raise NotImplementedError

    def calc_for_date_range(self, start: Date, end: Date) -> None:
        raise NotImplementedError


class RecordCalcV1(RecordCalcInterface):
    UNIT = 25
    FULLY_CREDIBLE = 200

    def __init__(self, expert_id: ExpertId):
        super().__init__(expert_id, version=1)
        self.stacks_and_games = None

    def _winner_id(self, row: Dict) -> TeamId:
        if row["home_score"] == row["away_score"]:
            return -1
        if row["home_score"] > row["away_score"]:
            return row["home_team_id"]
        return row["away_team_id"]

    def load_stacks_and_games(self) -> None:
        self.stacks_and_games = sql.query_df(f"""
            select      x.*, y.*,
                        z.team_1 as odd_team_1,
                        z.money_line_1 as odd_ml_1,
                        z.team_2 as odd_team_2,
                        z.money_line_2 as odd_ml_2
            from        game x
            left join   stack y
                    on  x.game_key = y.game_key
            inner join  odd z
                    on  x.game_key = z.game_key
            where       y.expert_id={self.expert_id}
            order       by x.game_date;""", conn=self.conn)

        self.stacks_and_games["winner_id"] = self.stacks_and_games.apply(
            self._winner_id, axis=1)

    def _baseline(self, n: int):
        return self.UNIT * np.sqrt(n) + n

    def _net(self, line: int, won: bool) -> float:
        bet_size = self.UNIT * np.sqrt(100 / abs(line))

        if not won:
            return -1 * bet_size

        if line > 0:
            return bet_size * line / 100

        return bet_size * 100 / abs(line)

    def _ml(self, row: Dict) -> int:
        if row["predicted_winner_id"] == row["odd_team_1"]:
            return row["odd_ml_1"]
        if row["predicted_winner_id"] == row["odd_team_2"]:
            return row["odd_ml_2"]
        raise Exception("???")

    def _score(self):
        # print(f"DEBUG: {self._baseline(len(self.deltas))}, {self.net}")
        return self._baseline(len(self.deltas)) + self.net

    def _clear_buffer(self, next_date, buffer) -> None:
        # Clears buffer in place.
        while buffer:
            item = buffer.pop()
            if item["predicted_winner_id"] and item["winner_id"] != -1:
                delta = self._net(self._ml(item),
                                  item["predicted_winner_id"] == item[
                                      "winner_id"])
                self.net += delta
                self.deltas.append(delta)
                if len(self.deltas) > self.FULLY_CREDIBLE:
                    # Subtract game on backend.
                    self.net -= self.deltas[0]
                    self.deltas = self.deltas[1:]

        # Record for the date.
        record = {
            "expert_id": self.expert_id,
            "at_date": next_date,
            "score": int(self._score()),
        }
        sql.add_row_to_table("records", record, safe_mode=self.safe_mode)

    # TODO: Use start/end
    def calc_for_date_range(self, start: Date, end: Date) -> None:
        if self.stacks_and_games is None:
            # raise Exception("Must run load_stacks_and_games first.")
            # There's no reason to not just do it here.
            self.load_stacks_and_games()

        self.deltas = list()
        self.n = 0
        self.net = 0
        last_date = 0
        buffer = list()
        for _, row in self.stacks_and_games.iterrows():
            next_date = row["game_date"]
            if next_date != last_date:
                self._clear_buffer(next_date, buffer)
                assert (len(buffer) == 0)

            last_date = next_date
            buffer.append(row)
        # TODO: Post for future dates...


for i in range(1, 15):
    if i in [10, 13]:
        # Don't know why this is empty...
        continue
    RecordCalcV1(i).calc_for_date_range(0, 99999999)
