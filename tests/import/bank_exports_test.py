"""Integration tests for the anonymized real bank-export fixtures.

Each test runs the full importer pipeline (find_start_row + read +
ignore-rules + column mapping + parse_date / normalize_number_format +
concat + write-back) and asserts the output matches a frozen expected
CSV. The fixtures are anonymized real exports — see
tests/import/bank-exports/README.md.

These tests catch:
  - Format-handling regressions (date parsing, decimal normalization, encoding)
  - Column-mapping regressions when import-dictionary.json aliases drift
  - Multi-line preamble skipping (mbank format)
  - Per-bank quirks (apostrophe-prefixed accounts in pekao,
    space-thousand-separator amounts, etc.)

Known behavioral quirks (current importer limitations, NOT regressions):
  - mbank "Amount" column retains the "PLN" suffix because
    "100,00 PLN" doesn't match the normalize_number_format regex set
  - pekao amounts retain the space thousand-separator
  - These are addressed by future cleanup proposals, not by these fixtures.

revolut.xlsx is committed but NOT exercised by these tests — the current
importer is CSV-only. The future add-revolut-adapter proposal will add
the corresponding integration test.
"""
import os
from unittest.mock import patch

import pandas as pd
import pytest

import config.constants as cts
from processor.transactions_importer import process_imported_csv


@pytest.mark.parametrize("fixture_name,delimiter", [
    ("mbank.csv", ";"),
    ("nestbank_utf8.csv", ","),
    ("pekaobp.csv", ";"),
    ("alior.csv", ";"),
])
def test_bank_export_round_trip(tmp_path, fixture_name, delimiter):
    base = os.path.dirname(__file__)
    repo_root = os.path.abspath(os.path.join(base, "..", ".."))

    fixture_path = os.path.join(base, "bank-exports", fixture_name)
    expected_path = os.path.join(
        base, "bank-exports", "expected", fixture_name.replace(".csv", "-expected.csv"))

    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    output_path = csv_dir / cts.TRANSACTION_CSV_NAME

    real_import_dict = os.path.join(repo_root, "dictionary", cts.IMPORT_DICTIONARY_NAME)
    real_ignore_dict = os.path.join(repo_root, "dictionary", cts.IGNORE_DICTIONARY_NAME)

    with patch("processor.transactions_importer.user_directory_path") as mock:
        def side_effect(arg):
            if arg.endswith(cts.CSV_FILE_DIRECTORY_PATH):
                return str(csv_dir) + os.sep
            if arg.endswith(cts.IGNORE_DICTIONARY_NAME):
                return real_ignore_dict
            if arg.endswith(cts.IMPORT_DICTIONARY_NAME):
                return real_import_dict
            return arg
        mock.side_effect = side_effect

        is_success, message = process_imported_csv(
            fixture_path, delimiter=delimiter, dot_decimal_separator=True)

    assert is_success, f"Import failed for {fixture_name}: {message}"
    assert output_path.exists(), f"Output CSV not created for {fixture_name}"

    actual_df = pd.read_csv(output_path, delimiter=cts.CSV_DELIMITER, encoding="utf-8")
    expected_df = pd.read_csv(expected_path, delimiter=cts.CSV_DELIMITER, encoding="utf-8")

    pd.testing.assert_frame_equal(actual_df, expected_df)
