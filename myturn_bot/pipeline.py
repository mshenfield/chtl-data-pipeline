"""Download data and run the processing pipeline."""

from dataclasses import dataclass
from enum import auto, Enum
import os

from .bot import MyTurnBot
from . import paths
from .processors.item_types import process as process_item_types
from .processors.inventory import process as process_inventory
from .processors.loans import process as process_loans
from .processors.transactions import process as process_transactions
from .processors.users import process as process_users


class Stages(Enum):
    """The stages of the pipeline to run."""

    # Download the files from MyTurn.
    DOWNLOAD = auto()
    # Process the data into a more usable format and spit it into the output/ dirs
    PROCESS = auto()


class MyTurnFiles(Enum):
    """The files to download and process."""

    def __init__(self, filename, path):
        self.filename = filename
        self.path = path

    ADMIN_USERS = ("admin-users", paths.ADMIN_USERS_PATH)
    INVENTORY = ("inventory", paths.INVENTORY_PATH)
    ITEM_TYPES = ("item-types", paths.ITEM_TYPES_PATH)
    # TODO: Make this less magic?
    LOANS = ("loans-", paths.loans_report_path)
    TRANSACTIONS = ("transactions-", paths.transactions_report_path)
    USERS = ("users", paths.USERS_PATH)


@dataclass
class PipelineConfig:
    output_dir: str
    myturn_subdomain: str
    stages: list[Stages]
    myturn_files: list[MyTurnFiles]
    years: list[int]


# TODO: PipelineConfig class?
def pipeline(
    output_dir,
    myturn_subdomain,
    myturn_username,
    myturn_password,
    stages,
    myturn_files,
    years,
):
    if not os.path.exists(output_dir):
        raise ValueError(f"Directroy '{output_dir}' not found")

    downloads_dir = f"{output_dir}/downloads"
    processed_dir = f"{output_dir}/processed"

    if Stages.DOWNLOAD in stages:
        bot = MyTurnBot(myturn_subdomain)
        bot.start_session(myturn_username, myturn_password)

        def download(bot, myturn_path, d, f):
            # The timeout is timeout-to-first-byte, not for the download to complete.
            # 3 minutes should be more than enough, and future proof as our transaction
            # volume increases.
            r = bot.get(myturn_path, timeout=180, allow_redirects=False)
            if r.status_code != 200:
                raise Exception(
                    f"Unexpected status received for report {f}. Response: {r.status_code} {r.headers} {r.text}"
                )
            with open(f"{d}/{f}.csv", "w") as f:
                f.write(r.text)

        os.makedirs(downloads_dir, exist_ok=True)
        for myf in myturn_files:
            if myf == MyTurnFiles.LOANS or myf == MyTurnFiles.TRANSACTIONS:
                for year in years:
                    filename = f"{myf.filename}{year}"
                    print(f"Downloading {filename}...")
                    download(bot, myf.path(year), downloads_dir, filename)
                    print(f"{filename} download complete")
            else:
                print(f"Downloading {myf.filename}...")
                download(bot, myf.path, downloads_dir, myf.filename)
                print(f"{myf.filename} download complete")
            # TODO: Make this all in one config
            # For loans, also download the currently checked out loans
            if myf == MyTurnFiles.LOANS:
                filename = f"{myf.filename}checked-out"
                print(f"Downloading {filename}")
                download(bot, paths.CURRENTLY_CHECKED_OUT_PATH, downloads_dir, filename)

    if Stages.PROCESS in stages:
        os.makedirs(processed_dir, exist_ok=True)

        for myf in myturn_files:
            if myf == MyTurnFiles.ADMIN_USERS or myf == MyTurnFiles.USERS:
                process_users(downloads_dir, processed_dir, myf.filename)
            if myf == MyTurnFiles.INVENTORY:
                process_inventory(downloads_dir, processed_dir, myf.filename)
            if myf == MyTurnFiles.ITEM_TYPES:
                process_item_types(downloads_dir, processed_dir, myf.filename)
            if myf == MyTurnFiles.LOANS:
                # TODO: Make magic filename prefix less magical.
                process_loans(downloads_dir, processed_dir, myf.filename)
            if myf == MyTurnFiles.TRANSACTIONS:
                # TODO: Make magic filename prefix less magical.
                process_transactions(downloads_dir, processed_dir, myf.filename)
