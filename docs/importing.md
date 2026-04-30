# Importing CSV files

To import a CSV, click the **Import CSV** button in the application.

## Requirements

- File must be **UTF-8 encoded**.
- The CSV cannot contain any description lines at the top — many bank exports include export metadata in the first row, which makes the file an invalid CSV. If your bank export does, open it in Excel and re-save as `CSV UTF-8`.
- Column count must be consistent: every row must have the same number of delimiters as the header row.

## What happens during import

1. The original `allTransactions.csv` is backed up into the `backup/` folder.
2. The imported CSV is parsed and date formats are normalized.
3. Rows matched by `ignore-dictionary.json` are skipped (see [Dictionaries](dictionaries.md)).
4. Remaining rows are appended to `allTransactions.csv`.
