import json
import os

import pytest

from processor.transactions_importer import find_start_row, load_column_mappings


@pytest.fixture
def import_dict(tmp_path):
    path = tmp_path / "import-dictionary.json"
    path.write_text(json.dumps({"column_mapping": {
        "Date": ["#Datum", "Data"],
        "Amount": ["Betrag"],
    }}))
    return str(path)


def test_load_column_mappings_flattens(import_dict):
    cols = load_column_mappings(import_dict)
    assert sorted(cols) == ["#Datum", "Betrag", "Data"]


def test_find_start_row_finds_header(tmp_path, import_dict):
    csv = tmp_path / "input.csv"
    csv.write_text("garbage 1\ngarbage 2\n#Datum;Betrag;Note;\n01.01.2024;10;hi;\n")
    rows_to_skip, fix = find_start_row(str(csv), import_dict)
    assert rows_to_skip == 2
    assert fix is None


def test_find_start_row_returns_header_fix_when_trailing_delim_missing(tmp_path, import_dict):
    csv = tmp_path / "input.csv"
    csv.write_text("Data;Betrag\n01.01.2024;10\n")
    rows_to_skip, fix = find_start_row(str(csv), import_dict)
    assert rows_to_skip == 0
    assert fix is not None
    assert fix["line_number"] == 0
    assert fix["fixed_line"].endswith(";\n")


def test_find_start_row_no_match_returns_zero(tmp_path, import_dict):
    csv = tmp_path / "input.csv"
    csv.write_text("totally unrelated content\nmore lines\n")
    rows_to_skip, fix = find_start_row(str(csv), import_dict)
    assert rows_to_skip == 0
    assert fix is None


def test_find_start_row_does_not_mutate_source(tmp_path, import_dict):
    csv = tmp_path / "input.csv"
    original = "Data;Betrag\n01.01.2024;10\n"
    csv.write_text(original)
    find_start_row(str(csv), import_dict)
    assert csv.read_text() == original, "find_start_row must not modify the source CSV"
