"""Script pull_nhl will pull DocSports with start and end dates.

Ex. https://www.docsports.com/free-picks/nhl-hockey/
https://www.docsports.com/free-picks/nhl-hockey/2020/tampa-bay-lightning-vs-dallas-stars-prediction-9-28-2020-nhl-pick-tips-and-odds.html
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

import logging
import traceback

import bs4

from shared_types import *
from tools import date_lib, game_key, scraper_tools, sql

MAX_PG = 426


def pull_page(url: Url, safe_mode: bool = SAFE_MODE) -> None:
    page_text = scraper_tools.one_day_read(url)
    soup = bs4.BeautifulSoup(page_text, features="html5lib")
    parts = [_ for _ in soup.findAll("div", {"class": "Text"})]

    author, prediction_date_str = parts[0].text.split("by ")[1].split(" - ")
    expert_id = sql.force_get_expert_id(author)
    prediction_date = date_lib.full_parse_date(prediction_date_str)

    body_pars = list()
    game_clause, date_clause, pick_clause = None, None, None
    for p in parts[1].findAll("p"):
        if str(p).find("<strong>") == -1:
            body_pars.append(p.text)
            continue

        if p.find("strong").text == "Game:":
            game_clause = scraper_tools.strip_white_space(
                str(p).split("</strong>")[1].split("</p>")[0])

        if p.find("strong").text == "Date:":
            date_clause = scraper_tools.strip_white_space(
                str(p).split("</strong>")[1].split("</p>")[0])

        if str(p).find("Pick") != -1:
            pick_clause = scraper_tools.strip_white_space(
                str(p).split("Pick:")[1].split("</strong>")[0])
            break

    body = " ".join(body_pars)

    team_1, team_2 = game_clause.split(" vs ")
    # Danger mode
    team_1_id, team_2_id = sql.get_team_id(team_1,
                                           prompt_on_miss=False), sql.get_team_id(
        team_2, prompt_on_miss=False)
    date = date_lib.full_parse_date(date_clause)
    gk = game_key.get_unique_game_key(date, team_1_id, team_2_id)

    if pick_clause.find("Take ") != -1:
        pick_clause = pick_clause.replace("Take ", "")
    pick_words = pick_clause.split(" ")
    predicted_winner_id = sql.get_team_id(" ".join(pick_words[:-1]),
                                          prompt_on_miss=False)
    ml = int(pick_words[-1].replace("(", "").replace(")", ""))

    new_stack = {
        "expert_id": expert_id,
        "affiliate": "PicksAndParlays",
        "game_key": gk,
        "predicted_winner_id": predicted_winner_id,
        "money_line": ml,
        "body": scraper_tools.strip_white_space(body),
        "link": url,
        "prediction_date": prediction_date,
        "fetched_date": date_lib.today(),
        "exclude": False,
    }
    sql.add_row_to_table("Stack", new_stack, safe_mode=safe_mode)


def pull_links_from_page(url: Url, start: Date, end: Date,
                         safe_mode: bool = SAFE_MODE) -> bool:
    """Read everything from the page, and return if there's more."""
    page_text = scraper_tools.zero_day_read(url)
    soup = bs4.BeautifulSoup(page_text, features="html5lib")
    for div in soup.findAll("div", {"class": "views-row views-row-flex"}):
        try:
            date_str = str(div).split(" - ")[1].split("<br")[0]
            date = date_lib.full_parse_date(date_str)
            if date >= end:
                continue
            if date < start:
                return False
        except:
            logging.error(f"Really uncaught error.")
            logging.error(str(div))
            logging.error(traceback.format_exc())
        link = div.find("a")["href"]
        try:
            status = pull_page(link, safe_mode=safe_mode)
            logging.info(status)
        except:
            logging.error(f"Uncaught error for DocSports: {link}")
            logging.error(traceback.format_exc())
    return True


def _pg(no: int) -> str:
    return f"https://www.docsports.com/free-picks/nhl-hockey/?start={no * 20}"


def pull_all_starting_with_page(pg_no: int, start: Date, end: Date,
                                safe_mode: bool = SAFE_MODE) -> None:
    no = pg_no
    while pull_links_from_page(_pg(no), start, end, safe_mode=safe_mode):
        no += 1
        if no >= MAX_PG:
            return


# pull_all_starting_with_page(0, 20181001, 99999999)
