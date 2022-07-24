# This is a removed scrip that calculates the number of accounts in
# a "requested", "active" (came in and signed up), or "expired" state
#
# This actually isn't very helpful, since "expired" isn't a useful state,
# it just indicates the user hasn't checked out something within the last 2
# years. The one thing this data showed was that the request
# count was consistent throughout the pandemic, but that fewere people came
# in to activate their pending membership. But we could figure that
# out with a lot fewer steps.

# A stacked area chart sorted by that shows count of members by status over time
#
# Statuses include "Requested" (signed up online but haven't come in), "Active" (came in and have an un-expired membership)
# and "Expired" (haven't renewed their membership since it expired).
#
# TODO: Change column names "Created" to "Requested", "First Membership" to "Activated" in base df
import pandas as pd
from datetime import date

members = pd.read_pickle('data/output/members.pkl')

# TODO: Move this to 01_members.py
#
# Fill in the gender as "would rather not say" for now for no response. Avoids kerfuffles below.
members['Sex'] = regular_members['Sex'].fillna('would rather not say')

date_range = pd.date_range(start='2015-10-01', end=date.today(), freq='D')

# Set boundaries by setting the dates. Got to be a better way :C
requested = []
activated = []
expiration = []

for _, member in members.iterrows():
    requested.append({'increment': 1, 'date': member['Created']})
    if not pd.isna(member['First Membership Started']):
        requested.append({'increment': -1, 'date': member['First Membership Started']})
        activated.append({'increment': 1, 'date': member['First Membership Started']})

    if not pd.isna(member['Expiration']):
        activated.append({'increment': -1, 'date': member['Expiration']})
        expiration.append({'increment': 1, 'date': member['Expiration']})

def get_running_total(date_increments):
    # At each date, do increment/decrement by summing, then cumsum to get the running total
    df = pd.DataFrame(date_increments).groupby('date').sum().cumsum()
    # Reindex to our specified date range, using the previous value for the next
    return df.reindex(date_range, method='ffill')

requests_on_date = get_running_total(requested)
active_on_date = get_running_total(activated)
expired_on_date = get_running_total(expiration)

status_count_on_date = pd.DataFrame({
    'Requested': requests_on_date['increment'],
    'Active': active_on_date['increment'],
    'Expired': expired_on_date['increment'],
    },
)

status_count_on_date.describe().applymap(int)