import os.path
from datetime import datetime
from typing import Callable

from shared_tools.cache import *

LOG_DIR = "/home/gaffney/stacks-by-stacks/back-end/logs"
ErrorLogger = Callable


def _error_iterator(*args):
    """ Adds decorators to a passed stream of error messages."""
    now = datetime.now()
    yield "{}".format(now.strftime("%Y-%m-%d %H:%M"))
    for arg in args:
        yield str(arg)
    yield "==========="


def print_error(*args):
    """ Same as log_error, but only prints to the screen."""
    for msg in _error_iterator(*args):
        print(msg)


def log_error(*args):
    """ Saves the arguments to a daily log with the time, and some other decorators."""
    print_error(*args)
    # Change the file name every day.
    log_path = os.path.join(LOG_DIR,
                            "{}".format(datetime.now().strftime("%Y%m%d")))
    with open(log_path, "a") as log_file:
        for msg in _error_iterator(*args):
            print(msg)
            log_file.write(msg)
            log_file.write("\n")


def swallow_error(default_return: Any,
                  error_logger: Optional[ErrorLogger] = None):
    """ A decorator which passes through an error with proper logging."""
    if error_logger is None:
        # Don't log.
        error_logger = lambda *args: None

    def real_swallow_error(func):
        def func_with_swallow(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except BaseException as e:

                error_logger(
                    "SWALLOWING ERROR!", str(e),
                    "function called: {}".format(func),
                    args, kwargs)

                return default_return

        return func_with_swallow

    return real_swallow_error