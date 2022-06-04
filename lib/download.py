"""Functions to download CSV reports from MyTurn."""
from dataclasses import dataclass
import datetime as dt
import requests


def download(myturn_url, session_id, output_directory='inputs_with_personal_info', download_past_years=False):
    """Download input reports from MyTurn to input_with_personal_info.
    
    myturn_url: the base MyTurn site to use, e.g. https://mylib.myturn.com
    session_id: the session id to use when fetching data from my turn. Use the start_session command to fetch a fresh session.
    output_directory: the directory to download files to.
    download_past_years: if True, download loans and transactions from previous years in addition to the current year.
        This should only be used once, when initially importing data.
    """
    cookies = {'JSESSIONID': session_id}
    current_year = dt.date.today().year
    
    # The URL for a report can be grabbed by following instructions in README.md, opening the Developer Tools for your browser
    # of choice just before clicking the download link, opening the Network tab, clicking the download link, and
    # copying the URL shown in the Network tab.
    reports = (
        Report(filename='admin-users-snapshot', url=f'{myturn_url}/library/orgMembership/exportUsers?format=csv&extension=csv&membershipTypeId=0&membershipExpiringAfter=struct&membershipExpiringAfter_tz=America%2FLos_Angeles&membershipExpiringAfter_time=00%3A00&membershipExpiringBefore=struct&membershipExpiringBefore_tz=America%2FLos_Angeles&membershipExpiringBefore_time=00%3A00&memberSinceAfter=struct&memberSinceAfter_tz=America%2FLos_Angeles&memberSinceAfter_time=00%3A00&memberSinceBefore=struct&memberSinceBefore_tz=America%2FLos_Angeles&memberSinceBefore_time=00%3A00&operatorsOnly=on&exportField%5B0%5D=membership.attributes.membershipId&exportField%5B1%5D=firstName&exportField%5B2%5D=lastName&exportField%5B3%5D=emailAddress&exportField%5B4%5D=emailAddressConfirmed&exportField%5B5%5D=unconfirmedEmailAddress&exportField%5B6%5D=username&exportField%5B7%5D=title&exportField%5B8%5D=organizationName&exportField%5B9%5D=address.street1&exportField%5B10%5D=address.street2&exportField%5B11%5D=address.city&exportField%5B12%5D=address.principalSubdivision&exportField%5B13%5D=address.postalCode&exportField%5B14%5D=address.country.displayName&exportField%5B15%5D=address.phone&exportField%5B16%5D=address.phone2&exportField%5B17%5D=address.notes&exportField%5B18%5D=sex&exportField%5B19%5D=age&exportField%5B20%5D=firstName2&exportField%5B21%5D=lastName2&exportField%5B22%5D=emailAddress2&exportField%5B23%5D=title2&exportField%5B24%5D=organizationName2&exportField%5B25%5D=address2.street1&exportField%5B26%5D=address2.street2&exportField%5B27%5D=address2.city&exportField%5B28%5D=address2.principalSubdivision&exportField%5B29%5D=address2.postalCode&exportField%5B30%5D=address2.country.displayName&exportField%5B31%5D=address2.phone&exportField%5B32%5D=address2.phone2&exportField%5B33%5D=address2.notes&exportField%5B34%5D=membership.memberSince&exportField%5B35%5D=firstFullMembershipStart&exportField%5B36%5D=membershipType.name&exportField%5B37%5D=latestMembershipPurchase&exportField%5B38%5D=membershipExpiration&exportField%5B39%5D=membership.autoRenews&exportField%5B40%5D=autoPayStatements&exportField%5B41%5D=attributes.latestNote&exportField%5B42%5D=attributes.latestWarning&exportField%5B43%5D=openingBalance&exportField%5B44%5D=openingBalanceDate&exportField%5B45%5D=dynamicFields.household_type&exportField%5B46%5D=dynamicFields.income_range&exportField%5B47%5D=dynamicFields.ethnicity&exportField%5B48%5D=dynamicFields.disabled&exportField%5B49%5D=dynamicFields.renter&exportField%5B50%5D=dynamicFields.household_size'),
        Report(filename='inventory-snapshot', url=f'{myturn_url}/library/orgInventory/report?format=csv&extension=csv&resolveValues=true&exportItemType=on&_exportItemType=true&exportDateCreated=on&_exportDateCreated=true&exportDateLastEdited=on&_exportDateLastEdited=true&exportDateLastUpdated=on&_exportDateLastUpdated=true&exportStatuses=on&_exportStatuses=true&selectedAttributes%5B0%5D=1&selectedAttributes%5B1%5D=15&selectedAttributes%5B2%5D=40&selectedAttributes%5B3%5D=8&selectedAttributes%5B4%5D=14&selectedAttributes%5B5%5D=58&selectedAttributes%5B6%5D=50&selectedAttributes%5B7%5D=13&selectedAttributes%5B8%5D=31&selectedAttributes%5B9%5D=4&selectedAttributes%5B10%5D=12&selectedAttributes%5B11%5D=29&selectedAttributes%5B12%5D=28&selectedAttributes%5B13%5D=2&selectedAttributes%5B14%5D=38&selectedAttributes%5B15%5D=52&selectedAttributes%5B16%5D=53&selectedAttributes%5B17%5D=54&selectedAttributes%5B18%5D=47&selectedAttributes%5B19%5D=55&selectedAttributes%5B20%5D=56&selectedAttributes%5B21%5D=46&selectedAttributes%5B22%5D=25&selectedAttributes%5B23%5D=6&selectedAttributes%5B24%5D=7&selectedAttributes%5B25%5D=16&selectedAttributes%5B26%5D=11&selectedAttributes%5B27%5D=48&selectedAttributes%5B28%5D=21&selectedAttributes%5B29%5D=35&selectedAttributes%5B30%5D=36&selectedAttributes%5B31%5D=37&selectedAttributes%5B32%5D=30&selectedAttributes%5B33%5D=42&selectedAttributes%5B34%5D=43&selectedAttributes%5B35%5D=51&selectedAttributes%5B36%5D=33&selectedAttributes%5B37%5D=34&selectedAttributes%5B38%5D=22&selectedAttributes%5B39%5D=49&selectedAttributes%5B40%5D=20&selectedAttributes%5B41%5D=23&selectedAttributes%5B42%5D=59&selectedAttributes%5B43%5D=10&selectedAttributes%5B44%5D=26&selectedAttributes%5B45%5D=24&selectedAttributes%5B46%5D=32&selectedAttributes%5B47%5D=3&selectedAttributes%5B48%5D=27&selectedAttributes%5B49%5D=57&selectedAttributes%5B50%5D=39&statusExclude=true&filterOperator=contains'),
        Report(filename='item-types', url=f'{myturn_url}/library/orgDefaults/export?format=csv&extension=csv'),
        Report(filename='loans-checked-out', url=f'{myturn_url}/library/orgLoan/exportLoans?format=csv&extension=csv&checkedOutBefore=struct&checkedOutBefore_time=23%3A59&checkedOutBefore_tz=America%2FLos_Angeles&checkedOutAfter=struct&checkedOutAfter_time=00%3A00&checkedOutAfter_tz=America%2FLos_Angeles&checkedInBefore=struct&checkedInBefore_time=23%3A59&checkedInBefore_tz=America%2FLos_Angeles&checkedInAfter=struct&checkedInAfter_time=00%3A00&checkedInAfter_tz=America%2FLos_Angeles&dueBefore=struct&dueBefore_time=23%3A59&dueBefore_tz=America%2FLos_Angeles&dueAfter=struct&dueAfter_time=00%3A00&dueOutAfter_tz=America%2FLos_Angeles&location.id=66&out=true&includeProjectData=false'),
        Report(filename='outstanding-balances', url=f'{myturn_url}/library/onAccount/exportOutstandingBalancesReport?format=csv&extension=csv'),
        Report(filename=f'loans-{current_year}', url=_loans_report_url(myturn_url, current_year)),
        Report(filename=f'transactions-{current_year}', url=_transactions_report_url(myturn_url, current_year)),
        Report(filename='users-snapshot', url=f'{myturn_url}/library/orgMembership/exportUsers?format=csv&extension=csv&membershipTypeId=0&membershipExpiringAfter=struct&membershipExpiringAfter_tz=America%2FLos_Angeles&membershipExpiringAfter_time=00%3A00&membershipExpiringBefore=struct&membershipExpiringBefore_tz=America%2FLos_Angeles&membershipExpiringBefore_time=00%3A00&memberSinceAfter=struct&memberSinceAfter_tz=America%2FLos_Angeles&memberSinceAfter_time=00%3A00&memberSinceBefore=struct&memberSinceBefore_tz=America%2FLos_Angeles&memberSinceBefore_time=00%3A00&exportField%5B0%5D=membership.attributes.membershipId&exportField%5B1%5D=firstName&exportField%5B2%5D=lastName&exportField%5B3%5D=emailAddress&exportField%5B4%5D=emailAddressConfirmed&exportField%5B5%5D=unconfirmedEmailAddress&exportField%5B6%5D=username&exportField%5B7%5D=title&exportField%5B8%5D=organizationName&exportField%5B9%5D=address.street1&exportField%5B10%5D=address.street2&exportField%5B11%5D=address.city&exportField%5B12%5D=address.principalSubdivision&exportField%5B13%5D=address.postalCode&exportField%5B14%5D=address.country.displayName&exportField%5B15%5D=address.phone&exportField%5B16%5D=address.phone2&exportField%5B17%5D=address.notes&exportField%5B18%5D=sex&exportField%5B19%5D=age&exportField%5B20%5D=firstName2&exportField%5B21%5D=lastName2&exportField%5B22%5D=emailAddress2&exportField%5B23%5D=title2&exportField%5B24%5D=organizationName2&exportField%5B25%5D=address2.street1&exportField%5B26%5D=address2.street2&exportField%5B27%5D=address2.city&exportField%5B28%5D=address2.principalSubdivision&exportField%5B29%5D=address2.postalCode&exportField%5B30%5D=address2.country.displayName&exportField%5B31%5D=address2.phone&exportField%5B32%5D=address2.phone2&exportField%5B33%5D=address2.notes&exportField%5B34%5D=membership.memberSince&exportField%5B35%5D=firstFullMembershipStart&exportField%5B36%5D=membershipType.name&exportField%5B37%5D=latestMembershipPurchase&exportField%5B38%5D=membershipExpiration&exportField%5B39%5D=membership.autoRenews&exportField%5B40%5D=autoPayStatements&exportField%5B41%5D=attributes.latestNote&exportField%5B42%5D=attributes.latestWarning&exportField%5B43%5D=openingBalance&exportField%5B44%5D=openingBalanceDate&exportField%5B45%5D=dynamicFields.household_type&exportField%5B46%5D=dynamicFields.income_range&exportField%5B47%5D=dynamicFields.ethnicity&exportField%5B48%5D=dynamicFields.disabled&exportField%5B49%5D=dynamicFields.renter&exportField%5B50%5D=dynamicFields.household_size'),
    )
    if download_past_years:
        past_years = tuple(range(2016, current_year))
        reports += tuple(Report(filename=f'loans-{year}', url=_loans_report_url(myturn_url, year)) for year in past_years)
        reports += tuple(Report(filename=f'transactions-{year}', url=_transactions_report_url(myturn_url, year)) for year in past_years)

    for report in reports:
        # TODO: Proper logging
        print(f'Downloading {report.filename}.csv...')
        _download(cookies, report.url, report.filename, output_directory)
        print('Download complete')


