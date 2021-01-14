"""Scrape this damn redditor.
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False

from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

import logging
import re
import traceback

import praw

from configs import *
from shared_types import *
from tools import date_lib, game_key, sql

COMMENT_1 = """???
# 2 NHL PICKS BY STATS PROFESSOR

#  

a) Coyotes vs Predators (@ +122 at Bookmaker.eu, i.e. 2.22 in decimal)

b) Oilers vs Blackhawks (@ -131 at Pinnacle, i.e. 1.76 in decimal)

Thus far in playoffs:

* RECORD = 5-3
* PROFIT = +1.82 unit

Best of luck!

[Professor MJ](https://twitter.com/DavidBeaudoin79)"""

COMMENT_2 = """
NHL Picks by Stats Professor for Monday August 3rd (let's build off yesterday's win on the Minnesota Wild!):

&#x200B;

a) Under 5.5 Stars-Golden Knights (@ -140)

b) Jets +140 vs Flames (sorry I posted this one too late here, but it's been on my Twitter this morning)

c) Under 6 Caps-Lightning (@ +100)

d) Canadiens +150 vs Penguins (waiting to place my bet because I'm optimistic the line will go up to +155 later today)

&#x200B;

Best of luck my friends!

[Professor MJ](https://twitter.com/DavidBeaudoin79)"""

COMMENT_3 = """
# NHL Pick by Stats Professor from Canada

# Toronto Maple Leafs -148 (1.68 decimal format) vs Columbus Blue Jackets

Thus far in playoffs:

* Record = 3-2
* Profit = +1.34 unit (from risking 1 unit per play)

Best of luck!

[Professor MJ](https://twitter.com/DavidBeaudoin79)"""

COMMENT_4 = """
Some explanations about the under 6.5 Chicago-Edmonton pick. The odds on "under 6" was -107 in Game #1, then +102 in Game #2 and now +124 in Game #3. Line clearly inflated due to overreaction to recent results, in my humble opinion. As a contrarian, I'm taking the "under".

As for the Avs, they should be favored with a -150 line at least. Much stronger team. +46 goal differential this year versus just +3 for the Stars. Give me Colorado in this one.
# 2 NHL PICKS (by University Statistics Professor)

# 

a) **Under 6.5 Blackhawks-Oilers @ -109 odds (1.91 decimal)**

b) **Avalanche @ -127 odds (1.79 decimal) vs Stars**

Why not add a couple of "leans" (unofficial picks that I like, but maybe not enough to bet... Up to you!)

c) *Under 5.5 Bruins-Lightning @ -104 odds (1.96 decimal)*

d) *Coyotes @ +115 odds (2.15 decimal) vs Predators*

Thus far in the 2020 playoffs:

* Record = 4-2
* Profit = +2.03 units (from risking 1 unit per play)

[Professor MJ](https://twitter.com/DavidBeaudoin79)"""

COMMENT_5 = """
# NHL System Picks by University Stats Professor (Thursday March 5th)

# 

Huge upset by the Ducks last night in Colorado! It generated a profit of 2.55 units.

&#x200B;

Too bad the Caps lost their big showdown with the Flyers (for a 1-unit loss since we're always risking 1 unit).

&#x200B;

Overall: +1.55 unit yesterday.

&#x200B;

RECORD:

&#x200B;

* Bets won = 99
* Bets lost = 127
* Profit = +1.07 unit (from RISKING 1 unit on every play)

&#x200B;

Today's picks based on my 10 NHL betting systems:

&#x200B;

* **4 STARS = Hurricanes (@ +116 or 2.16 odds, at Flyers)**
* **4 STARS = Wild (@ -111 or 1.90 odds, at Sharks)**
* **2 STARS = Rangers (@ +126 or 2.26 odds, vs Capitals)**
* **2 STARS = Kings (@ +157 or 2.57 odds, vs Maple Leafs)**
* **1 STAR = Canadiens (@ +165 or 2.65 odds, at Lightning)**

&#x200B;

Happy Thursday everyone!

&#x200B;

[Professor MJ](https://twitter.com/DavidBeaudoin79)"""

TEAMS = (
    "bruins",
    "sabres",
    "wings",
    "panthers",
    "canadiens",
    "senators",
    "lightning",
    "leafs",
    "hurricanes",
    "jackets",
    "devils",
    "islanders",
    "rangers",
    "flyers",
    "penguins",
    "capitals",
    "hawks",
    "avalanche",
    "stars",
    "wild",
    "predators",
    "blues",
    "jets",
    "ducks",
    "coyotes",
    "flames",
    "oilers",
    "kings",
    "sharks",
    "canucks",
    "knights",
)


def parse_comment(comment: str, date: Date, url: Url,
                  safe_mode: bool = SAFE_MODE) -> None:
    lines = comment.split("\n")
    for line in lines:
        logging.debug("Trying line.")
        logging.debug(line)

        # Special case, if STARS in all caps.
        line = line.replace("STARS", "")

        line = line.lower()

        if line.find("over") != -1 or line.find("under") != -1:
            logging.debug("Found over/under.")
            continue
        if line.find("pl ") != -1:
            logging.debug("Found PL.")
            continue

        teams = list()
        team_inds = list()
        for t in TEAMS:
            ti = line.find(t)
            if ti != -1:
                teams.append(t)
                team_inds.append(ti)
        if len(teams) != 2:
            logging.debug(f"Found {len(teams)} teams.")
            continue
        team_teams = list(zip(team_inds, teams))
        team_teams.sort()
        teams = [x[1] for x in team_teams]
        team_inds = [x[0] for x in team_teams]

        at_or_vs = None
        at_ind = line.find(" at ")
        if at_ind != -1:
            at_or_vs = at_ind
        at_ind = line.find("@")
        if at_ind != -1:
            at_or_vs = at_ind
        vs_ind = line.find(" vs")
        if vs_ind != -1:
            at_or_vs = vs_ind
        if not at_or_vs:
            logging.debug("Not found at or vs.")
            continue

        if at_or_vs < team_inds[0] or at_or_vs > team_inds[1]:
            logging.debug("Bad order")
            continue

        match = re.search(r"[+-]\d\d\d ", line)
        if not match:
            logging.debug("Couldn't find ml.")
            continue

        ml = match.group(0)[:4]

        pick_id = sql.get_team_id(teams[0])
        opp_id = sql.get_team_id(teams[1])

        gk = game_key.get_unique_game_key(date, pick_id, opp_id)

        stack = {
            "expert_id": sql.get_expert_id("david-mj"),
            "affiliate": "Reddit",
            "game_key": gk,
            "predicted_winner_id": pick_id,
            "money_line": int(ml),
            "link": f"http://reddit.com/{url}",
            "fetched_date": date_lib.today(),
            "exclude": False,
        }
        sql.add_row_to_table("Stack", stack, safe_mode=safe_mode)


def pull_all_comments(start: Date, end: Date, safe_mode: bool = SAFE_MODE) -> None:
    reddit = praw.Reddit(**PRAW_CONFIG)
    comments = reddit.redditor("David-MJ").comments.new(limit=None)

    for comment in comments:
        if comment.submission.title.find("NHL Daily Discussion") != -1:
            date = date_lib.full_parse_date(
                comment.submission.title.split(" - ")[1])
            url = comment.permalink
            if start <= date < end:
                try:
                    parse_comment(comment.body, date, url, safe_mode=safe_mode)
                except:
                    logging.error("Uncaught error.")
                    logging.error(comment.body)
                    logging.error(traceback.format_exc())


# pull_all_comments(0, 99999999)
