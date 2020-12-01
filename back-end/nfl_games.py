################################################################################
# Logging logic, must come first
SAFE_MODE = False
from shared_tools.logger import configure_logging
configure_logging(SAFE_MODE)
################################################################################

from bs4 import BeautifulSoup

from shared_tools.date_reader import *
from shared_tools.scraper_tools import *
from sql import *

NFL_PAGE = "https://www.nfl.com/schedules/{}/REG{}/"

raw_html_cacher = TimedReadWriteCacher(directory=RAW_HTML_DIR, age_days=1)


def pull_week(season: int, week: int, prompt_on_miss: bool = True) -> None:
    with WebDriver() as driver:
        nfl_page_text = read_url_to_string(NFL_PAGE.format(season, week), driver,
                                           cacher=raw_html_cacher)
    nfl_page = BeautifulSoup(nfl_page_text, features="html.parser")

    main_section = nfl_page.find("div", {"data-require": "modules/scheduleByWeek"})
    for day_section in main_section.select("div[class^=d3-l-col]"):
        day_header = day_section.find("h2").contents[0]
        date = read_date(day_header)
        date_int = date.year*10000 + date.month*100 + date.day
        for div in day_section.select("div[class^=nfl-c-matchup-strip\ ]"):
            new_game = dict()

            new_game["game_date"] = date_int

            new_game["season"] = season
            new_game["week"] = week

            game_type_str = div.attrs["class"][1].split("--")[1]
            game_type_map = {
                "pre-game": 1,  # UPCOMING
                "in-game": 2,  # LIVE
                "post-game": 3,  # PAST
            }
            new_game["play_status"] = game_type_map[game_type_str]

            away_text, home_text = "".join(map(str, div.contents)).split(
                "nfl-c-matchup-strip__team-separator")
            away, home = BeautifulSoup(away_text,
                                       features="html.parser"), BeautifulSoup(
                home_text, features="html.parser")
            away_name = away.find("span", {
                "class": "nfl-c-matchup-strip__team-fullname"}).contents[0].strip()
            home_name = home.find("span", {
                "class": "nfl-c-matchup-strip__team-fullname"}).contents[0].strip()
            new_game["away_team_id"] = get_team_id(away_name, prompt_on_miss=prompt_on_miss)
            new_game["home_team_id"] = get_team_id(home_name, prompt_on_miss=prompt_on_miss)

            if game_type_str == "post-game":
                new_game["away_score"] = int(away.find("div", {
                    "class": "nfl-c-matchup-strip__team-score"}).contents[0].strip())
                new_game["home_score"] = int(home.find("div", {
                    "class": "nfl-c-matchup-strip__team-score"}).contents[0].strip())

            # TODO(#17): Implement mutual_location.

            logging.debug(new_game)
            add_row_to_table("game", new_game)
