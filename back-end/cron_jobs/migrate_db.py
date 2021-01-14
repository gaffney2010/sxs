"""(Soft) Migrate the database.

0 6 * * *
"""

import materialize_table
import translate_data


materialize_table.mat()
translate_data.soft_translate()
