# Capitol Hill Tool Library Data Pipeline

Some scripts that download MyTurn data, massage it, and display them as reports.

## Running

Make sure [`Pipenv`](https://docs.pipenv.org/) is installed. In this directory, run:

```
pipenv shell
# Installs the myturn_bot package, and juptyer lab+pandas for hacking.
pipenv install
```

`myturn_bot` is installed as an editable package, so you can make edits and it will be reflected
when you run it next.

### Pipeline

To fetch and process data, use the newly installed `myturn_bot pipeline` tool in your pipenv.

```
# Download and process all your library's data
myturn_bot pipeline --output <somedir> --subdomain capitolhill
```

WARNING: Running `myturn_bot pipeline` requires [Super Admin access](https://support.myturn.com/hc/en-us/articles/205664648-Creating-Additional-Admin-Users).

See `myturn_bot pipeline --help` for more info on options. In addition to a full run, you can
only run specific stages (download/process), files (users/loans), or years
(e.g only 2024 loans and transactions).

### Notebooks

See the [`notebooks/`](./notebooks/) dir to run some interesting reports and data based on the
processed MyTurn data. To run notebooks:

```
pipenv shell
jupyter lab
```

## Data Sources

The process for manually exporting data from capitolhill.myturn.com is documented here. This is kept up to date because it makes it clear where data is coming from, and is used to grab the URL used by the programattic download script.

* Inventory
  * Go to the ["Export Inventory"](https://capitolhill.myturn.com/library/orgInventory/report) page
  * Leave "Reporting/Viewing" selected
  * Click "Select All" to inclue all fields
  * Expand the "Limit by Status" section, and uncheck "Disabled".  This makes sure any loans with "Disabled" items can still be processed
  * Click "CSV"
  * Move the downloaded file to `data/input_with_personal_info/inventory-snapshot.csv`
* Members
  * Go to the ["Search / Export Members"](https://capitolhill.myturn.com/library/orgMembership/searchUsers) page
  * Click "Search" without changing any options.
  * Click "CSV"
  * Move the downloaded file to `data/input_with_personal_info/users-snapshot.csv`
* Admins
  * Follow the instructions for "Users", but expand the "Advanced" section and click "Limit to all Administrators" before searching.
  * Move the downloaded file to `data/input_with_personal_info/admin-users-snapshot.csv`.
* Loans
  * Completed Loans - To populate the initial set of years, follow these instructions for each year from 2016 onward.  MyTurn only allows exporting a single year of loan data at a time. After the initial import, only the current year needs to be re-imported. Because "Checked Out" date is used, all past year loan data is static.
      * Go to the ["Loans" > "Custom"](https://capitolhill.myturn.com/library/orgLoan/reportParameters) page
      * Set "Checked Out On or After" to the first day of the year
      * Set "Checked Out On or Before" to the last day of the year
      * Click "Generate Report"
      * Click "CSV" on the next page
      * Move the downloaded file to `data/input_with_personal_info/loans-{year}.csv`
  * Checked Out Loans - Outstanding loans are exported separately, and may have been placed in any year.
      * Go to the ["Loans" > "All Checked Out"](https://capitolhill.myturn.com/library/orgLoan/list) page
      * Click "CSV"
      * Mvoe the downloaded file to `data/input_with_personal_info/loans-checked-out.csv`
* Transactions
  * To populate the initial set of years, follow these instructions for each year from 2016 onward. MyTurn only allows exporting two years of transaction data ata time, but only one year at a time is exported for simplicity.  After the initial import, only the current year needs to be re-imported.
    * Go to the ["Reports" > "Transactions / Money"](https://capitolhill.myturn.com/library/orgMyOrganization/moneyReport) page
    * Set "Transactions On or After" to the first day of the year
    * Set "Transactions On or Before" to the last day of the year
    * Click "Update"
    * Click "CSV"
    * Move the downloaded file to `data/input_with_personal_info/transaction-{year}.csv`
* Outstanding Balances
  * MyTurn records the balance accured from previous loans/fees separately from the balance due on outstanding loans and fees. The balance for outstanding fees back be read from the "Loans" data. Previously accrued balance is provided in this report.
    * Go to the ["Reports" > "Outstanding Balances"](https://capitolhill.myturn.com/library/onAccount/list) page
    * Click "CSV"
    * Move the downloaded file to `data/input_with_personal_info/outstanding-balances.csv`
* Item Types
  * A list of Item Types can be downloaded directly from [this link](https://capitolhill.myturn.com/library/orgDefaults/export?format=csv&extension=csv). This link is also listed on the ["Inventory" > "Import"](https://capitolhill.myturn.com/library/orgInventory/importInventory) page.

When done, run `./lib/cli.py anonymize --input_directory data/input_with_personal_info/ --output_directory data/input/` to remove any personal info from the downloads and copy it to the `input` folder, where it can be committed to source control and used by scripts.

## Deployment

Copy the setup.py and the myturn_bot folder to a folder on the server you'd liek to run:

```
cd <project-folder>
# At least Python 3.8. Create a virtualenv in the "venv/" folder
python3 -m venv venv
. ./venv/bin/activate
pip install -e .
# Now you can run the command line
```
## License

MIT
