"""(Soft) Migrate the database.

0 6 * * *
"""

import materialize_table
import translate_data


translate_data.soft_translate()
materialize_table.mat()
