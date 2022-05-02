#!/usr/bin/env python
"""
Loads each CSV in the "input_with_personal_info" folder, drops and personal info columns, and copies them to the "input" folder.

This makes some data in "input" folder look a little weird. For example, ints (1, 53) are turned into decimals (1.0, 53.0).
"""
import glob
from os import path
import pandas as pd

# List the cols we want instead of the the ones we think contain
# sensitive info. MyTurn occasionally changes column names, and this makes
# sure we don't accidentally start including personal info if the col name
# changes.

CHECKED_OUT_LOANS_COLS = (
    "Loan ID","Membership ID","Item ID","Item Name","Checked Out",
    "Checked In","Due Date","Check Out Location","Check In Location",
    "Late Fees to Date","Renewal",
)

# All the columns. List of columns last checked for completeness in April, 2022
INVENTORY_COLS = (
    "Item ID","Item Type","Status(es)","Name","Additional Image","Agreement that must be signed to checkout the item",
    "Amount / Fee","Attachment","Author","Between Buffer Days","Categories","Color","Condition","Daily Late Fee","Date Purchased",
    "Default Loan Length","Description","Dimensions (WxHxD)","Eco Rating","Embodied Carbon","Emission Factor","Featured",
    "Floating","Goes Home","Grace period on late fees (in days)","Historical Cost","Image","Keywords","Location Code","Maintenance",
    "Maintenance Plans","Manufacturer","Max Frequency","Max Frequency Units","Max Output","Maximum number of renewals",
    "Maximum number that may be reserved","Maximum percentage of inventory that may be reserved","Maximum Reservation Length",
    "Min Frequency","Min Frequency Units","Model","Now Buffer Days","Price to Purchase","Product Code / UPC","Publisher",
    "Purchased","Replacement Cost","Serial Number","Size","Source / Supplier","Tax(es)","Transfer Buffer Days","Weight",
    "Date Created","Date Last Edited","Date Last Updated",
)

ITEM_TYPE_COLS = ("Type","Parent Type","Full Hierarchy",)

LOAN_COLS = (
    "Membership ID","Item ID","Item Name","Checked Out","Checked In",
    "Due Date","Late Fees to Date","Renewal",
)

OUTSTANDING_BALANCE_COLS = ("ID","Amount",)

# Some notes on any excluded here that isn't obviously personal info:
# * Unconfirmed Email - not sure what it is, but excluding just in case.
# * Username - pretty easy to figure out who someone is based on their username.
# * Address Notes - sometimes actually include the member's address.
USER_COLS = (
    "Member ID","Confirmed?","Sex","Age","Member Created (M/D/YYYY)","Start of first full membership (M/D/YYYY)","Current Membership Type",
    "Latest Membership Change (request, upgrade, renewal, cancellation...) (M/D/YYYY)","Current Membership Expiration (M/D/YYYY)",
    "Renews Automatically","Automatically Pay Statements","User Note","User Warning","Opening Balance","Opening Balance Date (M/D/YYYY)",
    "Household Type","Single, non-elderly","Elderly","Single Parent","Two Parents","Female Head of Household","Household income range",
    "Household income range Value","Ethnicity","American Indian or Alaskan Native","Asian","Black or African American","Hispanic","White",
    "Native Hawaiian or Pacific Islander","Other","Number of disabled people in household","Renter/Homeowner","Renter/Homeowner Value",
    "Household Size",
)

# "Handled By" includes the admin username that handled things. It's fairly
# useful to include these, so I'm including the column here, and only
# including the first three letters of the col below.
TRANSACTION_COLS = (
    "Transaction ID","Member ID","Date","Payment Method","Payment Amount","Discount","On Account","Transaction Amount","Amount Due",
    "Amount Paid","Type","Amount Due For Line Item","Actual Paid","Item ID","Item Name","Membership Type","Applicable Taxes",
    "Project ID","Project Name","Handled By","Notes","Renewal",
)

def copy_to_input_with_cols(f, cols):
    """Copies the file from "input_with_personal_info" to "input", keeping the specified columns."""
    df = pd.read_csv(f'input_with_personal_info/{f}', usecols=cols,)
    # Drop the auto-generated row number index
    df.to_csv(f'input/{f}', index=False)

if __name__ == '__main__':        
    copy_to_input_with_cols('loans-checked-out.csv', CHECKED_OUT_LOANS_COLS)

    copy_to_input_with_cols('inventory-snapshot.csv', INVENTORY_COLS)    

    copy_to_input_with_cols('item-types.csv', ITEM_TYPE_COLS)    
    
    # Include the "-2" to avoid "loans-checked-out"
    for f in glob.glob('loans-2*.csv', root_dir='input_with_personal_info'):
        copy_to_input_with_cols(f, LOAN_COLS) 

    copy_to_input_with_cols('outstanding-balances.csv', OUTSTANDING_BALANCE_COLS)

    for f in ('users-snapshot.csv', 'admin-users-snapshot.csv'):
        copy_to_input_with_cols(f, USER_COLS)

    for f in glob.glob('transactions-*.csv', root_dir='input_with_personal_info'):
        # Copied from the helper, with some special handling to include only the first three letters of the "Handled By"
        # username.
        df = pd.read_csv(
            f'input_with_personal_info/{f}', usecols=TRANSACTION_COLS,
            converters={'Handled By': lambda s: s[:3]},
        )
        df.to_csv(f'input/{f}', index=False)

    # Double check we've processed all csv file in "input_with_personal_info"
    for f in glob.glob('*.csv', root_dir='input_with_personal_info'):
        if not path.exists(f'input/{f}'):
           raise AssertionError(f'There is no copy of {f} in "input". Add some handling for it to the script.')
    
    # Also make sure there aren't files in "input" that aren't in "input_with_personal_info"
    for f in glob.glob('*.csv', root_dir='input'):
        if not path.exists(f'input_with_personal_info/{f}'):
            raise AssertionError(f'A copy of {f} from "input" that looks like it was not anonymized.'
                                 'Move it to "input_with_personal_info" and remove any personal info columns using that script')