"""This is a dumb shared file to print false values for dumb mac environment"""

import datetime
import sys

if sys.platform != "darwin":
    import dateparser


def read_date(date: str) -> datetime.datetime:
    result = datetime.datetime.now()  # Dumb default value
    if sys.platform != "darwin":
        result = dateparser.parse(date)
    return result
