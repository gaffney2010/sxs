"""This should scrape CBS reviews.  Works for 2020, maybe goes back.

URL like https://www.cbssports.com/nfl/picks/experts/against-the-spread/10/
"""
#########################
# Logging logic
SAFE_MODE = False

from local_config import SXS
LOG_FOLDER = f"{SXS}/back-end/logs/"

from datetime import datetime

now = datetime.now()
date = now.year * 10000 + now.month * 100 + now.day

import logging
if SAFE_MODE:
    # Print to screen
    logging.basicConfig(format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s", level=logging.INFO)
else:
    # Print to file
    logging.basicConfig(format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s", filename=LOG_FOLDER+str(date)+".log", level=logging.INFO)

#########################

import attr
import re

from bs4 import BeautifulSoup

from shared_tools.scraper_tools import *
from sql import *


def _clean(name: str) -> str:
    return name.replace("\n", " ").strip()


@attr.s
class Game(object):
    href: str = attr.ib()
    date: int = attr.ib()
    away_team: str = attr.ib()
    home_team: str = attr.ib()


def run_scraper(url: str, sample_page: str) -> str:
    soup = BeautifulSoup(sample_page, features="html.parser")
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
        blob = sample_page.split(gi.href)[1]
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
                "game_date": gi.date,
                "home_team_id": home_team_id,
                "away_team_id": get_team_id(gi.away_team),
                "predicted_winner_id_with_spread": predicted_winner_id,
                "spread_favorite": spread_favorite,
                "spread_amt": spread_amt,
                "link": url,
                "exclude": False,
            }
            add_row_to_table("stack", new_row, safe_mode=SAFE_MODE)


ALL_URLS = ["https://www.cbssports.com/nfl/picks/experts/against-the-spread/10/"]

# TODO(#29): Share this logic too.
raw_html_cacher = TimedReadWriteCacher(directory=RAW_HTML_DIR, age_days=1)
for url in ALL_URLS:
    logging.info(url)
    with WebDriver() as driver:
        page_text = read_url_to_string(url, driver, cacher=raw_html_cacher)
    run_scraper(url, page_text)
