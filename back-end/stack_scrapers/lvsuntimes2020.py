"""Pull from site like:
https://lasvegassun.com/blogs/talking-points/2020/dec/03/vegas-odds-nfl-picks-against-spread-betting-week13/
"""

import datetime
from typing import List

import sql
from shared_tools import stack_tools
from shared_types import *


def _three_letter_month(month: int) -> str:
    if month == 1:
        return "jan"
    if month == 2:
        return "feb"
    if month == 3:
        return "mar"
    if month == 4:
        return "apr"
    if month == 5:
        return "may"
    if month == 6:
        return "jun"
    if month == 7:
        return "jul"
    if month == 8:
        return "aug"
    if month == 9:
        return "sep"
    if month == 10:
        return "oct"
    if month == 11:
        return "nov"
    if month == 12:
        return "dec"


def getter(period: Period) -> List[Url]:
    if period.year != 2020:
        raise NotImplementedError
    week_zero = datetime.date(2020, 9, 3)
    week_n = week_zero + datetime.timedelta(weeks=period.week)
    return ["http://lasvegassun.com/blogs/talking-points/{}/{}/{:02d}/vegas-odds-nfl-picks-against-spread-betting-week{}/".format(
        week_n.year, _three_letter_month(week_n.month), week_n.day, period.week
    )]


def scraper(
        text: PageText,
        link: Url,
        run_date: Date,
        period: Period,
        safe_mode: SafeMode,
) -> None:
    expert_name = text.split("<cite>")[1].split("</cite>")[0]
    expert_id = sql.get_expert_id(expert_name)

    prediction_date = stack_tools.full_parse_date(
        text.split("<p class=\"bypubdate\" itemprop=\"datePublished\">")[
            1].split(" | ")[0])

    headers, bodies = list(), list()
    words = text.replace(">", "> ").replace("<", " <").split()
    mode = "NORMAL"
    header, body = list(), list()
    for i, wi in enumerate(words):
        if mode == "NORMAL":
            if wi == "<strong>":
                s = " ".join(words[i:i + 10])
                if s.find("Twitter") != -1 or s.find("Entertainment:") != -1:
                    continue
                if s.find(" vs. ") == -1 and s.find(" at ") == -1:
                    continue
                mode = "HEADER"
                continue
        if mode == "HEADER":
            if wi == "</strong>":
                headers.append(" ".join(header))
                header = list()
                mode = "BODY"
                continue
            header.append(wi)
        if mode == "BODY":
            if wi == "<em>":
                continue
            if wi == "</em>":
                bodies.append(" ".join(body))
                body = list()
                mode = "NORMAL"
                continue
            body.append(wi)

    if len(headers) != len(bodies):
        raise Exception("Unexpected different size header/body")

    for header, body in zip(headers, bodies):
        s = header.split("</strong>")[0]
        mid = " at " if s.find(" vs. ") == -1 else " vs. "
        team_1 = " ".join(s.split(mid)[0].split()[:-1]).replace("&nbsp;", " ").strip()
        team_2 = s.split(mid)[1].replace("&nbsp;", " ").strip()
        away_team_name = team_2 if mid == " vs. " else team_1
        home_team_name = team_1 if mid == " vs. " else team_2
        predicted_winner_name = team_1
        away_team_id = sql.get_team_id(away_team_name)
        home_team_id = sql.get_team_id(home_team_name)
        predicted_winner_id = sql.get_team_id(predicted_winner_name)

        pick_clause = s.split(mid)[0].split()[-1]
        spread_favorite, spread_amt = stack_tools.spread_favorite_amt(
            pick_clause, predicted_winner_id, away_team_id, home_team_id)

        new_row = {
            "expert_id": expert_id,
            "affiliate": "LV Sun-Times",
            "prediction_date": prediction_date,
            "fetched_date": run_date,
            "game_date": sql.get_date_from_week_hometeam(period, home_team_id),
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "predicted_winner_id_with_spread": predicted_winner_id,
            "spread_favorite": spread_favorite,
            "spread_amt": spread_amt,
            "body": body,
            "link": link,
            "exclude": False,
        }
        sql.add_row_to_table("stack", new_row, safe_mode=safe_mode)
