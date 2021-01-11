import datetime

import dateparser

from shared_types import *


def full_parse_date(text: str) -> Date:
    """Runs date parser, AND converts to Date."""
    pred = dateparser.parse(text)
    return pred.year * 10000 + pred.month * 100 + pred.day


def today() -> Date:
    return int(datetime.datetime.today().strftime("%Y%m%d"))


def today_plus(delta: int) -> Date:
    today = datetime.datetime.today()
    then = today + datetime.timedelta(days=delta)
    return int(then.strftime("%Y%m%d"))
