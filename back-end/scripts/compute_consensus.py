################################################################################
# Logging logic, must come first
# SAFE_MODE = False
# from tools.logger import configure_logging
#
# configure_logging(SAFE_MODE)
################################################################################

from collections import defaultdict
from typing import List, Optional

from shared_types import *
from tools import sql


@attr.s
class ScoreStackValue(object):
    predicted_winner: TeamId = attr.ib()
    score: int = attr.ib()


def v1_consensus(values: List[ScoreStackValue]) -> Optional[TeamId]:
    """Simple spread winner weighted by score."""

    def _score(x):
        if x > 200:
            return 2
        return 1

    pick_weights = defaultdict(float)
    total_weight = 0
    for value in values:
        score = _score(value.score)
        pick_weights[value.predicted_winner] += score
        total_weight += score

    if total_weight < 2:
        return

    team_by_score = [(score, team) for team, score in pick_weights.items()]
    team_by_score.sort()
    return team_by_score[-1][1]


def compute_consensus(start: Date, end: Date, safe_mode=SAFE_MODE,
                      calc=v1_consensus):
    score_stacks = sql.query_df(f"""
        select      x.game_key,
                    x.predicted_winner_id,
                    y.score
        from        stack x
        inner join  records y
        on          x.expert_id = y.expert_id
        where       x.prediction_date >= {start} and x.prediction_date < {end}
    """)

    records = defaultdict(list)
    for _, row in score_stacks.iterrows():
        records[row["game_key"]].append(ScoreStackValue(
            predicted_winner=row["predicted_winner_id"],
            score=row["score"]))

    for gk, v in records.items():
        consensus = calc(v)
        if consensus is not None:
            cc = {
                "game_key": gk,
                "consensus_id": consensus
            }
            sql.add_row_to_table("consensus", cc, safe_mode=safe_mode)


# compute_consensus(0, 99999999)
