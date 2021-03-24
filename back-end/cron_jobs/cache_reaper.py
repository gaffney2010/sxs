"""Clean up caches

0 11 * * *
"""

################################################################################
# Logging logic, must come first
from tools.logger import configure_logging, log_section

# Turn on safe mode because this shouldn't write to our tables anyway.
configure_logging(safe_mode=True)
################################################################################

from tools.cache import cache_reaper

log_section("cache_reaper.py")

cache_reaper()
