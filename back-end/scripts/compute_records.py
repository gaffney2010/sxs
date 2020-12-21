"""Records will naturally evolve.  So I will make new functions with each new
scoring method.  That way I can compare old models if need be."""

from collections import defaultdict
import numpy as np
from typing import Callable, List, Tuple

import sql

STACK_TABLE = "stack_with_outcomes"


def _row_record(row) -> int:
    if row["predicted_winner_id"]:
        if row["home_score"] == row["away_score"]:
            return 0
        winner_id = row["home_team_id"] if row["home_score"] > row["away_score"] else row["away_team_id"]
        return 1 if winner_id == row["predicted_winner_id"] else -1
    if row["predicted_winner_id_with_spread"]:
        actual_diff = row["home_score"] - row["away_score"]
        line_diff = row["spread_amt"]
        if row["spread_favorite"] != row["home_team_id"]:
            line_diff *= -1
        if actual_diff == line_diff:
            return 0
        home_team_won = actual_diff > line_diff
        home_team_chosen = row["predicted_winner_id_with_spread"] == row["home_team_id"]
        return 1 if home_team_won == home_team_chosen else -1
    return 0


def v1_score(stack_record: List[Tuple[int, int]]) -> int:
    """Compute score for player.

    Net number of predictions correct + 3 * sqrt(# predictions), out of last 900
    Then normalize by 1000/180, and round.

    stack_record: Record (+/- 1) by game date.
    """
    rel_record = [x[1] for x in sorted(stack_record)[-900:]]
    return int((np.sum(rel_record) + 3*np.sqrt(len(rel_record))) * 1000/180)


def compute_records(scorer: Callable[[List[Tuple[int, int]]], int], safe_mode: bool) -> None:
    df = sql.pull_everything_from_table(STACK_TABLE)
    df["record"] = df.apply(_row_record, axis=1)
    stack_records = defaultdict(list)
    for _, row in df.iterrows():
        stack_records[row["expert_id"]].append((row["game_date"], row["record"]))
    for stack, record in stack_records.items():
        sql.add_row_to_table("records", {"expert_id": int(stack), "score": scorer(record)}, safe_mode=safe_mode)