def start_session(myturn_url, username, password):
    """Start a session on MyTurn using the provided username and password, returning the JSESSIONID cookie value."""
    r = requests.post(
        f'{myturn_url}/library/j_spring_security_check',
        data={'j_username': username, 'j_password': password},
        # Don't follow the login redirect, it's unnecessary since the 302 gives the session cookie
        allow_redirects=False,
        timeout=5,
    )
    r.raise_for_status()
    # Authentication failure redirect to '/library/login/authfail?login_error=1'.
    if 'fail' in r.headers['Location'] or 'error' in r.headers['Location']:
        raise ValueError(f'Error starting session. Bad username ({username}) or password.')
    return r.cookies['JSESSIONID']

def _download(cookies, report_url, filename, output_directory):
    """Fetch the report from MyTurn, and save it to input_with_personal_info/{filename}.csv
    
    cookies: map of cookie name to value to use when fetching report. Should have JSESSIONID populated with an un-expired session.
    report_url: the complete URL, including protocol and query params
    filename: the name of the file to save the result to without the ".csv" suffix.
    """
    # The timeout is timeout-to-first-byte, not for the download to complete.
    # 30 seconds timed out for transactions, but 45 seconds should be enough time for MyTurn to generate the start of a response.
    r = requests.get(report_url, timeout=45, cookies=cookies, allow_redirects=False)
    r.raise_for_status()
    if r.status_code != 200:
        raise Exception(f'Unexpected status received for report {filename}. Response: {r.status_code} {r.headers} {r.text}')
    with open(f'{output_directory}/{filename}.csv', 'w') as f:
        f.write(r.text)

