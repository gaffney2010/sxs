from datetime import datetime

import dateparser

from shared_types import *


def full_parse_date(text: str) -> Date:
    """Runs date parser, AND converts to Date."""
    pred = dateparser.parse(text)
    return pred.year * 10000 + pred.month * 100 + pred.day


def today() -> Date:
    return int(datetime.today().strftime("%Y%m%d"))
