"""
Best-effort script to import MyTurn CSV exports into a SQLite
database file for working with SQL queries.
"""

import sqlite3
import csv
import os
import sys

csv.field_size_limit(sys.maxsize)


os.unlink("data/myturn.db")

conn = sqlite3.connect("data/myturn.db")
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS members (
        id TEXT PRIMARY KEY,
        membership_type TEXT,
        confirmed BOOLEAN NOT NULL,
        created_at TIMESTAMP,
        note TEXT,
        warning TEXT
    );
    """
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS items (
        id TEXT PRIMARY KEY,
        item_type TEXT,
        name TEXT,
        description TEXT,
        dimensions TEXT,
        featured BOOLEAN,
        floating BOOLEAN,
        historical_cost REAL,
        location_code TEXT,
        admin_notes TEXT,
        manufacturer TEXT,
        model TEXT,
        now_buffer_days INTEGER,
        price_to_purchase REAL,
        product_code TEXT,
        publisher TEXT,
        purchased BOOLEAN,
        replacement_cost REAL,
        date_created TIMESTAMP,
        date_last_edited TIMESTAMP,
        date_last_updated TIMESTAMP,
        wish_list BOOLEAN,
        lost_by_member BOOLEAN,
        disabled BOOLEAN,
        in_maintenance BOOLEAN,
        lost_in_shop BOOLEAN,
        shop_use_only BOOLEAN,
        not_fixable BOOLEAN
    );
"""
)

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS checkouts (
        id INTEGER PRIMARY KEY,
        membership_id TEXT,
        item_id TEXT,
        checked_out TIMESTAMP,
        checked_in TIMESTAMP,
        due_date TIMESTAMP,
        renewals INTEGER,

        FOREIGN KEY (membership_id) REFERENCES members(id),
        FOREIGN KEY (item_id) REFERENCES items(id)
    );
    """
)


with open("data/processed/users.csv", "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute(
            """
            INSERT INTO members (id, membership_type, confirmed, created_at, note, warning)
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                row["Membership ID"],
                row["Current Membership Type"],
                row["Confirmed?"] == "True",
                row["Created"],
                row["User Note"],
                row["User Warning"],
            ),
        )

with open("data/processed/inventory.csv", "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute(
            """
            INSERT INTO items (
            id, 
            item_type, 
            name, 
            description, 
            dimensions, 
            featured, 
            floating, 
            historical_cost, 
            location_code, 
            admin_notes, 
            manufacturer, 
            model, 
            now_buffer_days, 
            price_to_purchase, 
            product_code, 
            publisher, 
            purchased, 
            replacement_cost, 
            date_created, 
            date_last_edited, 
            date_last_updated, 
            wish_list, 
            lost_by_member, 
            disabled, 
            in_maintenance, 
            lost_in_shop, 
            shop_use_only, 
            not_fixable
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                row["Item ID"],
                row["Item Type"],
                row["Name"],
                row["Description"],
                row["Dimensions (WxHxD)"],
                row["Featured"],
                row["Floating"],
                row["Historical Cost"],
                row["Location Code"],
                row["Admin Notes"],
                row["Manufacturer"],
                row["Model"],
                row["Now Buffer Days"],
                row["Price to Purchase"],
                row["Product Code / UPC"],
                row["Publisher"],
                row["Purchased"],
                row["Replacement Cost"],
                row["Date Created"],
                row["Date Last Edited"],
                row["Date Last Updated"],
                row["Wish List"],
                row["Lost By Member"],
                row["Disabled"],
                row["In Maintenance"],
                row["Lost In Shop"],
                row["Shop Use Only"],
                row["Not Fixable"],
            ),
        )

with open("data/processed/loans.csv", "r") as f:
    reader = csv.DictReader(f)

    for row in reader:
        cur.execute(
            """
            INSERT INTO checkouts (
                membership_id,
                item_id,
                checked_out,
                checked_in,
                due_date,
                renewals
            )
            VALUES (?, ?, ?, ?, ?, ?);
            """,
            (
                row["Membership ID"],
                row["Item ID"],
                row["Checked Out"],
                row["Checked In"],
                row["Due Date"],
                row["Renewals"],
            ),
        )

conn.commit()
conn.close()
