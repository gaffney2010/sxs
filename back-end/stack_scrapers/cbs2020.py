"""This should scrape CBS reviews.  Works for 2020, maybe goes back.

URL like https://www.cbssports.com/nfl/picks/experts/against-the-spread/10/
"""

import re

from bs4 import BeautifulSoup

from sql import *


def _clean(name: str) -> str:
    return name.replace("\n", " ").strip()


@attr.s
class Game(object):
    href: str = attr.ib()
    date: int = attr.ib()
    away_team: str = attr.ib()
    home_team: str = attr.ib()


def getter(period: Period) -> str:
    if period.year != 2020:
        raise NotImplementedError
    return f"https://www.cbssports.com/nfl/picks/experts/against-the-spread/{period.week}/"


def scraper(
    page_text: PageText,
    url: Url,
    run_date: Date,
    period: Period,
    safe_mode: SafeMode,
) -> None:
    soup = BeautifulSoup(page_text, features="html.parser")
    experts = list()
    for name_div in soup.findAll("div", class_="AuthorHeadshotAndName-name"):
        experts.append(_clean(name_div.text))

    games = list()
    for link in soup.findAll(href=re.compile(r"_\w+@\w+")):
        href = link["href"]
        link_info = re.search(r"NFL_(\d\d\d\d\d\d\d\d)_(\w+)@(\w+)", href)
        date, away_team, home_team = (
            int(link_info.group(1)),
            link_info.group(2),
            link_info.group(3),
        )
        games.append(
            Game(href=href, date=date, away_team=away_team, home_team=home_team)
        )

    for i, gi in enumerate(games):
        blob = page_text.split(gi.href)[1]
        if i < len(games) - 1:
            blob = blob.split(games[i + 1].href)[0]

        blob_soup = BeautifulSoup(blob, features="html.parser")
        for expert, p in zip(
            experts,
            blob_soup.findAll("p", class_=re.compile("TableExpertPicks-pick")),
        ):
            pick_clause = _clean(p.text)
            predicted_winner_id = get_team_id(pick_clause.split(" ")[0])

            home_team_id = get_team_id(gi.home_team)
            away_team_id = get_team_id(gi.away_team)

            # TODO: Share this functionality.
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
            else:
                raise Exception(f"Malformed pick_clause: {pick_clause}")

            new_row = {
                "expert_id": get_expert_id(expert),
                "affiliate": "CBS",
                "fetched_date": run_date,
                "game_date": gi.date,
                "home_team_id": home_team_id,
                "away_team_id": get_team_id(gi.away_team),
                "predicted_winner_id_with_spread": predicted_winner_id,
                "spread_favorite": spread_favorite,
                "spread_amt": spread_amt,
                "link": url,
                "exclude": False,
            }
            add_row_to_table("stack", new_row, safe_mode=safe_mode)
