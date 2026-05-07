## ADDED Requirements

### Requirement: openpyxl pinned in core dependencies

The project SHALL pin `openpyxl` exactly in `pyproject.toml` `[project] dependencies` (NOT under optional extras). The pinned version MUST be one known compatible with the active pandas pin.

#### Scenario: Project metadata declares the pin

- **WHEN** a contributor reads `pyproject.toml`
- **THEN** the `dependencies` array contains an entry of the form `openpyxl==<exact version>`

#### Scenario: Fresh install pulls openpyxl

- **WHEN** a contributor runs `pip install -e .` against the project (no extras)
- **THEN** `pip show openpyxl` reports the pinned version

### Requirement: File-extension dispatch in importer

`process_imported_csv` SHALL accept files with `.csv`, `.xlsx`, or `.xlsm` extensions. The internal read step (`_read_imported_csv` or equivalent) MUST branch on extension: CSV files go through `pd.read_csv` (existing path); xlsx/xlsm files go through `pd.read_excel(..., engine='openpyxl')`. All downstream processing (`_apply_ignore_rules`, `assign_imported_values_to_new_row`, `pd.concat`, `to_csv` write-back) MUST be identical for both paths.

#### Scenario: CSV import unchanged

- **WHEN** `process_imported_csv` is called with a `.csv` file
- **THEN** it follows the pre-existing CSV branch and produces output identical to before this change

#### Scenario: xlsx import takes the new branch

- **WHEN** `process_imported_csv` is called with a `.xlsx` file
- **THEN** the input is loaded via `pd.read_excel(..., engine='openpyxl')`, NOT via `pd.read_csv`
- **AND** the resulting DataFrame is passed through the same downstream pipeline as a CSV would be

#### Scenario: xlsm extension also accepted

- **WHEN** `process_imported_csv` is called with a `.xlsm` (macro-enabled Excel) file
- **THEN** it follows the xlsx branch (same `pd.read_excel` call); macros are NOT executed

### Requirement: GUI file picker accepts both formats

The Qt file dialog opened by `import_csv` SHALL accept `.csv`, `.xlsx`, and `.xlsm` files via a unified filter. The filter MUST be structured so that the default ("Bank Exports") shows all three; per-format filters are also offered for users who want to narrow.

#### Scenario: User sees combined filter

- **WHEN** a user clicks "Import CSV" in the GUI
- **THEN** the file picker shows a default filter named like "Bank Exports (*.csv *.xlsx *.xlsm)"

#### Scenario: User can pick an xlsx

- **WHEN** a user picks a `.xlsx` file from the dialog
- **THEN** the import flow proceeds without raising "unsupported format"

### Requirement: Delimiter dialog skipped for xlsx

The post-file-pick `create_input_dialog` MUST detect xlsx/xlsm files and skip the delimiter dropdown for them (xlsx has no delimiter). The decimal-separator checkbox MUST still be shown.

#### Scenario: xlsx import skips delimiter prompt

- **WHEN** the user picks a `.xlsx` file in the file dialog
- **AND** the delimiter dialog is about to appear
- **THEN** the dialog shows ONLY the decimal-separator checkbox, NOT the delimiter dropdown

#### Scenario: CSV import still asks for delimiter

- **WHEN** the user picks a `.csv` file in the file dialog
- **THEN** the delimiter dialog appears with both the delimiter dropdown AND the decimal-separator checkbox (unchanged from current behavior)

### Requirement: Single-section xlsx contract

The xlsx import path SHALL only handle xlsx files that follow the **single-section** contract: one header row at the top of the active sheet, transaction rows immediately below, no nested sub-headers, no `Total` summary rows, no metadata sections preceding the header. Multi-section workbooks (per-currency or per-account sub-sheets, consolidated statements, etc.) are explicitly out of scope and MUST be addressed by a separate adapter proposal if a real user need surfaces.

#### Scenario: Single-section xlsx parses cleanly

- **WHEN** a user imports an xlsx file with structure `[header row, data row, data row, ...]`
- **THEN** the import succeeds and produces a DataFrame whose columns match the header row

#### Scenario: Multi-section xlsx is rejected with a clear error

- **WHEN** a user imports an xlsx file with multiple "Date | Description | ..." header rows separated by blank rows or sub-headers
- **THEN** the import either succeeds reading only the first section (and surfaces a warning) OR fails with a clear "single-section contract violated" error message

### Requirement: xlsx integration test fixture

The test suite SHALL include at least one xlsx fixture under `tests/import/` that exercises the new branch end-to-end. The fixture MUST be a single-section xlsx mirror of an existing CSV fixture so the expected output is the same.

#### Scenario: Parametrized integration test covers xlsx

- **WHEN** `pytest tests/import/` runs
- **THEN** at least one test case loads an xlsx fixture via `process_imported_csv` and asserts the resulting `allTransactions.csv` matches a frozen expected fixture

### Requirement: Documentation updated

`docs/importing.md` SHALL document that the importer accepts both CSV and xlsx, and SHALL include a "Recommended export format" table covering the major banks tested, with notes on which format to prefer per bank.

#### Scenario: docs/importing.md mentions xlsx

- **WHEN** a user reads `docs/importing.md`
- **THEN** the document explicitly lists `.xlsx` and `.xlsm` as accepted formats AND points users toward CSV when both are available (CSV avoids the openpyxl roundtrip)
