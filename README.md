# Capitol Hill Tool Library Data Pipeline

A pipeline for data from the Capitol Hill Tool Library's MyTurn dashboard.

## Running

Make sure you have [`Pipenv`](https://docs.pipenv.org/) installed. In this directory, run:

```
pipenv shell
# The first time you run, install dependencies
pipenv install
# Open up the set of Jupyter notebooks
jupyter lab
```

This will open a browser window where you can edit and run the import/processing scripts.

Before commiting changes or submitting pull requests, run `cp pre-commit .git/hooks`. This file is set up to automatically remove ipynb notebook output prior to committing (as long as you are running `git commit` in a `pipenv shell`).

## Inputs

Data can be manually or programatically exported from [the CHTL MyTurn site](https://capitolhill.myturn.com/).  To export, request [Super Admin access](https://support.myturn.com/hc/en-us/articles/205664648-Creating-Additional-Admin-Users), or ask an existing Super Admin to export the data for you.


## Automated Export

You can automatically download and anomyize files using `cli.py` in lib.

```
# Make sure you're in a pipenv shell, and the root of this project
pipenv shell
./lib/cli.py download --subdomain capitolhill --output_directory input_with_personal_info/
./lib/cli.py anonymize --input_directory input_with_personal_info/ --output_directory input/
# TODO: Convert the more stable Python notebooks into a format we can run from the CLI
# TODO: Allow downloading/process/anonymizing a particular report
```

## Manual Export

The process for manually exporting data is documented here. This is kept up to date because it makes it clear where data is coming from, and is used to grab the URL used by the programattic download script.

* Inventory
  * Go to the ["Export Inventory"](https://capitolhill.myturn.com/library/orgInventory/report) page
  * Leave "Reporting/Viewing" selected
  * Click "Select All" to inclue all fields
  * Expand the "Limit by Status" section, and uncheck "Disabled".  This makes sure any loans with "Disabled" items can still be processed
  * Click "CSV"
  * Move the downloaded file to `input_with_personal_info/inventory-snapshot.csv`
* Members
  * Go to the ["Search / Export Members"](https://capitolhill.myturn.com/library/orgMembership/searchUsers) page
  * Click "Search" without changing any options.
  * Click "CSV"
  * Move the downloaded file to `input_with_personal_info/users-snapshot.csv`
* Admins
  * Follow the instructions for "Users", but expand the "Advanced" section and click "Limit to all Administrators" before searching.
  * Move the downloaded file to `input_with_personal_info/admin-users-snapshot.csv`.
* Loans
  * Completed Loans - To populate the initial set of years, follow these instructions for each year from 2016 onward.  MyTurn only allows exporting a single year of loan data at a time. After the initial import, only the current year needs to be re-imported. Because "Checked Out" date is used, all past year loan data is static.
      * Go to the ["Loans" > "Custom"](https://capitolhill.myturn.com/library/orgLoan/reportParameters) page
      * Set "Checked Out On or After" to the first day of the year
      * Set "Checked Out On or Before" to the last day of the year
      * Click "Generate Report"
      * Click "CSV" on the next page
      * Move the downloaded file to `input_with_personal_info/loans-{year}.csv`
  * Checked Out Loans - Outstanding loans are exported separately, and may have been placed in any year.
      * Go to the ["Loans" > "All Checked Out"](https://capitolhill.myturn.com/library/orgLoan/list) page
      * Click "CSV"
      * Mvoe the downloaded file to `input_with_personal_info/loans-checked-out.csv`
* Transactions
  * To populate the initial set of years, follow these instructions for each year from 2016 onward. MyTurn only allows exporting two years of transaction data ata time, but only one year at a time is exported for simplicity.  After the initial import, only the current year needs to be re-imported.
    * Go to the ["Reports" > "Transactions / Money"](https://capitolhill.myturn.com/library/orgMyOrganization/moneyReport) page
    * Set "Transactions On or After" to the first day of the year
    * Set "Transactions On or Before" to the last day of the year
    * Click "Update"
    * Click "CSV"
    * Move the downloaded file to `input_with_personal_info/transaction-{year}.csv`
* Outstanding Balances
  * MyTurn records the balance accured from previous loans/fees separately from the balance due on outstanding loans and fees. The balance for outstanding fees back be read from the "Loans" data. Previously accrued balance is provided in this report.
    * Go to the ["Reports" > "Outstanding Balances"](https://capitolhill.myturn.com/library/onAccount/list) page
    * Click "CSV"
    * Move the downloaded file to `input_with_personal_info/outstanding-balances.csv`
* Item Types
  * A list of Item Types can be downloaded directly from [this link](https://capitolhill.myturn.com/library/orgDefaults/export?format=csv&extension=csv). This link is also listed on the ["Inventory" > "Import"](https://capitolhill.myturn.com/library/orgInventory/importInventory) page.

When done, run `./lib/cli.py anonymize --input_directory input_with_personal_info/ --output_directory input/` to remove any personal info from the downloads and copy it to the `input` folder, where it can be committed to source control and used by scripts.

## Outputs

To generate data in `output/`, run each notebook in the order it appears in jupyter lab. The prefix of each file (`01_` etc.) indicates whether it depends on any previous file. Files with `01_` don't depend on any other files, but files with `02_` depend on the outputs of `01_`, and so on.

## License

MIT