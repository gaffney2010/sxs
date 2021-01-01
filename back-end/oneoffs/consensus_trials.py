from collections import defaultdict
import numpy as np
from typing import Dict, List

from shared_types import *
from tools import sql

INF = 999999


predictions = sql.query_df(f"""
    select      x.game_key,
                y.expert_id,
                y.predicted_winner_id,
                w.score
    from        game x
    inner join  stack y
            on  x.game_key = y.game_key
    inner join  records w
            on  x.game_date=w.at_date and y.expert_id=w.expert_id
    where       x.home_score <> x.away_score;
""")


preds_by_game = defaultdict(list)
for _, pred in predictions.iterrows():
    preds_by_game[pred["game_key"]].append(pred)


def consensus(rows: List[Dict], B: float, D: int, W: int, T: int) -> TeamId:
    ### Trial logic
    # for row in rows:
    #     if row["expert_id"] == 14:
    #         return row["predicted_winner_id"]
    # raise Exception("No CBS")

    def _score(x):
        if x > T:
            return 1+B
        return 1

    pick_weights = defaultdict(float)
    total_weight = 0
    for row in rows:
        score = _score(row["score"])
        pick_weights[row["predicted_winner_id"]] += score
        total_weight += score

    if total_weight < W:
        return

    best_k, best_v = None, -INF
    worst_k, worst_v = None, INF
    num_teams = 0
    for k, v in pick_weights.items():
        num_teams += 1
        if v > best_v:
            best_k, best_v = k, v
        if v < worst_v:
            worst_k, worst_v = k, v

    if num_teams == 1:
        # Dumb corner case
        worst_v = 0

    if best_v-worst_v >= D:
        return best_k


def big_run(B=1, D=1, W=1, T=100):
    my_picks = dict()
    for k, v in preds_by_game.items():
        try:
            pick = consensus(v, B, D, W, T)
            if pick is not None:
                my_picks[k] = pick
        except:
            pass


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


    # TODO: Share these
    def _winner_id(row: Dict) -> TeamId:
        if row["home_score"] == row["away_score"]:
            return -1
        if row["home_score"] > row["away_score"]:
            return row["home_team_id"]
        return row["away_team_id"]

    def _ml(row: Dict, pick: TeamId) -> int:
        if pick == row["odd_team_1"]:
            return row["odd_ml_1"]
        if pick == row["odd_team_2"]:
            return row["odd_ml_2"]
        raise Exception("???")


    total_laid, total_net = 0, 0
    for _, game in games.iterrows():
        if game["game_key"] not in my_picks:
            continue

        pick = my_picks[game["game_key"]]

        ml = _ml(game, pick)

        laid = np.sqrt(100/abs(ml))
        total_laid += laid

        # TODO: Share this
        if _winner_id(game) != pick:
            total_net -= laid
        else:
            if ml > 0:
                total_net += laid * ml / 100
            else:
                total_net += laid * 100 / abs(ml)

    return total_net/total_laid

print(big_run(D=1, W=3, T=250))
