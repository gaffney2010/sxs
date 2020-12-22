"""Script pull_nhl will pull CBS with start and end dates.

Ex. https://www.cbssports.com/nhl/expert-picks/20200807/
"""

import re

import bs4

from shared_types import *
from tools import date_lib, game_key, scraper_tools, sql


def pull_page(url: Url, date: Date) -> None:
    page_text = scraper_tools.one_day_read(url)
    soup = bs4.BeautifulSoup(page_text, features="html5lib")
    for row in soup.findAll("div", {"class": "picks-tr"}):
        if str(row).find("span") == -1:
            # Header row
            continue

        teams = list()
        for team in row.findAll("span", {"class": "team"}):
            teams.append(team.find("a").text)
        team_1, team_2 = teams

        team_1_id = sql.get_team_id(team_1)
        team_2_id = sql.get_team_id(team_2)

        gk = game_key.get_unique_game_key(date, team_1_id, team_2_id)

        pick = scraper_tools.strip_white_space(
            row.find("div", {"class": re.compile("^expert-spread")}).text)
        pred, line = pick.split(" ")

        stack = {
            "expert_id": sql.get_expert_id("CBS Sports Staff"),
            "affliate": "CBS",
            "game_key": gk,
            "predicted_winner_id": sql.get_team_id(pred),
            "money_line": int(line),
            "link": url,
            "fetched_date": date_lib.today(),
            "exclude": False,
        }
        print(stack)


pull_page("https://www.cbssports.com/nhl/expert-picks/20200807/", 20200807)
