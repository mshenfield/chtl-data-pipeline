# Generate the members table.
import pandas as pd


def process(input_dir, output_dir, filename):
    print(f"Processing {filename}")
    raw_users = pd.read_csv(
        f"{input_dir}/{filename}.csv",
        # Only include extra information that is required on sign-up ('Age') or widely pouplated ('Gender')
        usecols=(
            # A handful of users have string Member IDs
            "Member ID",
            # Gender is filled for about 1/3rd of users, but isn't required anymore
            "Sex",
            # Age is required now, and filled for 2/3rds of users
            "Age",
            # Include Race columns - even though they're not frequently filled in, glean what we can
            "American Indian or Alaskan Native",
            "Asian",
            "Black or African American",
            "Hispanic",
            "White",
            "Native Hawaiian or Pacific Islander",
            "Other",
            "Confirmed?",
            "Member Created (M/D/YYYY)",
            "Start of first full membership (M/D/YYYY)",
            "Current Membership Type",
            "Latest Membership Change (request, upgrade, renewal, cancellation...) (M/D/YYYY)",
            "Current Membership Expiration (M/D/YYYY)",
            "User Note",
            "User Warning",
        ),
        parse_dates=[
            "Member Created (M/D/YYYY)",
            "Start of first full membership (M/D/YYYY)",
            "Latest Membership Change (request, upgrade, renewal, cancellation...) (M/D/YYYY)",
            "Current Membership Expiration (M/D/YYYY)",
        ],
        dtype={
            "Current Membership Type": "category",
            "Confirmed?": "boolean",
            "Age": "Int64",
        },
    )

    # For consistency with the loans column name
    users = raw_users.rename(
        columns={
            "Member ID": "Membership ID",
            "Member Created (M/D/YYYY)": "Created",
            "Start of first full membership (M/D/YYYY)": "First Membership Started",
            "Latest Membership Change (request, upgrade, renewal, cancellation...) (M/D/YYYY)": "Last Changed",
            "Current Membership Expiration (M/D/YYYY)": "Expiration",
        }
    )
    users["Sex"] = users["Sex"].fillna("unknown")

    users.to_csv(f"{output_dir}/{filename}.csv")
    users.to_pickle(f"{output_dir}/{filename}.pkl")
    print(f"{filename} complete")
