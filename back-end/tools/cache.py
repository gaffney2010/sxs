import logging
import os
import pickle
import time
from typing import Any, Optional, Union

import filelock

from configs import *

RAW_HTML_DIR = f"{SXS}/back-end/data/raw_html"
EXPIRATION_PAD = "expiration.pickle"
EXPIRATION_PAD_LOCK = "expiration.pickle.lock"

TOMBSTONE_LEN = 7 * 24  # 7 days

# An infinite token
class InfTtl(object):
    pass


# Time-to-live object
TtlHours = Union[int, InfTtl]
# Seconds from epoch
Seconds = int


def _transform_key(key: str) -> str:
    """Make it safe to save"""
    return os.path.join(RAW_HTML_DIR, key.replace("/", ""))


def _expiration_from_ttl(ttl: TtlHours) -> Seconds:
    if isinstance(ttl, InfTtl):
        return 253402214400  # Dec 31, 9999
    return int(time.time()) + (ttl * 60 * 60)


class BaseCacher(object):
    """A strategy for how to read and write locally."""

    def try_to_read(self, key: str) -> Optional[Any]:
        """Returns flat text if found, otherwise None."""
        raise NotImplementedError

    def write(self, key: str, value: Any) -> None:
        """Write value by key locally."""
        raise NotImplementedError


class Cacher(BaseCacher):
    """Empty cache, doesn't save or load."""

    def try_to_read(self, key: str) -> Optional[Any]:
        return None

    def write(self, key: str, value: Any) -> None:
        pass


class TimedReadWriteCacher(BaseCacher):
    """Implements a write-aside with a TTL for expiration."""

    def __init__(self, directory: str = RAW_HTML_DIR, ttl: TtlHours = InfTtl):
        self.ttl = ttl

    def try_to_read(self, key: str) -> Optional[Any]:
        """Always try to read locally."""
        tkey = _transform_key(key)
        if os.path.exists(tkey):
            with open(tkey, "rb") as f:
                return pickle.load(f)

    def write(self, key: str, value: Any) -> None:
        """Write if file doesn't already exist, and set ttl."""
        tkey = _transform_key(key)
        if not os.path.exists(tkey):
            with open(tkey, "wb") as f:
                pickle.dump(value, f)
            with filelock.FileLock(
                os.path.join(RAW_HTML_DIR, EXPIRATION_PAD_LOCK)
            ):
                pad_path = os.path.join(RAW_HTML_DIR, EXPIRATION_PAD)
                pad = dict()
                if os.path.exists(pad_path):
                    with open(pad_path, "rb") as f:
                        pad = pickle.load(f)
                pad[tkey] = _expiration_from_ttl(self.ttl)
                with open(pad_path, "wb") as f:
                    pickle.dump(pad, pad_path)


def cache_reaper() -> None:
    pad_lock = os.path.join(RAW_HTML_DIR, EXPIRATION_PAD_LOCK)
    pad_path = os.path.join(RAW_HTML_DIR, EXPIRATION_PAD)

    with filelock.FileLock(pad_lock):
        pad = dict()
        if os.path.exists(pad_path):
            with open(pad_path, "rb") as f:
                pad = pickle.load(f)

        files_encountered = set()
        for fn in os.listdir(RAW_HTML_DIR):
            logging.debug(fn)
            files_encountered.add(fn)
            if fn in pad:
                if pad[fn] < time.time():
                    # Expired.
                    os.remove(os.path.join(RAW_HTML_DIR, fn))
            else:
                # Something happened, add a tombstone.
                pad[fn] = _expiration_from_ttl(TOMBSTONE_LEN)

        # If for some reason, the pad has entries for files that don't exist,
        #  then erase these.
        pad = {fn: pad[fn] for fn in files_encountered}
        logging.debug(pad)

        with open(pad_path, "wb") as f:
            pickle.dump(pad, f)



def memoize(key: str, cacher: Cacher):
    def real_memoize(func):
        def func_with_memo(*args, **kwargs):
            cached_value = cacher.try_to_read(key)
            if cached_value is not None:
                return cached_value
            result = func(*args, **kwargs)
            cacher.write(key, result)
            return result

        return func_with_memo

    return real_memoize
