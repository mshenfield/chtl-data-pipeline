"""Functions to download CSV reports from MyTurn."""
from dataclasses import dataclass
import datetime as dt
import requests

from my_turn_bot import MyTurnBot


def download(my_turn_subdomain, username, password, output_directory='inputs_with_personal_info', download_past_years=False):
    """Download input reports from MyTurn to input_with_personal_info.

    myturn_url: the subdomain of MyTurn to use, e.g. "mylib" in "https://mylib.myturn.com"
    output_directory: the directory to download files to.
    download_past_years: if True, download loans and transactions from previous years in addition to the current year.
        This should only be used once, when initially importing data.
    """
    current_year = dt.date.today().year
 
    # The URL for a report can be grabbed by following instructions in README.md, opening the Developer Tools for your browser
    # of choice just before clicking the download link, opening the Network tab, clicking the download link, and
    # copying the URL shown in the Network tab.
    reports = (
        Report(filename='admin-users-snapshot', path='/library/orgMembership/exportUsers?format=csv&extension=csv&membershipTypeId=0&membershipExpiringAfter=struct&membershipExpiringAfter_tz=America%2FLos_Angeles&membershipExpiringAfter_time=00%3A00&membershipExpiringBefore=struct&membershipExpiringBefore_tz=America%2FLos_Angeles&membershipExpiringBefore_time=00%3A00&memberSinceAfter=struct&memberSinceAfter_tz=America%2FLos_Angeles&memberSinceAfter_time=00%3A00&memberSinceBefore=struct&memberSinceBefore_tz=America%2FLos_Angeles&memberSinceBefore_time=00%3A00&operatorsOnly=on&exportField=membership.attributes.membershipId&exportField=firstName&exportField=lastName&exportField=emailAddress&exportField=emailAddressConfirmed&exportField=unconfirmedEmailAddress&exportField=username&exportField=title&exportField=organizationName&exportField=address.street1&exportField=address.street2&exportField=address.city&exportField=address.principalSubdivision&exportField=address.postalCode&exportField=address.country.displayName&exportField=address.phone&exportField=address.phone2&exportField=address.notes&exportField=sex&exportField=age&exportField=firstName2&exportField=lastName2&exportField=emailAddress2&exportField=title2&exportField=organizationName2&exportField=address2.street1&exportField=address2.street2&exportField=address2.city&exportField=address2.principalSubdivision&exportField=address2.postalCode&exportField=address2.country.displayName&exportField=address2.phone&exportField=address2.phone2&exportField=address2.notes&exportField=membership.memberSince&exportField=firstFullMembershipStart&exportField=membershipType.name&exportField=latestMembershipPurchase&exportField=membershipExpiration&exportField=membership.autoRenews&exportField=autoPayStatements&exportField=attributes.latestNote&exportField=attributes.latestWarning&exportField=openingBalance&exportField=openingBalanceDate&exportField=dynamicFields.household_type&exportField=dynamicFields.income_range&exportField=dynamicFields.ethnicity&exportField=dynamicFields.disabled&exportField=dynamicFields.renter&exportField=dynamicFields.household_size'),
        Report(filename='inventory-snapshot', path='/library/orgInventory/report?format=csv&extension=csv&resolveValues=true&exportItemType=on&_exportItemType=true&exportDateCreated=on&_exportDateCreated=true&exportDateLastEdited=on&_exportDateLastEdited=true&exportDateLastUpdated=on&_exportDateLastUpdated=true&exportStatuses=on&_exportStatuses=true&selectedAttributes%5B0%5D=1&selectedAttributes%5B1%5D=15&selectedAttributes%5B2%5D=40&selectedAttributes%5B3%5D=8&selectedAttributes%5B4%5D=14&selectedAttributes%5B5%5D=58&selectedAttributes%5B6%5D=50&selectedAttributes%5B7%5D=13&selectedAttributes%5B8%5D=31&selectedAttributes%5B9%5D=4&selectedAttributes%5B10%5D=12&selectedAttributes%5B11%5D=29&selectedAttributes%5B12%5D=28&selectedAttributes%5B13%5D=2&selectedAttributes%5B14%5D=38&selectedAttributes%5B15%5D=52&selectedAttributes%5B16%5D=53&selectedAttributes%5B17%5D=54&selectedAttributes%5B18%5D=47&selectedAttributes%5B19%5D=55&selectedAttributes%5B20%5D=56&selectedAttributes%5B21%5D=46&selectedAttributes%5B22%5D=25&selectedAttributes%5B23%5D=6&selectedAttributes%5B24%5D=7&selectedAttributes%5B25%5D=16&selectedAttributes%5B26%5D=11&selectedAttributes%5B27%5D=48&selectedAttributes%5B28%5D=21&selectedAttributes%5B29%5D=35&selectedAttributes%5B30%5D=36&selectedAttributes%5B31%5D=37&selectedAttributes%5B32%5D=30&selectedAttributes%5B33%5D=42&selectedAttributes%5B34%5D=43&selectedAttributes%5B35%5D=51&selectedAttributes%5B36%5D=33&selectedAttributes%5B37%5D=34&selectedAttributes%5B38%5D=22&selectedAttributes%5B39%5D=49&selectedAttributes%5B40%5D=20&selectedAttributes%5B41%5D=23&selectedAttributes%5B42%5D=59&selectedAttributes%5B43%5D=10&selectedAttributes%5B44%5D=26&selectedAttributes%5B45%5D=24&selectedAttributes%5B46%5D=32&selectedAttributes%5B47%5D=3&selectedAttributes%5B48%5D=27&selectedAttributes%5B49%5D=57&selectedAttributes%5B50%5D=39&statusExclude=true&filterOperator=contains'),
        Report(filename='item-types', path='/library/orgDefaults/export?format=csv&extension=csv'),
        Report(filename='loans-checked-out', path='/library/orgLoan/exportLoans?format=csv&extension=csv&checkedOutBefore=struct&checkedOutBefore_time=23%3A59&checkedOutBefore_tz=America%2FLos_Angeles&checkedOutAfter=struct&checkedOutAfter_time=00%3A00&checkedOutAfter_tz=America%2FLos_Angeles&checkedInBefore=struct&checkedInBefore_time=23%3A59&checkedInBefore_tz=America%2FLos_Angeles&checkedInAfter=struct&checkedInAfter_time=00%3A00&checkedInAfter_tz=America%2FLos_Angeles&dueBefore=struct&dueBefore_time=23%3A59&dueBefore_tz=America%2FLos_Angeles&dueAfter=struct&dueAfter_time=00%3A00&dueOutAfter_tz=America%2FLos_Angeles&location.id=66&out=true&includeProjectData=false'),
        Report(filename='outstanding-balances', path='/library/onAccount/exportOutstandingBalancesReport?format=csv&extension=csv'),
        Report(filename=f'loans-{current_year}', path=_loans_report_path(current_year)),
        Report(filename=f'loans-{current_year - 1}', path=_loans_report_path(current_year - 1)),
        Report(filename=f'transactions-{current_year}', path=_transactions_report_path(current_year)),
        Report(filename=f'transactions-{current_year - 1}', path=_transactions_report_path(current_year - 1)),
    Report(filename='users-snapshot', path='/library/orgMembership/exportUsers?format=csv&extension=csv&membershipTypeId=0&membershipExpiringAfter=struct&membershipExpiringAfter_tz=America%2FLos_Angeles&membershipExpiringAfter_time=00%3A00&membershipExpiringBefore=struct&membershipExpiringBefore_tz=America%2FLos_Angeles&membershipExpiringBefore_time=00%3A00&memberSinceAfter=struct&memberSinceAfter_tz=America%2FLos_Angeles&memberSinceAfter_time=00%3A00&memberSinceBefore=struct&memberSinceBefore_tz=America%2FLos_Angeles&memberSinceBefore_time=00%3A00&exportField=membership.attributes.membershipId&exportField=firstName&exportField=lastName&exportField=emailAddress&exportField=emailAddressConfirmed&exportField=unconfirmedEmailAddress&exportField=username&exportField=title&exportField=organizationName&exportField=address.street1&exportField=address.street2&exportField=address.city&exportField=address.principalSubdivision&exportField=address.postalCode&exportField=address.country.displayName&exportField=address.phone&exportField=address.phone2&exportField=address.notes&exportField=sex&exportField=age&exportField=firstName2&exportField=lastName2&exportField=emailAddress2&exportField=title2&exportField=organizationName2&exportField=address2.street1&exportField=address2.street2&exportField=address2.city&exportField=address2.principalSubdivision&exportField=address2.postalCode&exportField=address2.country.displayName&exportField=address2.phone&exportField=address2.phone2&exportField=address2.notes&exportField=membership.memberSince&exportField=firstFullMembershipStart&exportField=membershipType.name&exportField=latestMembershipPurchase&exportField=membershipExpiration&exportField=membership.autoRenews&exportField=autoPayStatements&exportField=attributes.latestNote&exportField=attributes.latestWarning&exportField=openingBalance&exportField=openingBalanceDate&exportField=dynamicFields.household_type&exportField=dynamicFields.income_range&exportField=dynamicFields.ethnicity&exportField=dynamicFields.disabled&exportField=dynamicFields.renter&exportField=dynamicFields.household_size')
    )
    past_years = tuple(range(2016, current_year - 1))
    reports += tuple(Report(filename=f'loans-{year}', path=_loans_report_path(year)) for year in past_years)
    # reports += tuple(Report(filename=f'transactions-{year}', path=_transactions_report_path(year)) for year in past_years)

    bot = MyTurnBot(my_turn_subdomain)
    bot.start_session(username, password)
    for report in reports:
        print(f'Downloading {report.filename}.csv...')
        _download(bot, report, output_directory)
        print('Download complete')

