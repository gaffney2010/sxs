"""Script pull_nhl will pull CBS with start and end dates.

Ex. https://freepicks.picksandparlays.net/more-free-picks/nhl-picks
https://freepicks.picksandparlays.net/more-free-picks/nhl-picks/dallas-stars-vs-tampa-bay-lightning-92620-nhl-picks-and-predictions
Not like -- https://freepicks.picksandparlays.net/more-free-picks/nhl-picks/lightning-vs-stars-game-6-monday-92820-nhl-picks-and-predictions
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging
import logging

configure_logging(SAFE_MODE, logging_level=logging.INFO)
################################################################################

import enum
# import logging

import bs4
import traceback

from shared_types import *
from tools import date_lib, game_key, scraper_tools, sql

MAX_PG = 100  # All available pages
FREE_PICK = "Free NHL Pick:"


class PullStatus(enum.Enum):
    """How pull_page exits."""
    Unknown = 0
    Success = 1
    NotAFreePick = 2
    NonUniqueGame = 3


def pull_page(url: Url, safe_mode: bool = SAFE_MODE) -> PullStatus:
    page_text = scraper_tools.one_day_read(url)
    if page_text.find(FREE_PICK) == -1:
        return PullStatus.NotAFreePick
    soup = bs4.BeautifulSoup(page_text, features="html5lib")

    article_date_title = soup.find("div", {"class": "article-date"})
    author = str(article_date_title).split("/cappers/")[1].split("\"")[0]
    expert_id = sql.force_get_expert_id(author)

    published = article_date_title.find("span", {"itemprop": "datePublished"})
    modified = article_date_title.find("span", {"itemprop": "dateModified"})
    date_str = modified.text if modified else published.text
    logging.info(f"DATE === {date_str}")
    prediction_date = date_lib.full_parse_date(date_str)

    game_clause = soup.find("td", {"itemprop": "name performer about"})
    teams = [span.text for span in game_clause.findAll("span")]
    assert (len(teams) == 2)
    team_1, team_2 = teams
    team_1_id, team_2_id = sql.get_team_id(team_1), sql.get_team_id(team_2)

    date_clause = soup.find("td", {"itemprop": "startDate"})
    date = date_lib.full_parse_date(date_clause.text)

    try:
        gk = game_key.get_unique_game_key(date, team_1_id, team_2_id)
    except game_key.HeaderException:
        return PullStatus.NonUniqueGame

    pick_clause = soup.find("div", {"class": "article-pick flex"})
    pick_clause = pick_clause.text.replace(FREE_PICK, "")
    pick_clause_list = scraper_tools.strip_white_space(pick_clause).split(" ")
    pick = " ".join(pick_clause_list[:-1])
    ml = int(pick_clause_list[-1])

    # body = soup.find("div", {"class": "article-body"})
    conclusion = soup.find("div", {"class": "article-conclusion"})
    article_text = scraper_tools.strip_white_space(conclusion.text)

    new_stack = {
        "expert_id": expert_id,
        "affiliate": "PicksAndParlays",
        "game_key": gk,
        "predicted_winner_id": sql.get_team_id(pick),
        "money_line": ml,
        "body": article_text,
        "link": url,
        "prediction_date": prediction_date,
        "fetched_date": date_lib.today(),
        "exclude": False,
    }
    sql.add_row_to_table("Stack", new_stack, safe_mode=safe_mode)

    return PullStatus.Success


def pull_links_from_page(url: Url, start: Date, end: Date,
                         safe_mode: bool = SAFE_MODE) -> bool:
    """Read everything from the page, and return if there's more."""
    page_text = scraper_tools.one_day_read(url)
    soup = bs4.BeautifulSoup(page_text, features="html5lib")
    for div in soup.findAll("div", {"class": "article-content"}):
        date_str = scraper_tools.strip_white_space(
            div.find("div", {"class": "article-meta"}).text)
        date = date_lib.full_parse_date(date_str)
        if date >= end:
            continue
        if date < start:
            return False
        link = div.find("a")["href"]
        try:
            status = pull_page(f"https://freepicks.picksandparlays.net{link}",
                               safe_mode=safe_mode)
            logging.info(status)
        except:
            logging.error(f"Uncaught error for PicksAndParlays: {link}")
            logging.error(traceback.format_exc())
    return True


def _pg(no: int) -> str:
    return f"https://freepicks.picksandparlays.net/more-free-picks/nhl-picks?page={no}"


def pull_all_starting_with_page(pg_no: int, start: Date, end: Date,
                                safe_mode: bool = SAFE_MODE) -> None:
    no = pg_no
    while pull_links_from_page(_pg(no), start, end, safe_mode=safe_mode):
        no += 1
        if no >= MAX_PG:
            return


pull_all_starting_with_page(0, 0, 99999999)
