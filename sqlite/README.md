# SQLite

You can open and play around with this by running `sqlite libtool.db` in this directory. To import data, use `mode csv` and then `import ../output/<filename>`.

## Background
This is my first attempt at processing CHTL data.  [SQLite](https://sqlite.org/) is a fantastic tool, and these queries are still useful for processing the cleaned data in the [`output`][../output] directory.  However, it was much easier to do the following with Pandas and Jupyter:

* Clean up the data - Pandas makes it easy to identify unusual data by either failing to process it, or marking it as NaN-ish.
* Handling dates - This is one of SQLite's biggest weak spots out of the box. There may be an extension for this, but the default date handling is limited to specific date formats, and the raw MyTurn data for CHTL didn't have this.
* Iterative processing - the best I could come up with for a way to determine things like the "maximum checkouts" for an item was an iterative algorithm. SQLite has some capacity for this using recursion, but I think it's pretty far outside its typical purpose.
