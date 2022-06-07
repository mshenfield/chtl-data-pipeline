#!/usr/bin/env python
"""CLI to download data and run the processing pipeline."""
import click
import os

from download import download as _download
from anonymize import anonymize as _anonymize

@click.group()
def cli():
    pass


@cli.command()
@click.option('--subdomain', required=True, help='The MyTurn subdomain for your library (the "yourlib" part of "yourlib.myturn.com").')
@click.option('--username', prompt='MyTurn username', show_envvar=True, required=True, help='The username used to log into MyTurn.')
@click.option('--password', prompt='MyTurn password', hide_input=True, show_envvar=True, required=True, help='The password use to log into MyTurn. If not provided by environment variable or by flag, it will be prompted. Prefer using the prompt or the environment variable for security.')
@click.option('--output_directory', type=str, required=True, default='input_with_peronal_info', help='The directory to save downloaded files to.')
@click.option('--download_past_years', default=False, show_default=True, help='Whether to download loans and transactions from previous years in addition to the current year. This should only be used once, when initially importing data.')
def download(subdomain, username, password, output_directory, download_past_years):
    """Download input reports from MyTurn to the input_with_personal_info/ directory."""
    _download(subdomain, username, password, output_directory, download_past_years)

@cli.command()
@click.option('--input_directory', type=str, required=True, help='The directory to read non-anonymized data from.')
@click.option('--output_directory', type=str, required=True, help='The directory to output anonymize data to.')
def anonymize(input_directory, output_directory):
    """Anonymize input data downloaded from the download command and save it to a new directory."""
    _anonymize(input_directory, output_directory)

if __name__ == '__main__':
    cli(auto_envvar_prefix='MYTURN')
