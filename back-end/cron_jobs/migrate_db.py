"""(Soft) Migrate the database.

0 6 * * *
"""

import translate_data


translate_data.soft_translate()
