"""Encoding smoke — automates what was manual §4.1 in upgrade-pandas-3.

Bank exports come in a variety of encodings (UTF-8 with BOM, Windows-1252, ISO-8859-2).
chardet sometimes misidentifies single-byte European encodings on small files; this test
documents what works end-to-end and what relies on the user's pre-conversion to UTF-8 BOM.
"""
import os
from unittest.mock import patch

import pandas as pd
import pytest

import config.constants as cts
from processor.transactions_importer import process_imported_csv


@pytest.mark.parametrize("input_filename,expected_note_substring", [
    ("sample-utf8-bom.csv",  "żółwiowa"),    # canonical: encoding declared via BOM
    ("sample-cp1252.csv",    "café"),         # chardet often misidentifies as iso8859-16
    ("sample-iso8859-2.csv", "żółwiowa"),    # chardet often misidentifies as iso8859-16
])
def test_encoding_round_trip_preserves_diacritics(tmp_path, input_filename, expected_note_substring):
    base = os.path.dirname(__file__)
    input_path = os.path.join(base, "encodings", input_filename)

    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    output_path = csv_dir / cts.TRANSACTION_CSV_NAME

    repo_root = os.path.abspath(os.path.join(base, "..", ".."))
    import_dictionary = os.path.join(repo_root, "dictionary", cts.IMPORT_DICTIONARY_NAME)
    ignore_dictionary = os.path.join(repo_root, "dictionary", cts.IGNORE_DICTIONARY_NAME)

    with patch("processor.transactions_importer.user_directory_path") as mock:
        def side_effect(arg):
            if arg.endswith(cts.CSV_FILE_DIRECTORY_PATH):
                return str(csv_dir) + os.sep
            if arg.endswith(cts.IGNORE_DICTIONARY_NAME):
                return ignore_dictionary
            if arg.endswith(cts.IMPORT_DICTIONARY_NAME):
                return import_dictionary
            return arg
        mock.side_effect = side_effect

        is_success, message = process_imported_csv(
            input_path, delimiter=";", dot_decimal_separator=True)

    assert is_success, f"Import failed for {input_filename}: {message}"
    assert output_path.exists(), f"Output CSV not created for {input_filename}"

    # Verify diacritic round-trip
    df = pd.read_csv(output_path, delimiter=";", encoding="utf-8")
    notes = df["Note"].astype(str).tolist()
    assert any(expected_note_substring in note for note in notes), (
        f"Expected '{expected_note_substring}' in any Note column value, got: {notes}\n"
        f"This may indicate chardet misidentified the source encoding. "
        f"Workaround: pre-convert to UTF-8 with BOM (see docs/troubleshooting.md)."
    )
