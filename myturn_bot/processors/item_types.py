from collections import defaultdict
import pandas as pd


def itertuples(item_type_df):
    return item_type_df.rename(
        columns={"Type": "name", "Parent Type": "parent"},
    ).itertuples(index=False)


def process(input_dir, output_dir, filename):
    print(f"Processing {filename}")
    raw_item_types = pd.read_csv(
        f"{input_dir}/{filename}.csv",
        # Skip the "Full Hierarchy" column since we don't use it at the moment
        usecols=("Type", "Parent Type"),
    )
    # Remove 'root' row, since it's a bit weird
    item_types = raw_item_types.iloc[1:]

    item_types.to_csv(f"{output_dir}/{filename}.csv")
    item_types.to_pickle(f"{output_dir}/{filename}.pkl")
    print(f"{filename} complete")
