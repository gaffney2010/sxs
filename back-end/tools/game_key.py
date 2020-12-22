"""A function to compute the game key from date and teams."""

from shared_types import *
from tools.sql import sql_exists


class NoHeaderException(Exception):
    pass


class DoubleHeaderException(Exception):
    pass


def game_key(date: int, x: TeamId, y: TeamId, n: int = 1) -> str:
    """Get a key to use in SQL tables."""
    if n >= 10:
        # n is used if there are multiple games in a day.
        raise Exception("Large n should never happen")

    # Injective commutative mapping of x and y.
    t = (x + 1) * (y + 1) * (x * y + x + y) + 2 * (x + y)
    t_str = str(hex(t))[2:]
    t_str = ("00000000" + t_str)[-8:]

    return "{}{}x{}".format(date, n, t_str)


def get_unique_game_key(date: int, x: TeamId, y: TeamId) -> GameKey:
    """Returns the GameKey iff there's only one game for the day.'"""
    key_1 = game_key(date, x, y)
    key_2 = game_key(date, x, y, 2)
    if not sql_exists(f"select * from Game where game_key='{key_1}';"):
        raise NoHeaderException
    if sql_exists(f"select * from Game where game_key='{key_2}';"):
        raise DoubleHeaderException
    return key_1
