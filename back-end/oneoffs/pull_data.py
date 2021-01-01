from typing import Dict

from shared_types import *
from tools import sql

predictions = sql.query_df(f"""
    select      x.game_key,
                y.predicted_winner_id,
                w.score
    from        game x
    inner join  stack y
            on  x.game_key = y.game_key
    inner join  records w
            on  x.game_date=w.at_date and y.expert_id=w.expert_id
    where       x.home_score <> x.away_score;
""")

predictions.to_csv("predictions.csv")

games = sql.query_df(f"""
    select      x.*,
                y.team_1 as odd_team_1,
                y.money_line_1 as odd_ml_1,
                y.team_2 as odd_team_2,
                y.money_line_2 as odd_ml_2
    from        game x
    inner join  odd y
            on  x.game_key = y.game_key
    where       x.home_score <> x.away_score;
""")

def _winner_id(row: Dict) -> TeamId:
    if row["home_score"] == row["away_score"]:
        return -1
    if row["home_score"] > row["away_score"]:
        return row["home_team_id"]
    return row["away_team_id"]

games["winner_id"] = games.apply(_winner_id, axis=1)
games = games[["game_key", "winner_id", "odd_team_1", "odd_ml_1", "odd_team_2", "odd_ml_2"]]

games.to_csv("games.csv")
