from datetime import datetime
from typing import Tuple

import dateparser

from shared_types import *


def spread_favorite_amt(pick_clause, predicted_winner_id, away_team_id, home_team_id) -> Tuple[int, int]:
    if pick_clause.find("-") != -1:
        spread_favorite = predicted_winner_id
        spread_amt = float(pick_clause.split("-")[-1])
    elif pick_clause.find("+") != -1:
        # Set spread_favorite to the non-predicted-winner
        spread_favorite = (
            away_team_id
            if predicted_winner_id == home_team_id
            else home_team_id
        )
        spread_amt = float(pick_clause.split("+")[-1])
    elif pick_clause.find("pick") != -1:
        spread_favorite = predicted_winner_id
        spread_amt = 0
    else:
        raise ValueError(
            f"Unexpected, pick clause malformed: {pick_clause}"
        )
    return spread_favorite, spread_amt


# TODO: Move date functions to better file.
def full_parse_date(text: str) -> Date:
    """Runs date parser, AND converts to Date."""
    pred = dateparser.parse(text)
    return pred.year * 10000 + pred.month * 100 + pred.day


def today() -> Date:
    return int(datetime.today().strftime("%Y%m%d"))
