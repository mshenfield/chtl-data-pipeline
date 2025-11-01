"""Download data and run the processing pipeline."""

from dataclasses import dataclass
from enum import auto, Enum
import os
from datetime import datetime, date
from typing import List, Tuple

from .bot import MyTurnBot
from . import paths
from .processors.item_types import process as process_item_types
from .processors.inventory import process as process_inventory
from .processors.loans import process as process_loans
from .processors.transactions import process as process_transactions
from .processors.users import process as process_users


def generate_monthly_ranges(year: int) -> List[Tuple[date, date]]:
    """Generate monthly date ranges for a given year.
    
    Args:
        year: The year to generate monthly ranges for
        
    Returns:
        List of tuples containing (start_date, end_date) for each month
    """
    monthly_ranges = []
    for month in range(1, 13):  # 1 to 12
        # First day of the month
        start_date = date(year, month, 1)
        
        # Last day of the month
        if month == 12:
            end_date = date(year + 1, 1, 1) - date.resolution
        else:
            end_date = date(year, month + 1, 1) - date.resolution
            
        monthly_ranges.append((start_date, end_date))
    
    return monthly_ranges


def combine_monthly_files(chunks_dir: str, downloads_dir: str, file_prefix: str, year: int) -> str:
    """Combine monthly chunk files into a single yearly file.
    
    Args:
        chunks_dir: Directory containing the monthly chunk files
        downloads_dir: Directory where the combined file should be saved
        file_prefix: Prefix of the files to combine (e.g., "loans-", "transactions-")
        year: The year to combine files for
        
    Returns:
        Path to the combined file
    """
    import glob
    
    # Find all monthly files for this year and prefix in chunks directory
    pattern = f"{chunks_dir}/{file_prefix}{year}-*.csv"
    monthly_files = sorted(glob.glob(pattern))
    
    if not monthly_files:
        raise FileNotFoundError(f"No monthly files found for pattern: {pattern}")
    
    # Create the combined filename in downloads directory
    combined_filename = f"{file_prefix}{year}.csv"
    combined_path = f"{downloads_dir}/{combined_filename}"
    
    # Combine the files
    with open(combined_path, 'w') as outfile:
        for i, file_path in enumerate(monthly_files):
            with open(file_path, 'r') as infile:
                # Skip header for all files except the first
                if i > 0:
                    next(infile)
                outfile.write(infile.read())
    
    print(f"Combined {len(monthly_files)} monthly files into {combined_filename}")
    return combined_path


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
    chunk_by_month: bool = True
    combine_monthly_chunks: bool = True


# TODO: PipelineConfig class?
def pipeline(
    output_dir,
    myturn_subdomain,
    myturn_username,
    myturn_password,
    stages,
    myturn_files,
    years,
    chunk_by_month,
    combine_monthly_chunks=True,
):
    if not os.path.exists(output_dir):
        raise ValueError(f"Directroy '{output_dir}' not found")

    downloads_dir = f"{output_dir}/downloads"
    chunks_dir = f"{output_dir}/downloads/chunks"
    processed_dir = f"{output_dir}/processed"

    if Stages.DOWNLOAD in stages:
        bot = MyTurnBot(myturn_subdomain)
        bot.start_session(myturn_username, myturn_password)

        def download(bot, myturn_path, d, f):
            # The timeout is timeout-to-first-byte, not for the download to complete.
            # 5 minutes should be more than enough, and future proof as our transaction
            # volume increases.
            r = bot.get(myturn_path, timeout=600, allow_redirects=False)
            if r.status_code != 200:
                raise Exception(
                    f"Unexpected status received for report {f}. Response: {r.status_code} {r.headers} {r.text}"
                )
            with open(f"{d}/{f}.csv", "w") as f:
                f.write(r.text)

        os.makedirs(downloads_dir, exist_ok=True)
        if chunk_by_month:
            os.makedirs(chunks_dir, exist_ok=True)
        for myf in myturn_files:
            if myf == MyTurnFiles.LOANS or myf == MyTurnFiles.TRANSACTIONS:
                for year in years:
                    if chunk_by_month:
                        # Download monthly chunks to chunks directory
                        monthly_ranges = generate_monthly_ranges(year)
                        for month_idx, (start_date, end_date) in enumerate(monthly_ranges, 1):
                            if myf == MyTurnFiles.LOANS:
                                path = paths.loans_report_path_monthly(start_date, end_date)
                            else:  # TRANSACTIONS
                                path = paths.transactions_report_path_monthly(start_date, end_date)
                            
                            filename = f"{myf.filename}{year}-{month_idx:02d}"
                            print(f"Downloading {filename} ({start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')})...")
                            download(bot, path, chunks_dir, filename)
                            print(f"{filename} download complete")
                    else:
                        # Download entire year at once (original behavior)
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

    # Combine monthly files if chunking was used and combination is enabled
    if chunk_by_month and combine_monthly_chunks and Stages.DOWNLOAD in stages:
        print("Combining monthly files into yearly files...")
        for myf in myturn_files:
            if myf == MyTurnFiles.LOANS or myf == MyTurnFiles.TRANSACTIONS:
                for year in years:
                    try:
                        combine_monthly_files(chunks_dir, downloads_dir, myf.filename, year)
                    except FileNotFoundError as e:
                        print(f"Warning: {e}")

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
