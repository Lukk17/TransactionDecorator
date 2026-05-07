## 1. Pre-flight + dep pin

- [ ] 1.1 Confirm latest stable `openpyxl` version compatible with the active `pandas==3.0.2` pin (`pip index versions openpyxl`)
- [ ] 1.2 Add `openpyxl==<version>` to `pyproject.toml` `[project] dependencies` (alongside chardet, pandas, PySide6)
- [ ] 1.3 Reinstall: `pip install -e .[dev]`. Confirm `pip show openpyxl` reports the pinned version

## 2. Source: extension dispatch

- [ ] 2.1 In `src/processor/transactions_importer.py::_read_imported_csv`, add an extension check at the top: if file ends in `.xlsx`/`.xlsm`, return `pd.read_excel(file_name, engine='openpyxl')` and ignore the CSV-specific args (`delimiter`, `encoding`, `rows_to_skip`, `header_fix`)
- [ ] 2.2 Verify the calling code in `process_imported_csv` doesn't break when the CSV-specific args are passed but ignored (they should just be discarded)
- [ ] 2.3 Run existing test suite (`pytest -W error`) — must remain green; this is a strictly additive branch

## 3. GUI: file picker filter + delimiter dialog skip

- [ ] 3.1 In `src/processor/transactions_importer.py::import_csv`, change the file dialog filter from `"CSV Files (*.csv)"` to `"Bank Exports (*.csv *.xlsx *.xlsm);;CSV Files (*.csv);;Excel Files (*.xlsx *.xlsm)"`
- [ ] 3.2 After the file is picked, detect extension. If xlsx/xlsm, call a slimmer dialog that shows only the decimal-separator checkbox (no delimiter dropdown). If CSV, call the existing `create_input_dialog`
- [ ] 3.3 Add a new helper `create_xlsx_input_dialog(main_window)` in `src/gui_elements/widget_assembler.py` returning `(dot_decimal_separator, ok)` (no delimiter)
- [ ] 3.4 Update the existing `create_input_dialog` docstring/comment to clarify it's CSV-only

## 4. Test fixture

- [ ] 4.1 Create `tests/import/sample-single-section.xlsx` — a single-sheet xlsx mirroring `tests/import/importerTestData.csv` (same header row, same data rows, just packaged as xlsx). Use openpyxl in a one-shot script (don't commit the script — reproduce inline if challenged) OR open the CSV in Excel/LibreOffice and Save As xlsx
- [ ] 4.2 Create `tests/import/expected/correctly-sample-single-section.csv` matching the existing CSV-fixture expected output
- [ ] 4.3 Add a parametrized case to `tests/import_test.py` (or a new `tests/import/xlsx_test.py`) loading the xlsx and asserting equality with the expected output

## 5. Unit tests for new dispatch + GUI logic

- [ ] 5.1 Add `tests/unit/test_xlsx_dispatch.py` with cases:
  - `_read_imported_csv` with `.xlsx` extension calls `pd.read_excel`, not `pd.read_csv`
  - `_read_imported_csv` with `.xlsm` extension calls `pd.read_excel`
  - `_read_imported_csv` with `.csv` extension still calls `pd.read_csv`
- [ ] 5.2 In `tests/unit/test_widget_assembler.py`, add cases for the new `create_xlsx_input_dialog`:
  - On Accept, returns `(True, 1)` (dot decimal default + ok=1)
  - On Cancel, returns `(True, 0)`
- [ ] 5.3 In `tests/unit/test_widget_assembler.py::test_import_csv_*`, extend to cover the xlsx branch:
  - `test_import_csv_xlsx_skips_delimiter_dialog` — pick xlsx, verify `create_input_dialog` is NOT called and `create_xlsx_input_dialog` IS called

## 6. Documentation

- [ ] 6.1 Update `docs/importing.md`:
  - Add `.xlsx` / `.xlsm` to the "Accepted formats" section
  - Add the "Recommended export format" per-bank table
  - Note that CSV is preferred when both are available (avoids the openpyxl roundtrip)
- [ ] 6.2 Update README install table footnote to mention both formats are accepted
- [ ] 6.3 Update `docs/architecture/decisions/adr-0007-packaging.md` to note the new openpyxl bundle dep adds ~3-5 MB

## 7. Manual smoke

- [ ] 7.1 Run `pytest -W error` — full suite green (count grew by xlsx fixture + ~5 unit tests)
- [ ] 7.2 Launch `python src/gui.py`, click Import, pick the xlsx fixture, verify the new dialog flow (no delimiter prompt) and successful import

## 8. Spec lifecycle

- [ ] 8.1 Run `openspec validate add-xlsx-import` — must pass
- [ ] 8.2 After §1–§7 done, run `openspec archive add-xlsx-import`
