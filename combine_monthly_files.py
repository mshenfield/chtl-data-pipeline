#!/usr/bin/env python3
"""Standalone script to combine monthly chunk files into yearly files.

This script can be used to combine existing monthly files without re-downloading.
"""

import argparse
import glob
import os
from pathlib import Path


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
    # Find all monthly files for this year and prefix in chunks directory
    pattern = f"{chunks_dir}/{file_prefix}{year}-*.csv"
    monthly_files = sorted(glob.glob(pattern))
    
    if not monthly_files:
        print(f"No monthly files found for pattern: {pattern}")
        return None
    
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


def main():
    parser = argparse.ArgumentParser(description="Combine monthly chunk files into yearly files")
    parser.add_argument("output_dir", help="Output directory (should contain downloads/ and downloads/chunks/ subdirectories)")
    parser.add_argument("--file-prefix", help="File prefix to combine (e.g., 'loans-', 'transactions-')")
    parser.add_argument("--year", type=int, help="Year to combine files for")
    parser.add_argument("--all-years", action="store_true", help="Combine all years found")
    parser.add_argument("--all-prefixes", action="store_true", help="Combine all prefixes found")
    
    args = parser.parse_args()
    
    downloads_dir = f"{args.output_dir}/downloads"
    chunks_dir = f"{args.output_dir}/downloads/chunks"
    
    if not os.path.exists(downloads_dir):
        print(f"Error: Downloads directory '{downloads_dir}' not found")
        return 1
    
    if not os.path.exists(chunks_dir):
        print(f"Error: Chunks directory '{chunks_dir}' not found")
        return 1
    
    if args.all_prefixes and args.all_years:
        # Find all monthly files and group them
        pattern = f"{chunks_dir}/*-*-*.csv"
        monthly_files = glob.glob(pattern)
        
        # Group by prefix and year
        groups = {}
        for file_path in monthly_files:
            filename = os.path.basename(file_path)
            # Extract prefix and year from filename like "loans-2024-01.csv"
            parts = filename.split('-')
            if len(parts) >= 3:
                prefix = parts[0] + '-'
                year = int(parts[1])
                key = (prefix, year)
                if key not in groups:
                    groups[key] = []
                groups[key].append(file_path)
        
        # Combine each group
        for (prefix, year), files in groups.items():
            if len(files) > 1:  # Only combine if there are multiple files
                combine_monthly_files(chunks_dir, downloads_dir, prefix, year)
            else:
                print(f"Only one file found for {prefix}{year}, skipping combination")
    
    elif args.file_prefix and args.year:
        # Combine specific prefix and year
        combine_monthly_files(chunks_dir, downloads_dir, args.file_prefix, args.year)
    
    elif args.file_prefix and args.all_years:
        # Find all years for this prefix
        pattern = f"{chunks_dir}/{args.file_prefix}*-*.csv"
        monthly_files = glob.glob(pattern)
        
        years = set()
        for file_path in monthly_files:
            filename = os.path.basename(file_path)
            parts = filename.split('-')
            if len(parts) >= 3:
                year = int(parts[1])
                years.add(year)
        
        for year in sorted(years):
            combine_monthly_files(chunks_dir, downloads_dir, args.file_prefix, year)
    
    else:
        print("Error: Please specify either --file-prefix and --year, or use --all-prefixes and --all-years")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
