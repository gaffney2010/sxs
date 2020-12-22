################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

import datetime
import logging
import re

import bs4
import dateparser

from shared_types import *
from tools import date_lib, game_key, scraper_tools, sql


def pull_single_game(url: Url, safe_mode: bool = SAFE_MODE) -> None:
    page_text = scraper_tools.one_day_read(url)
    soup = bs4.BeautifulSoup(page_text, features="html5lib")

    teams = soup.find("h1").text
    team_1, team_2 = teams.split(" - ")
    team_1_id, team_2_id = sql.get_team_id(team_1), sql.get_team_id(team_2)

    date_str = soup.find("p", {"class": re.compile("^date datet")}).text
    date = date_lib.full_parse_date(date_str)

    try:
        gk = game_key.get_unique_game_key(date, team_1_id, team_2_id)
    except game_key.NoHeaderException:
        pred = dateparser.parse(date_str)
        pred = pred - datetime.timedelta(days=1)
        prev_date = pred.year * 10000 + pred.month * 100 + pred.day
        gk = game_key.get_unique_game_key(prev_date, team_1_id, team_2_id)

    avg_row = page_text.split("Average")[1].split("</tr>")[0]
    avg_row_html = f"<table><tr><td><strong>{avg_row}</tr></table>"
    avg_soup = bs4.BeautifulSoup(avg_row_html, features="html5lib")
    odds = [td.text for td in avg_soup.findAll("td", {"class": "right"})]
    moneyline_1, moneyline_2 = int(odds[0]), int(odds[1])

    odd_row = {
        "game_key": gk,
        "pull_date": date_lib.today(),
        "pull_hour": 0,
        "team_1": team_1_id,
        "money_line_1": moneyline_1,
        "team_2": team_2_id,
        "money_line_2": moneyline_2,
    }
    sql.add_row_to_table("odd", odd_row, safe_mode=safe_mode)


def pull_page(url: Url, safe_mode: bool = SAFE_MODE) -> bool:
    page_text = scraper_tools.one_day_read(url)
    soup = bs4.BeautifulSoup(page_text, features="html5lib")
    at_least_one_game = False
    for td in soup.findAll("td", {"class": "name table-participant"}):
        try:
            link = str(td).split("href=\"")[1].split("\"")[0]
            pull_single_game(f"https://www.oddsportal.com/{link}#home-away;1",
                             safe_mode=safe_mode)
        except:
            logging.error(f"Failed on URL: {str(td)} from {url}")
        else:
            at_least_one_game = True
    return at_least_one_game


def pull_season(url: Url, safe_mode: bool = SAFE_MODE) -> None:
    pg = 1
    while pull_page(f"{url}/#/page/{pg}/", safe_mode):
        pg += 1


pull_season("https://www.oddsportal.com/hockey/usa/nhl/results")
pull_season("https://www.oddsportal.com/hockey/usa/nhl-2018-2019/results")
