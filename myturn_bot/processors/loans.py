from datetime import datetime
import os
import pandas as pd

from ._formats import MYTURN_DATE_FORMAT, MYTURN_DATETIME_FORMAT
from ..chtl import OPEN_YEARS


def _read_loans_csv(filepath):
    """Call pd.read_csv with appropriate options and file prefix."""
    return pd.read_csv(
        filepath,
        # Excludes colums redundant with another table.
        usecols=(
            "Membership ID",
            "Item ID",
            "Checked Out",
            "Checked In",
            "Due Date",
            "Late Fees to Date",
            "Renewal",
        ),
        dtype={
            # Typically a number, but members can choose their own, e.g. "t00ln00b"
            "Membership ID": "string",
            # I manually modified two loans in loans-2017 that had "Item ID": "Drill" to use ID 517, rest should be Int64.
            # Without an explicit type, some files parse the "Item ID" as a number, some as a string.
            "Item ID": "Int64",
            "Renewal": "string",
            # 'Late Fees to Date' is specified in converters
        },
        # Convert "$0.00" strings to actual numbers
        converters={"Late Fees to Date": lambda x: float(x.replace("$", ""))},
        parse_dates=["Checked Out", "Checked In", "Due Date"],
        date_format={
            "Checked Out": MYTURN_DATETIME_FORMAT,
            "Checked In": MYTURN_DATETIME_FORMAT,
        },
    )


def process(input_dir, output_dir, filename):
    print("Processing loans")
    # Combine the completed loans from each year and any outstanding loans into a single dataframe.
    raw_loans = pd.concat(
        [_read_loans_csv(f"{input_dir}/{filename}{year}.csv") for year in OPEN_YEARS]
        # TODO: Tighten this up.
        + [_read_loans_csv(f"{input_dir}/{filename}checked-out.csv")]
    )
    # Rename "Late Fees to Date" to "Late Fees To Date" for consistency
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

    by_member_item = raw_loans.groupby(["Membership ID", "Item ID"])

    acc = []

    def consolidated_loan(first_loan, last_loan, renewals):
        """Uses the first_loan row, but populate renewal information"""
        loan = first_loan.copy()
        # We don't need the old "Renewals" column that tells us whether it's a renewal or not,
        # since we're combing a loan and its renewals into a single loan row
        del loan["Renewal"]
        # A new "Renewals" column has the # of times the loan was renewed
        loan["Renewals"] = renewals
        # The check in date of the loan becomes the check in of it's final renewal
        loan["Checked In"] = last_loan["Checked In"]
        # And any late fees
        loan["Late Fees To Date"] = last_loan["Late Fees To Date"]
        # And use the latest due date
        loan["Due Date"] = last_loan["Due Date"]
        return loan

    for (member_id, item_id), loans in by_member_item:
        renewals = 0
        init_loan = prev_loan = loans.iloc[0]

        for ix, loan in list(loans.iterrows())[1:]:
            if loan["Checked Out"].date() == prev_loan["Checked In"].date():
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

    # Dump consolidated loans to a CSV and Pickle
    loans.to_csv(
        f"{output_dir}/loans.csv",
        # Don't include the row labels, which are just the position of the row in the original file.
        index=False,
    )
    loans.to_pickle(f"{output_dir}/loans.pkl")

    # Create a list of "Checkouts". Each checkout is a user checking out a group of items. This can be helpful to avoid
    # over-counting when users make a lot of loans.
    checkouts = (
        loans.groupby(["Membership ID", "Checked Out"])
        .size(
            # Make the multiindex a column, and give the size column ("0") a proper name
        )
        .reset_index()
        .rename(columns={0: "Item Count"})
    )

    checkouts.to_csv(f"{output_dir}/checkouts.csv", index=False)
    checkouts.to_pickle(f"{output_dir}/checkouts.pkl")
    print("loans complete")
