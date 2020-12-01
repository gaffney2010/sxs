from datetime import datetime
import logging
import traceback
from typing import Callable

from local_config import SXS
from shared_tools.cache import *

LOG_DIR = f"{SXS}/back-end/logs"
ErrorLogger = Callable


def swallow_error(default_return: Any):
    """ A decorator which passes through an error with proper logging."""

    def real_swallow_error(func):
        def func_with_swallow(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logging.error("SWALLOWING ERROR!")
                logging.error("function called: {}".format(func))
                logging.error(args)
                logging.error(kwargs)
                logging.error("Exception:", traceback.format_exc(), str(e))

                return default_return

        return func_with_swallow

    return real_swallow_error


def configure_logging(safe_mode: bool) -> None:
    now = datetime.now()
    today = now.year * 10000 + now.month * 100 + now.day

    if safe_mode:
        # Print to screen
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            level=logging.INFO,
        )
    else:
        # Print to file
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            filename=LOG_DIR + str(today) + ".log",
            level=logging.INFO,
        )
