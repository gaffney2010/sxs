import logging
import traceback
from typing import Callable

from shared_tools.cache import *

LOG_DIR = "/home/gaffney/stacks-by-stacks/back-end/logs"
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