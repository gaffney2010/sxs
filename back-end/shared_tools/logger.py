from datetime import datetime
import logging

from configs import SXS

LOG_DIR = f"{SXS}/back-end/logs/"


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
