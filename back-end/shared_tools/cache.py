import os
import pickle
import time
from typing import Any, Optional


def _esc_key(key: str) -> str:
    """Make it safe to save"""
    return key.replace("/", "")


class Cacher(object):
    """A strategy for how to read and write locally."""

    def try_to_read(self, key: str) -> Optional[Any]:
        """Returns flat text if found, otherwise None."""
        return None

    def write(self, key: str, value: Any) -> None:
        """Write value by key locally."""
        return None


def _write_key_value(directory: str, key: str, value: Any) -> None:
    """Write value to directory/key."""
    with open(os.path.join(directory, _esc_key(key)), "wb") as f:
        return pickle.dump(value, f)


class WriteCacher(Cacher):
    """Only writes to relative directory, but always write."""

    def __init__(self, directory: str):
        self.directory = directory
        super().__init__()

    def write(self, key: str, value: Any) -> None:
        _write_key_value(self.directory, key, value)


def _read_key(directory: str, key: str) -> Any:
    """Reads a file.  Will raise if file doesn't exist."""
    with open(os.path.join(directory, _esc_key(key)), "rb") as f:
        return pickle.load(f)


class ReadWriteCacher(Cacher):
    """Tries to read locally.  If failed, will write computed value."""

    def __init__(self, directory: str):
        self.directory = directory
        self.should_write = set()
        super().__init__()

    def _read_impl(self, key: str) -> Optional[str]:
        try:
            return _read_key(self.directory, key)
        except:
            return None

    def try_to_read(self, key: str) -> Optional[str]:
        """Try to read and record cache misses."""
        result = self._read_impl(key)
        if result is None:
            self.should_write.add(key)
        return result

    def write(self, key: str, value: Any) -> None:
        """If the key has been cache missed, then write."""
        if key in self.should_write:
            _write_key_value(self.directory, key, value)
            self.should_write.remove(key)


class TimedReadWriteCacher(ReadWriteCacher):
    """Tries to read locally, if not too old.  Will write new reads."""

    def __init__(self, directory: str, age_days: int):
        self.age_days = age_days
        super().__init__(directory)

    def _read_impl(self, key: str) -> Optional[str]:
        """Only try to read locally if the file is newer than age_days old."""
        if os.path.exists(os.path.join(self.directory, key)):
            mod_time = os.path.getmtime(key)
            current_time = time.time()
            if current_time - mod_time < self.age_days * 60 * 60 * 24:
                return _read_key(self.directory, key)


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