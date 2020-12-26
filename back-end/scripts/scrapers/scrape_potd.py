"""Script will pull this random spreadsheet

https://docs.google.com/spreadsheets/d/1glOKlt6NA2V-1sC3yP4_Jb5wx2FSS8hDJyYAy6uFMmE/edit#gid=0
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging

configure_logging(SAFE_MODE)
################################################################################

import functools

import requests

from tools import date_lib, game_key, sql

SHEET_URL = "https://docs.google.com/spreadsheet/ccc?key=1glOKlt6NA2V-1sC3yP4_Jb5wx2FSS8hDJyYAy6uFMmE&output=csv"


@functools.lru_cache(1)
def _get_page():
    response = requests.get(SHEET_URL)
    return response.content


_lines = _get_page().decode().split("\n")
lines = [{x: y for x, y in zip (_lines[0].split(","), l.split(","))} for l in _lines]

for i, line in enumerate(lines):
    if line["Type"] != "ML":
        continue

    date = date_lib.full_parse_date(line["Date"])
    prediction = line["Team"].replace(" (H)", "")
    opponent = line["Opponent"].replace(" (H)", "")
    pred_id, opp_id = sql.get_team_id(prediction), sql.get_team_id(opponent)
    gk = game_key.get_unique_game_key(date, pred_id, opp_id)

    new_stack = {
        "expert_id": sql.force_get_expert_id("POTD"),
        "affiliate": "POTD",
        "game_key": gk,
        "predicted_winner_id": pred_id,
        "money_line": int(line["Odds"]),
        "link": SHEET_URL,
        "fetched_date": date_lib.today(),
        "exclude": False,
    }
    sql.add_row_to_table("Stack", new_stack, safe_mode=SAFE_MODE)
