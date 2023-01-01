"""Run all stages in the pipeline."""
from datetime import date
from re import split
import pandas as pd

def process(input_directory, output_directory):
    """Process input data, outputing the final result to an output directory."""
    inventory_csv_path = _inventory(input_directory, output_directory)
    loans_csv_path = _loans_and_checkouts(input_directory, output_directory)
    

def _inventory(input_directory, output_directory):
    """Generate a nicely formatted inventory table."""
    raw_inventory = pd.read_csv(
        f'{input_directory}/inventory-snapshot.csv',
        dtype={
            # "Item Type" is categorical, and so is "Location Code" when labeled fastidiously
            'Item Type': 'category',
            'Location Code': 'category',
        },
        parse_dates=['Date Created'],
        converters={
            # "Status(es)" is a CSV of possible statuses.
            'Status(es)': lambda s: frozenset() if s == '' else frozenset(s.split(',')),
            # "Keywords" are space or comma separated lists of arbitrary words
            'Keywords': lambda k: frozenset(split('[, ]', k))
        }
    )
    inventory = pd.DataFrame(raw_inventory)
    for status in {'Disabled', 'In Maintenance', 'Shop Use Only', 'Wish List'}:
        inventory[status] = raw_inventory['Status(es)'].map(lambda s: status in s)

    del inventory['Status(es)']
    inventory.to_csv(f'{output_directory}/inventory.csv', index=False)
    inventory.to_pickle(f'{output_directory}/inventory.pkl')
    return f'{output_directory}/inventory.csv'

def _loans_and_checkouts(input_directory, output_directory):
    """Combine the completed loans from each year and any outstanding loans into a single dataframe."""
    current_year = date.today().year

    def read_loans_csv(filename):
        """Call pd.read_csv with appropriate options and file prefix."""
        return pd.read_csv(
            f'{input_directory}/{filename}',
            # Excludes colums redundant with another table.
            usecols=('Membership ID', 'Item ID', 'Checked Out', 'Checked In', 'Due Date', 'Late Fees to Date', 'Renewal'),
            dtype={
                # Typically a number, but members can choose their own, e.g. "t00ln00b"
                'Membership ID': 'string',
                # I manually modified two loans in loans-2017 that had "Item ID": "Drill" to use ID 517, rest should be Int64.
                # Without an explicit type, some files parse the "Item ID" as a number, some as a string.
                'Item ID': 'Int64',
                'Renewal': 'string',
                # 'Late Fees to Date' is specified in converters
            },
            # Convert "$0.00" strings to actual numbers
            converters={'Late Fees to Date': lambda x: float(x.replace("$", ""))},
            # 'Checked Out'. 'Checked In', 'Due Date'
            parse_dates=[2, 3, 4])

    raw_completed_loans = pd.concat([
        read_loans_csv(f'loans-{year}.csv')
        for year in range(2016, current_year + 1)
    ])

    raw_loans = pd.concat([raw_completed_loans, read_loans_csv('loans-checked-out.csv')])

    # Rename "Late Fees to Date" to "Late Fees T̲o Date" for consistency
    raw_loans.rename(columns={"Late Fees to Date": "Late Fees To Date"}, inplace=True)

    # Fill "Initial" for "Renewal" <NA> values
    # We don't need this b/c we deleted the "Renewal" column in the "consolidated_loans", and
    # remove the col, but keep this to save some re-discovery in case we want to use "Renewal" again.
    # raw_loans.fillna(value={"Renewal": "Initial"}, inplace=True)

    # Only use one Loan row to represent a member checking out an item, now matter how many times
    # they renew.
    #
    # If an item is checked out again by the same user on the same day they return it, it is considered
    # a renewal. We could just use the "Renewal" field, but sometimes users fully check things in,
    # then immediately check them out again, and we want to treat that as renewal as well.
    #
    # TODO: Speed up using itertuples(), docs say iterrows is slow

    by_member_item = raw_loans.groupby(['Membership ID', 'Item ID'])

    acc = []

    for (member_id, item_id), loans in by_member_item:
        renewals = 0
        init_loan = prev_loan = loans.iloc[0]

        def consolidated_loan(first_loan, last_loan, renewals):
            """Uses the first_loan row, but populate renewal information"""
            loan = first_loan.copy()
            # We don't need the "Renewals" column that tells us whether it's a renewal or not,
            # since we're combing a loan and its renewals into a single loan row
            del loan['Renewal']
            # A new "Renewals" row includes the # of times the loan was renewed
            loan['Renewals'] = renewals
            # The check in date of the loan becomes the check in of it's final renewal
            loan['Checked In'] = last_loan['Checked In']
            # And any late fees
            loan['Late Fees To Date'] = last_loan['Late Fees To Date']
            # And use the latest due date
            loan['Due Date'] = last_loan['Due Date']
            return loan

        for ix, loan in list(loans.iterrows())[1:]:
            if loan['Checked Out'].date() == prev_loan["Checked In"].date():
                renewals += 1
                prev_loan = loan
            else:
                # We've come to a new loan for the same member and item. Append
                # the previous one to our list with the new renewal info.
                acc.append(consolidated_loan(init_loan, prev_loan, renewals))
                # Reset to this new loan
                renewals = 0
                init_loan = prev_loan = loan

        # The loop above doesn't do anything for the last item - handle it here.
        acc.append(consolidated_loan(init_loan, prev_loan, renewals))

    # The index initially corresponds to the position in each file.  To avoid duplicate index
    # entries, reset so the index is the position of the row in the entire table.
    loans = pd.DataFrame(acc).reset_index()

    loans.to_csv(
        f'{output_directory}/loans.csv',
        # Don't include the row labels, which are just the position of the row in the original file.
        index=False,
    )
    loans.to_pickle(f'{output_directory}/loans.pkl')
    
    # Create a list of "Checkouts". Each checkout is a user checking out a group of items. This can be helpful to avoid
    # over-counting when users make a lot of loans.
    checkouts = loans.groupby(['Membership ID', 'Checked Out']).size(
    # Make the multiindex a column, and give the size column ("0") a proper name
    ).reset_index().rename(columns={0: 'Item Count'})

    checkouts.to_csv(f'{output_directory}/checkouts.csv', index=False)
    checkouts.to_pickle(f'{output_directory}/checkouts.pkl')
    return f'{output_directory}/loans.csv', f'{output_directory}/checkouts.csv'