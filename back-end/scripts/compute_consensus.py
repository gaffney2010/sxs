from collections import defaultdict
from typing import List, Optional

import attr

from shared_types import Date, TeamId
from tools import sql

INF = 999999


score_stacks = sql.query_df("""
    select      x.game_date, x.home_team_id, x.away_team_id,
                x.predicted_winner_id_with_spread as predicted_winner,
                y.score
    from        stack x
    inner join  records y
    on          x.expert_id = y.expert_id
""")

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
    for row in rows:
        score = _score(row["score"])
        pick_weights[row["predicted_winner_id"]] += score
        total_weight += score

    if total_weight < 2:
        return

    team_by_score = [(score, team) for team, score in pick_weights.items()]
    team_by_score.sort()
    return team_by_score[-1][1]
