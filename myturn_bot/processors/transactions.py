from datetime import date
import re
import pandas as pd

from ._myturn_formats import MYTURN_DATETIME_FORMAT
from ..chtl import OPEN_YEARS

# Match everything but the number in of "$1.01" or "($1.01)"
_balance_pattern = re.compile(r"[\$\(\)]")


def _balance_to_float(balance_string):
    """
    Converts a balance in the format "$1.01" or "($1.01)" to a float.

    Positive balances (indicated by wrapped parens) are returned as negative numbers - most money we get is unwrapped.
    """
    # It's a bit easier to treat positive balances as negative numbers in this context,
    # since we're thinking about it in terms of amount owed.
    #
    # Positive balances are wrapped in parens, e.g. ($10.20)
    if not balance_string:
        return 0.0

    sign = -1 if balance_string.startswith("(") else 1
    # Strip everything but the number.
    number_string = _balance_pattern.sub("", balance_string)
    return sign * float(number_string)


def _read_transactions_csv(input_dir, filename):
    """Call pd.read_csv with appropriate options and file prefix."""
    money_cols = (
        "Payment Amount",
        "Discount",
        "On Account",
        "Transaction Amount",
        "Amount Due",
        "Amount Paid",
        "Amount Due For Line Item",
        "Actual Paid",
    )
    return pd.read_csv(
        f"{input_dir}/{filename}",
        # Excludes colums redundant with another table.
        usecols=(
            "Transaction ID",
            "Member ID",
            "Date",
            "Payment method",
            "Payment Amount",
            "Discount",
            "On Account",
            # "Item Type" is actually the "Transaction Type" - confusing.
            "Transaction Amount",
            "Amount Due",
            "Amount Paid",
            "Item Type",
            "Amount Due For Line Item",
            "Actual Paid",
            "Item ID",
            "Membership Type",
            "Handled By",
            "Notes",
            "Renewal",
        ),
        dtype={
            # Typically a number, but members can choose their own, e.g. "t00ln00b"
            "Member ID": "string",
            # I manually modified two loans in loans-2017 that had "Item ID": "Drill" to use ID 517, rest should be Int64.
            # Without an explicit type, some files parse the "Item ID" as a number, some as a string.
            "Item ID": "Int64",
            # For some reason this pops up as an object
            "Item Type": "string",
        },
        # Convert "$0.00" strings to actual numbers
        converters={col: _balance_to_float for col in money_cols},
        parse_dates=["Date"],
        date_format={"Date": MYTURN_DATETIME_FORMAT},
    )


def process(input_dir, output_dir, filename):
    print(f"Processing transactions")
    raw_transactions = pd.concat(
        [
            _read_transactions_csv(input_dir, f"{filename}{year}.csv")
            for year in OPEN_YEARS
        ]
    ).reset_index()

    # "Item Type" is only set for the first row in a sequence of transactions.
    # Use the initial value for each row for forward fill until the next value.
    raw_transactions["Item Type"] = raw_transactions["Item Type"].fillna(
        method="ffill", inplace=True
    )

    raw_transactions.to_csv(f"{output_dir}/{filename}.csv")
    raw_transactions.to_pickle(f"{output_dir}/{filename}.pkl")
    print(f"transactions complete")
