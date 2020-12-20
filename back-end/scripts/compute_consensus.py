from typing import List

import attr

from shared_types import Date, TeamId
import sql


score_stacks = sql.query_df("""
    select      x.game_date, x.home_team_id, x.away_team_id,
                x.predicted_winner_id_with_spread as predicted_winner,
                y.score
    from        stack x
    inner join  records y
    on          x.expert_id = y.expert_id
""")

@attr.s(frozen=True)
class ScoreStackKey(object):
    game_date: Date = attr.ib()
    home_team_id: TeamId = attr.ib()
    away_team_id: TeamId = attr.ib()

@attr.s
class ScoreStackValue(object):
    predicted_winner: TeamId = attr.ib()
    score: int = attr.ib()

def v1_consensus(key: ScoreStackKey, values: List[ScoreStackValue]) -> TeamId:
    """Simple spread winner weighted by score."""
