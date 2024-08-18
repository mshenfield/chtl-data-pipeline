import pandas as pd
import re

from ._formats import MYTURN_DATE_FORMAT, MYTURN_DATETIME_FORMAT


def process(input_dir, output_dir, filename):
    print(f"Processing {filename}")
    raw_inventory = pd.read_csv(
        f"{input_dir}/{filename}.csv",
        dtype={
            # "Item Type" is categorical, and so is "Location Code" (when labeled fastidiously)
            "Item Type": "category",
            "Location Code": "category",
            "Item ID": "int64",
        },
        parse_dates=["Date Created", "Date Last Edited", "Date Last Updated"],
        converters={
            # "Status(es)" is a comma separated set of statuses on the item.
            "Status(es)": lambda s: (
                frozenset() if s == "" else frozenset(s.split(","))
            ),
            # "Keywords" are space or comma separated lists of arbitrary words
            "Keywords": lambda k: frozenset(re.split("[, ]", k)),
        },
    )

    inventory = pd.DataFrame(raw_inventory)
    # These are found/editable on the /library/orgMyOrganization/statusList settings page
    statuses = {
        "Disabled",
        "In Maintenance",
        "Shop Use Only",
        "Wish List",
        "Lost In Shop",
        "Lost By Member",
        "Not Fixable",
    }
    # Convert each status into it's own column and delete the "Status(es)" column because it's hard to use
    for status in set(s for statutes in inventory["Status(es)"] for s in statuses):
        inventory[status] = raw_inventory["Status(es)"].map(lambda s: status in s)

    del inventory["Status(es)"]
    inventory.to_csv(f"{output_dir}/{filename}.csv", index=False)
    inventory.to_pickle(f"{output_dir}/{filename}.pkl")
    print(f"{filename} complete")