def _download(bot, report, output_directory):
    """Fetch the report from MyTurn, and save it to input_with_personal_info/{filename}.csv
  
    bot: a MyTurnBot with an active session.
    report: the Report object with the report path and filename
    output_directory: the directory to download the file to.
    """
    # The timeout is timeout-to-first-byte, not for the download to complete.
    # 3 minutes should be more than enough, and future proof as our transaction
    # volume increases.
    r = bot.get(report.path, timeout=180, allow_redirects=False)
    if r.status_code != 200:
        raise Exception(f'Unexpected status received for report {filename}. Response: {r.status_code} {r.headers} {r.text}')
    with open(f'{output_directory}/{report.filename}.csv', 'w') as f:
        f.write(r.text)

def _loans_report_path(year):
    """Return the loans report path for the given year, starting at the first day and including the last day.
  
    year: an integer year.
    """
    return f'/library/orgLoan/exportLoans?format=csv&extension=csv&checkedOutBefore=struct&checkedOutBefore_date=12%2F31%2F{year}&checkedOutBefore_time=23%3A59&checkedOutBefore_tz=America%2FLos_Angeles&checkedOutAfter=struct&checkedOutAfter_date=1%2F1%2F{year}&checkedOutAfter_time=00%3A00&checkedOutAfter_tz=America%2FLos_Angeles&checkedInBefore=struct&checkedInBefore_time=23%3A59&checkedInBefore_tz=America%2FLos_Angeles&checkedInAfter=struct&checkedInAfter_time=00%3A00&checkedInAfter_tz=America%2FLos_Angeles&dueBefore=struct&dueBefore_time=23%3A59&dueBefore_tz=America%2FLos_Angeles&dueAfter=struct&dueAfter_time=00%3A00&dueOutAfter_tz=America%2FLos_Angeles&includeProjectData=false'

def _transactions_report_path(year):
    """Return the transaction report path for the given year, starting at the first day and including the last day.

    year: an integer year.
    """
    return f'/library/orgMyOrganization/exportTransactionReport?format=csv&extension=csv&after_date=1%2F1%2F{year}&after=struct&after_tz=America%2FLos_Angeles&after_time=00%3A00&before_date=12%2F31%2F{year}&before=struct&before_tz=America%2FLos_Angeles&before_time=23%3A59'

@dataclass
class Report:
    """Class that contains information required to fetch a report."""
    # The filename to download the report to, including the ".csv" suffix
    filename: str
    # The path to issue a GET requests to in order to download the report
    path: str
