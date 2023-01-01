# Analysis scripts

This directory contains scripts that run one-time analyses on the contents of the root `data/output` directory.

## Contents

### `most_popular_hours.sh`

Determine which hours of which days are most popular for checkouts at the tool library. Useful for potentially adjusting which hours we decide to staff.

Input: `checkouts.csv`

Output: `stdout` CSV-format text with the columns `dow`, `minutes_after_opening`, and `half_hour`. Can be quickly visualized as histograms using pivot tables in your spreadsheet of choice.

### clear_personal_info.ipynb

Powerful stuff. Clears everything but email and phone number from member accounts.