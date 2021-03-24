from datetime import datetime
import logging

from configs import *


def log_section(section_header: str) -> None:
    WIDTH = 30
    width = max(WIDTH, len(section_header)+4)
    left_margin = (width - len(section_header)) // 2
    right_margin = width - len(section_header) - left_margin

    logging.info("\n")
    logging.info("\n")
    logging.info("=" * width)
    logging.info("=" * left_margin + section_header.upper() + "=" * right_margin)
    logging.info("=" * width)


def configure_logging(safe_mode: bool, logging_level = logging.INFO) -> None:
    now = datetime.now()
    today = now.year * 10000 + now.month * 100 + now.day

    if safe_mode:
        # Print to screen
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            level=logging_level,
        )
    else:
        # Print to file
        logging.basicConfig(
            format="%(asctime)s  %(levelname)s:\t%(module)s::%(funcName)s:%(lineno)d\t-\t%(message)s",
            filename=LOG_DIR + str(today) + ".log",
            level=logging_level,
        )