def _loans_report_url(myturn_url, year):
    """Return the loans report URL for the given year, starting at the first day and including the last day.
    
    myturn_url: the base MyTurn site to use, e.g. https://mylib.myturn.com
    year: an integer year.
    """
    return f'{myturn_url}/library/orgLoan/exportLoans?format=csv&extension=csv&checkedOutBefore=struct&checkedOutBefore_date=12%2F31%2F{year}&checkedOutBefore_time=23%3A59&checkedOutBefore_tz=America%2FLos_Angeles&checkedOutAfter=struct&checkedOutAfter_date=1%2F1%2F{year}&checkedOutAfter_time=00%3A00&checkedOutAfter_tz=America%2FLos_Angeles&checkedInBefore=struct&checkedInBefore_time=23%3A59&checkedInBefore_tz=America%2FLos_Angeles&checkedInAfter=struct&checkedInAfter_time=00%3A00&checkedInAfter_tz=America%2FLos_Angeles&dueBefore=struct&dueBefore_time=23%3A59&dueBefore_tz=America%2FLos_Angeles&dueAfter=struct&dueAfter_time=00%3A00&dueOutAfter_tz=America%2FLos_Angeles&includeProjectData=false'

def _transactions_report_url(myturn_url, year):
    """Return the transaction report URL for the given year, starting at the first day and including the last day.

    myturn_url: the base MyTurn site to use, e.g. https://mylib.myturn.com
    year: an integer year.
    """
    return f'{myturn_url}/library/orgMyOrganization/exportTransactionReport?format=csv&extension=csv&after_date=1%2F1%2F{year}&after=struct&after_tz=America%2FLos_Angeles&after_time=00%3A00&before_date=12%2F31%2F{year}&before=struct&before_tz=America%2FLos_Angeles&before_time=23%3A59'

@dataclass
class Report:
    """Class that contains information required to fetch a report."""
    # The filename to download the report to, including the ".csv" suffix
    filename: str
    # The URL to issue a GET requests to in order to download the report
    url: str