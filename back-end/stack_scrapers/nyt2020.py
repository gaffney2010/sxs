"""This should scrape NYT reviews.  Works for 2020, maybe goes back.

URL like https://www.nytimes.com/2020/11/05/sports/football/nfl-picks-week-9.html

Can use NYT API to find articles.  I don't know how I will get past pay wall, I
may need to log in on Firefox.
"""
import logging  # Must be first
logging.basicConfig(format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s", level=logging.INFO)

import dateparser
import datetime
import re
from typing import Iterator

import attr
from bs4 import BeautifulSoup

from shared_tools.scraper_tools import *
from sql import *


@attr.s
class GameInfo(object):
    """All info I can pull from the game block, with nothing processed."""

    home_team: str = attr.ib()
    away_team: str = attr.ib()
    pick_clause: str = attr.ib()  # "<Team> <Spread>"
    body: str = attr.ib()


def read_games(text: str) -> Iterator[GameInfo]:
    """Extract basic info from the games from a single page.

    NYT reviews has 2 strong tags per game, and no other <strong> tags.  One
     for "X at Y" and one for "Pick: Z line".  The review body looks like:
     <strong>[X at Y]</strong>...</p><p>...</p>
     <p>[body]</p><p>(0+ times)...<strong>Pick:</strong> [Z line]</p>
    """
    # Split at the strong tags
    strong_splits = text.split("<strong")
    if len(strong_splits) % 2 == 0:
        raise ValueError("Expect even number of <strong> tags.")

    for split_i, split in enumerate(strong_splits):
        try:
            if split_i % 2 == 0:
                continue
            # This is a game block
            next_strong_ending = strong_splits[split_i + 1].split("</p>")[0]
            game_block = f"<strong{split}<strong{next_strong_ending}</p>"
            game_soup = BeautifulSoup(game_block, features="html.parser")

            teams = game_soup.strong.contents[0]
            away_team, home_team = teams.split(" at ")

            # Delete the first two and the last paragraph of the game_block
            ps = list(game_soup.find_all("p"))
            p_texts = list()
            for pi, p in enumerate(ps):
                if pi not in (0, 1, len(ps) - 1):
                    p_texts.append(p.text)
            body = " ".join(p_texts)

            pick_clause = game_block.split("</strong>")[-1].split("</p>")[0].strip()

            yield GameInfo(
                home_team=home_team,
                away_team=away_team,
                pick_clause=pick_clause,
                body=body,
            )
        except:
            pass


def read_article(text: str, link: str) -> None:
    # Get the author
    match = re.search(r"nytimes.com/by/([^\"]+)\"", text)
    author = " ".join(match.group(1).split("-"))
    expert_id = get_expert_id(author)

    # Get fetched date
    now = datetime.datetime.now()
    date = now.year * 10000 + now.month * 100 + now.day

    # Get latest date
    if text.find("Updated") != -1:
        # Look for "Updated <!-- -->Nov. 8, 2020</span>"
        pred = dateparser.parse(text.split("Updated <!-- -->")[1].split("</span>")[0])
        prediction_date = pred.year * 10000 + pred.month * 100 + pred.day
    else:
        # Look for "Published <!-- -->Nov. 8, 2020</span>"
        pred = dateparser.parse(text.split("Published <!-- -->")[1].split("</span>")[0])
        prediction_date = pred.year * 10000 + pred.month * 100 + pred.day


    for game in read_games(text):
        home_team_id = get_team_id(game.home_team)
        away_team_id = get_team_id(game.away_team)
        predicted_winner_id = get_team_id(game.pick_clause.split()[0])
        if (
            predicted_winner_id != home_team_id
            and predicted_winner_id != away_team_id
        ):
            raise ValueError(
                "Pick {} doesn't match either team {} or {}".format(
                    game.pick_clause.split()[0], game.home_team, game.away_team
                )
            )

        if game.pick_clause.find("-") != -1:
            spread_favorite = predicted_winner_id
            spread_amt = float(game.pick_clause.split("-")[-1])
        elif game.pick_clause.find("+") != -1:
            # Set spread_favorite to the non-predicted-winner
            spread_favorite = (
                away_team_id
                if predicted_winner_id == home_team_id
                else home_team_id
            )
            spread_amt = float(game.pick_clause.split("+")[-1])
        else:
            raise ValueError(
                f"Unexpected, pick clause malformed: {game.pick_clause}"
            )

        new_row = {
            "expert_id": expert_id,
            "expert_type": "HUMAN",
            "affiliate": "NYT",
            "prediction_date": prediction_date,
            "fetched_date": date,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "predicted_winner_id_with_spread": predicted_winner_id,
            "spread_favorite": spread_favorite,
            "spread_amount": spread_amt,
            "body": game.body,
            "link": link,
        }
        add_row_to_table("stack", new_row, safe_mode=True)


nyt_page = "https://www.nytimes.com/2020/11/05/sports/football/nfl-picks-week-9.html"
raw_html_cacher = TimedReadWriteCacher(directory=RAW_HTML_DIR, age_days=1)
with WebDriver() as driver:
    nfl_page_text = read_url_to_string(nyt_page, driver, cacher=raw_html_cacher)
read_article(nfl_page_text, nyt_page)
