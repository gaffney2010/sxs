"""(Soft) Migrate the database.

0 6 * * *
"""

################################################################################
# Logging logic, must come first
SAFE_MODE = False
from tools.logger import configure_logging, log_section

configure_logging(SAFE_MODE)
################################################################################

import materialize_table
import translate_data


log_section("migrate_db.py")

translate_data.soft_translate()
materialize_table.mat()
