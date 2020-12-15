"""Pull from CFN page like:
https://collegefootballnews.com/2020/12/nfl-expert-picks-predictions-week-14-2020
"""

import datetime
from typing import List

from bs4 import BeautifulSoup

import sql
from shared_tools.stack_tools import full_parse_date
from shared_types import *


def getter(period: Period) -> List[Url]:
    if period.year != 2020:
        raise NotImplementedError
    week_zero = datetime.date(2020, 9, 2)
    week_n = week_zero + datetime.timedelta(weeks=period.week)
    return [
        "https://collegefootballnews.com/{}/{}/nfl-expert-picks-predictions-week-{}-{}/{}".format(
            week_n.year, week_n.month, period.week, period.year, i) for i in
        range(1, 10)]


def scraper(
        text: PageText,
        link: Url,
        run_date: Date,
        period: Period,
        safe_mode: SafeMode,
) -> None:
    bs = BeautifulSoup(text, features="html.parser")
    prediction_date = full_parse_date(
        bs.find("span", {"itemprop": "datePublished"}).text)

    games_plus = text.split("CONSENSUS PICK")
    for gp in games_plus[:-1]:
        game = gp.split("<h3>")[-1]
        game_desc = BeautifulSoup(
            game.split("</h3>")[0], features="html.parser").get_text()
        away_team_name, home_team_name = game_desc.split(" at ")
        home_team_id = sql.get_team_id(home_team_name)
        away_team_id = sql.get_team_id(away_team_name)
        odds_clause = gp.split("Line:")[1].split(",")[0].strip()
        spread_favorite, spread_amt = odds_clause.split(" -")
        spread_favorite = sql.get_team_id(spread_favorite)
        spread_amt = float(spread_amt)
        all_picks = gp.split("o/u")[1].replace("<", " <").replace(">", "> ")
        mode = "NORMAL"
        pickers, picks = list(), list()
        picker, pick = list(), list()
        for _, wi in enumerate(all_picks.split()):
            if mode == "NORMAL":
                if wi == "<strong>":
                    mode = "PICKER"
                    continue
            if mode == "PICKER":
                if wi == "</strong>":
                    pickers.append(" ".join(picker))
                    picker = list()
                    mode = "PICK"
                    continue
                picker.append(wi)
            if mode == "PICK":
                if wi.find("<br") != -1:
                    picks.append(" ".join(pick))
                    pick = list()
                    mode = "NORMAL"
                    continue
                pick.append(wi)

        for picker, pick in zip(pickers, picks):
            if pick.find("*") != -1:
                # These are not against the line
                continue

            predicted_winner_id = sql.get_team_id(pick.strip())
            expert_id = sql.get_expert_id(picker.split(",")[0])
            affiliate = picker.split(",")[0].strip()
            new_row = {
                "expert_id": expert_id,
                "affiliate": affiliate,
                "prediction_date": prediction_date,
                "fetched_date": run_date,
                "game_date": sql.get_date_from_week_hometeam(period,
                                                             home_team_id),
                "home_team_id": home_team_id,
                "away_team_id": away_team_id,
                "predicted_winner_id_with_spread": predicted_winner_id,
                "spread_favorite": spread_favorite,
                "spread_amt": spread_amt,
                "link": link,
                "exclude": False,
            }
            sql.add_row_to_table("stack", new_row, safe_mode=safe_mode)
