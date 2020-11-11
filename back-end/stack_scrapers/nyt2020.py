"""This should scrape NYT reviews.  Works for 2020, maybe goes back.

URL like https://www.nytimes.com/2020/11/05/sports/football/nfl-picks-week-9.html

Can use NYT API to find articles.  I don't know how I will get past pay wall, I
may need to log in on Firefox.
"""

import datetime
import re
from typing import Iterator

import attr
from bs4 import BeautifulSoup

from sql import *


@attr.s
class GameInfo(object):
    """All info I can pull from the game block, with nothing processed."""

    home_team: str
    away_team: str
    pick_clause: str  # "<Team> <Spread>"
    body: str


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
            away_team=away_team,
            home_team=home_team,
            pick_clause=pick_clause,
            body=body,
        )


def read_article(text: str, link: str) -> None:
    # Get the author
    match = re.search(r"nytimes.com/by/[^\"]\"", text)
    author = " ".join(match.split("-"))

    # Get fetched date
    now = datetime.now()
    date = now.year * 10000 + now.month * 100 + now.day

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
            spread_amt = int(game.pick_clause.split("-")[-1])
        elif game.pick_clause.find("+") != -1:
            # Set spread_favorite to the non-predicted-winner
            spread_favorite = (
                away_team_id
                if predicted_winner_id == home_team_id
                else home_team_id
            )
            spread_amt = int(game.pick_clause.split("+")[-1])
        else:
            raise ValueError(
                f"Unexpected, pick clause malformed: {game.pick_clause}"
            )

        new_row = {
            "expert_id": "...",
            "expert_type": "HUMAN",
            "affiliate": "NYT",
            "prediction_date": "...",
            "fetched_date": date,
            "home_team_id": home_team_id,
            "away_team_id": away_team_id,
            "predicted_winner_id_with_spread": predicted_winner_id,
            "spread_favorite": spread_favorite,
            "spread_amount": spread_amt,
            "body": game.body,
            "link": link,
        }
        add_row_to_table("stack", new_row)


test_str = '<div class="css-1fanzo5 StoryBodyCompanionColumn"><div class="css-53u6y8"><p class="css-158dogj evys1bk0"><strong class="css-8qgvsz ebyp5n10">New England Patriots at Jets</strong>, <em class="css-2fg4z9 e1gzwzxm0">8:15 p.m., ESPN</em></p><p class="css-158dogj evys1bk0"><em class="css-2fg4z9 e1gzwzxm0">Line: Patriots -7 | Total: 42.5</em></p><p class="css-158dogj evys1bk0">The Jets (0-8) have matched the longest winless start in franchise history, and the Patriots (2-5) have matched their <a class="css-1g7m0tk" href="https://www.nytimes.com/2020/10/26/sports/football/patriots-49ers.html" title="">worst seven-game start since 2000</a>. Something has to give, and while both teams have been disappointing, the Jets have truly earned their spot at the bottom of the N.F.L. The team is 32nd in points scored and 28th in points allowed.</p><p class="css-158dogj evys1bk0">This game presents what appears to be one of the Jets’ best chances for a win this season. They are playing at home against <a class="css-1g7m0tk" href="https://www.nytimes.com/2020/10/26/sports/football/patriots-49ers.html" title="">an injury-ravaged team</a> that has lost four straight. But it is hard to imagine the Jets scoring enough to beat anyone. Quarterback Sam Darnold aggravated his shoulder injury last week and, <a class="css-1g7m0tk" href="https://www.rotoworld.com/football/nfl/player/9506/frank-gore" title="" rel="noopener noreferrer" target="_blank">as Rotoworld eloquently said of Frank Gore</a>, “We have reached the ‘why? … just why’ phase of Gore’s status as the Jets’ lead back.”</p><p class="css-158dogj evys1bk0">New England has been bad enough that a spread of 7 points seems outlandish, but opponents thus far have seemed to enjoy beating up on the Jets. If Cam Newton wants to prove a point about his health, it is hard to see Gang Green stopping him. <strong class="css-8qgvsz ebyp5n10">Pick:</strong> Patriots -7</p>'
for game in read_games(test_str):
    print(game)
