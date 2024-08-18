"""Capitol Hill Tool Library specific info"""

from datetime import datetime

# CHTL has been officially open since April 2016!
# https://www.capitolhillseattle.com/2016/04/capitol-hill-tool-library-is-open-for-lending/
OPEN_YEARS = tuple(year for year in range(2016, datetime.utcnow().year + 1))
