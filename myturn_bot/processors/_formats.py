"""Shared constants and helpers related to MyTurn data (e.g. their default date format).

Formats are strftime formats:
https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
"""

# e.g. 10/12/2019
# The "%-d" is day of month w/out zero padding
MYTURN_DATE_FORMAT = "%m/%d/%Y"
# e.g. 8/24/2016 7:02 PM
# %-I is the hour without zero padding
MYTURN_DATETIME_FORMAT = f"{MYTURN_DATE_FORMAT} %I:%M %p"
