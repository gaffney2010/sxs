"""This should scrape NYT reviews.  Works for 2020, maybe goes back.

URL like https://www.nytimes.com/2020/11/05/sports/football/nfl-picks-week-9.html

Can use NYT API to find articles.  I don't know how I will get past pay wall, I
may need to log in on Firefox.
"""
import datetime
import re
from typing import Iterator, List

from bs4 import BeautifulSoup

from shared_tools import stack_tools
from sql import *


def getter(period: Period) -> List[Url]:
    if period.year != 2020:
        raise NotImplementedError
    week_zero = datetime.date(2020, 9, 3)
    week_n = week_zero + datetime.timedelta(weeks=period.week)
    return ["https://www.nytimes.com/{}/{:02d}/{:02d}/sports/football/nfl-picks-week-{}.html".format(
        week_n.year, week_n.month, week_n.day, period.week
    )]


def strip_html(html: str) -> str:
    html = html.replace("</p>", " </p>")
    while html.find("  ") != -1:
        html = html.replace("  ", " ")
    soup = BeautifulSoup(html, features="html.parser")
    return soup.text.strip()


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
        strong_splits.pop()  # Remove last one.
        # raise ValueError("Expect even number of <strong> tags.")

    for split_i, split in enumerate(strong_splits):
        try:
            if split_i % 2 == 0:
                continue
            # This is a game block
            next_strong_ending = strong_splits[split_i + 1].split("</p>")[0]
            game_block = f"<strong{split}<strong{next_strong_ending}</p>"
            logging.debug(game_block)
            logging.debug("===========")

            game_soup = BeautifulSoup(game_block, features="html.parser")
            teams = game_soup.strong.contents[0]
            away_team, home_team = teams.split(" at ")

            # Delete the first two and the last paragraph of the game_block
            body = strip_html(
                game_block.split("</em></p>")[-1].split("<strong")[0]
            )

            pick_clause = (
                game_block.split("</strong>")[-1].split("</p>")[0].strip()
            )

            yield GameInfo(
                home_team=home_team,
                away_team=away_team,
                pick_clause=pick_clause,
                body=body,
            )
        except Exception as e:
            logging.error(e)


def scraper(
        text: PageText,
        link: Url,
        run_date: Date,
        period: Period,
        safe_mode: SafeMode,
) -> None:
    logging.info(f"Running NYT on URL: {link}")

    # Get the author
    match = re.search(r"nytimes.com/by/([^\"]+)\"", text)
    author = " ".join(match.group(1).split("-"))
    expert_id = get_expert_id(author)

    # Get fetched date
    now = datetime.datetime.now()
    date = now.year * 10000 + now.month * 100 + now.day

    # Get latest date
    if text.find("Updated <!-- -->") != -1:
        # Look for "Updated <!-- -->Nov. 8, 2020</span>"
        prediction_date = stack_tools.full_parse_date(
            text.split("Updated <!-- -->")[1].split("</span>")[0])
    elif text.find("Published <!-- -->") != -1:
        # Look for "Published <!-- -->Nov. 8, 2020</span>"
        prediction_date = stack_tools.full_parse_date(
            text.split("Published <!-- -->")[1].split("</span>")[0])
    else:
        # Look for any time tag
        time_clause = text.split("<time")[1].split("</time")[0]
        time_clause = time_clause.split("</span>")[0].split(">")[-1]
        prediction_date = stack_tools.full_parse_date(time_clause)

    for game in read_games(text):
        try:
            home_team_id = get_team_id(game.home_team)
            away_team_id = get_team_id(game.away_team)
            predicted_winner_id = get_team_id(game.pick_clause.split()[0])
            if (
                    predicted_winner_id != home_team_id
                    and predicted_winner_id != away_team_id
            ):
                raise ValueError(
                    "Pick {} doesn't match either team {} or {}".format(
                        game.pick_clause.split()[0],
                        game.home_team,
                        game.away_team,
                    )
                )

            spread_favorite, spread_amt = stack_tools.spread_favorite_amt(
                game.pick_clause, predicted_winner_id, away_team_id,
                home_team_id)

            new_row = {
                "expert_id": expert_id,
                "affiliate": "NYT",
                "prediction_date": prediction_date,
                "fetched_date": run_date,
                "game_date": get_date_from_week_hometeam(period, home_team_id),
                "home_team_id": home_team_id,
                "away_team_id": away_team_id,
                "predicted_winner_id_with_spread": predicted_winner_id,
                "spread_favorite": spread_favorite,
                "spread_amt": spread_amt,
                "body": game.body,
                "link": link,
                "exclude": False,
            }
            add_row_to_table("stack", new_row, safe_mode=safe_mode)
        except Exception as e:
            logging.error(e)
