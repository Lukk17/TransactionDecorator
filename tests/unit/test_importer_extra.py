"""Coverage for transactions_importer.py branches not covered by integration tests."""
import json
import os
from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

import config.constants as cts
from processor.transactions_importer import (
    _apply_ignore_rules,
    _load_column_mapping,
    _load_ignore_rules,
    _read_imported_csv,
    assign_imported_values_to_new_row,
    create_column_position_map,
    detect_encoding,
    process_imported_csv,
)


# ---- detect_encoding ------------------------------------------------------

def test_detect_encoding_returns_default_for_missing_file(tmp_path):
    missing = tmp_path / "nope.csv"
    assert detect_encoding(str(missing)) == cts.DEFAULT_ENCODING


def test_detect_encoding_returns_default_when_chardet_returns_none(tmp_path, monkeypatch):
    f = tmp_path / "tiny.csv"
    f.write_bytes(b"\x00\x00")  # ambiguous bytes
    # Force chardet to return None confidence
    monkeypatch.setattr(
        "processor.transactions_importer.chardet.detect", lambda _: {"encoding": None})
    assert detect_encoding(str(f)) == cts.DEFAULT_ENCODING


def test_detect_encoding_returns_chardet_value(tmp_path, monkeypatch):
    f = tmp_path / "u8.csv"
    f.write_text("hello world", encoding="utf-8")
    monkeypatch.setattr(
        "processor.transactions_importer.chardet.detect",
        lambda _: {"encoding": "windows-1252"})
    assert detect_encoding(str(f)) == "windows-1252"


# ---- _load_ignore_rules ---------------------------------------------------

def test_load_ignore_rules_reads_array(tmp_path):
    path = tmp_path / "ignore.json"
    payload = {cts.IGNORE_IGNORE_RULES_PARAM_NAME: [
        {"conditions": [{"column": "X", "value": "Y"}]}
    ]}
    path.write_text(json.dumps(payload), encoding="utf-8")
    rules = _load_ignore_rules(str(path))
    assert rules == payload[cts.IGNORE_IGNORE_RULES_PARAM_NAME]


def test_load_ignore_rules_raises_on_invalid_json(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text("{ not valid", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        _load_ignore_rules(str(path))


# ---- _load_column_mapping -------------------------------------------------

def test_load_column_mapping_reads_dict(tmp_path):
    path = tmp_path / "imp.json"
    payload = {cts.IMPORT_COLUMN_MAPPING_PARAM_NAME: {"Date": ["#Datum"]}}
    path.write_text(json.dumps(payload), encoding="utf-8")
    mapping = _load_column_mapping(str(path))
    assert mapping == payload[cts.IMPORT_COLUMN_MAPPING_PARAM_NAME]


# ---- _read_imported_csv ---------------------------------------------------

def test_read_imported_csv_no_fix_branch(tmp_path):
    f = tmp_path / "in.csv"
    f.write_text("Date;Note;\n01.01.2024;hi;\n", encoding="utf-8")
    df = _read_imported_csv(str(f), ";", "utf-8", rows_to_skip=0, header_fix=None)
    assert list(df.columns)[:2] == ["Date", "Note"]
    assert len(df) == 1


def test_read_imported_csv_header_fix_does_not_mutate_source(tmp_path):
    f = tmp_path / "in.csv"
    original = "Date;Note\n01.01.2024;hi\n"
    f.write_text(original, encoding="utf-8")
    fix = {"line_number": 0, "fixed_line": "Date;Note;\n"}
    df = _read_imported_csv(str(f), ";", "utf-8", rows_to_skip=0, header_fix=fix)
    # Source file content is untouched
    assert f.read_text(encoding="utf-8") == original
    assert len(df) == 1


# ---- _apply_ignore_rules --------------------------------------------------

def test_apply_ignore_rules_empty_rules_returns_df_unchanged():
    df = pd.DataFrame({"a": [1, 2, 3]})
    out = _apply_ignore_rules(df, [])
    assert len(out) == 3


def test_apply_ignore_rules_drops_matching_rows():
    df = pd.DataFrame({"X": ["A", "B", "A"], "Y": [1, 2, 1]})
    rules = [{cts.IGNORE_CONDITION_PARAM_NAME: [
        {cts.IGNORE_COLUMN_PARAM_NAME: "X", cts.IGNORE_VALUE_PARAM_NAME: "A"},
        {cts.IGNORE_COLUMN_PARAM_NAME: "Y", cts.IGNORE_VALUE_PARAM_NAME: 1},
    ]}]
    out = _apply_ignore_rules(df, rules)
    assert out["X"].tolist() == ["B"]


def test_apply_ignore_rules_warns_on_missing_column(caplog):
    df = pd.DataFrame({"X": ["A"]})
    rules = [{cts.IGNORE_CONDITION_PARAM_NAME: [
        {cts.IGNORE_COLUMN_PARAM_NAME: "Missing", cts.IGNORE_VALUE_PARAM_NAME: "x"},
    ]}]
    with caplog.at_level("WARNING"):
        out = _apply_ignore_rules(df, rules)
    assert any("missing column" in rec.message.lower() for rec in caplog.records)
    # Missing column means rule cannot match -> no rows dropped
    assert len(out) == 1


def test_apply_ignore_rules_or_logic_across_rules():
    df = pd.DataFrame({"X": ["A", "B", "C"]})
    rules = [
        {cts.IGNORE_CONDITION_PARAM_NAME: [
            {cts.IGNORE_COLUMN_PARAM_NAME: "X", cts.IGNORE_VALUE_PARAM_NAME: "A"}]},
        {cts.IGNORE_CONDITION_PARAM_NAME: [
            {cts.IGNORE_COLUMN_PARAM_NAME: "X", cts.IGNORE_VALUE_PARAM_NAME: "C"}]},
    ]
    out = _apply_ignore_rules(df, rules)
    assert out["X"].tolist() == ["B"]


# ---- assign_imported_values_to_new_row ------------------------------------

def _orig():
    return pd.DataFrame(columns=["Date", "Wallet", "Amount", "Note"])


def test_assign_imported_values_basic_passthrough():
    column_mapping = {"Note": ["Beschreibung"], "Wallet": ["Konto"]}
    column_indices = {"Note": 0, "Wallet": 1}
    imported_row = pd.Series(["pizza", "MyWallet"], index=["Beschreibung", "Konto"])
    new = assign_imported_values_to_new_row(
        column_indices, column_mapping, imported_row, _orig(), dot_decimal_separator=True)
    assert new["Note"] == "pizza"
    assert new["Wallet"] == "MyWallet"


def test_assign_imported_values_parses_date():
    """Date parsing only triggers when the canonical column name ('Date') is in its own alias list.
    The real import-dictionary.json includes the canonical name; this test mirrors that shape."""
    column_mapping = {"Date": ["Date", "#Datum"]}  # canonical name MUST appear in aliases
    column_indices = {"Date": 0}
    imported_row = pd.Series(["2024-01-15"], index=["#Datum"])
    new = assign_imported_values_to_new_row(
        column_indices, column_mapping, imported_row, _orig(), dot_decimal_separator=True)
    assert new["Date"] == "15.01.2024 00:00"


def test_assign_imported_values_normalizes_amount():
    column_mapping = {"Amount": ["Amount", "Betrag"]}  # canonical name MUST appear in aliases
    column_indices = {"Amount": 0}
    imported_row = pd.Series(["1.234,56"], index=["Betrag"])
    new = assign_imported_values_to_new_row(
        column_indices, column_mapping, imported_row, _orig(), dot_decimal_separator=True)
    assert new["Amount"] == "1234.56"


def test_assign_imported_values_parses_date_even_when_canonical_name_absent_from_aliases():
    """Post-fix (upgrade-pytest-9 §5.2): date routing compares canonical name against
    the constant cts.DATE_COLUMN, not against the alias list. So a user who omits the
    canonical name from their dictionary aliases still gets date parsing."""
    column_mapping = {"Date": ["#Datum"]}  # canonical 'Date' deliberately missing from aliases
    column_indices = {"Date": 0}
    imported_row = pd.Series(["2024-01-15"], index=["#Datum"])
    new = assign_imported_values_to_new_row(
        column_indices, column_mapping, imported_row, _orig(), dot_decimal_separator=True)
    assert new["Date"] == "15.01.2024 00:00"  # parsed AND reformatted


def test_assign_imported_values_normalizes_amount_even_when_canonical_name_absent_from_aliases():
    column_mapping = {"Amount": ["Betrag"]}  # canonical 'Amount' deliberately missing from aliases
    column_indices = {"Amount": 0}
    imported_row = pd.Series(["1.234,56"], index=["Betrag"])
    new = assign_imported_values_to_new_row(
        column_indices, column_mapping, imported_row, _orig(), dot_decimal_separator=True)
    assert new["Amount"] == "1234.56"


def test_assign_imported_values_skips_nan_inputs():
    column_mapping = {"Note": ["Beschreibung"]}
    column_indices = {"Note": 0}
    imported_row = pd.Series([np.nan], index=["Beschreibung"])
    new = assign_imported_values_to_new_row(
        column_indices, column_mapping, imported_row, _orig(), dot_decimal_separator=True)
    # NaN inputs leave the cell as the original-DF default (NaN)
    assert pd.isna(new["Note"])


# ---- create_column_position_map -------------------------------------------

def test_create_column_position_map_finds_first_match():
    column_mapping = {"Date": ["NotPresent", "Datum"], "Note": ["Beschreibung"]}
    imported_csv = pd.DataFrame(columns=["Datum", "Beschreibung", "Other"])
    indices = create_column_position_map(column_mapping, imported_csv)
    assert indices["Date"] == 0
    assert indices["Note"] == 1


def test_create_column_position_map_omits_missing_columns():
    column_mapping = {"Date": ["NotPresent"], "Note": ["Beschreibung"]}
    imported_csv = pd.DataFrame(columns=["Beschreibung"])
    indices = create_column_position_map(column_mapping, imported_csv)
    assert "Date" not in indices
    assert "Note" in indices


# ---- process_imported_csv error paths -------------------------------------

def test_process_imported_csv_returns_false_on_missing_file(tmp_path):
    """When the import dictionary itself is missing, the function returns False, not raises."""
    with patch("processor.transactions_importer.user_directory_path") as m:
        m.side_effect = lambda p: str(tmp_path / p)
        is_success, message = process_imported_csv(
            str(tmp_path / "nonexistent.csv"), delimiter=";", dot_decimal_separator=True)
    assert is_success is False
    assert isinstance(message, str)


def test_process_imported_csv_merges_into_non_empty_existing_csv(tmp_path):
    """Verifies the importer correctly appends new rows to an already-populated allTransactions.csv.
    Integration tests start from an empty CSV; this covers the realistic scenario where the user
    has historical data and imports a new batch."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    real_import_dict = os.path.join(repo_root, "dictionary", cts.IMPORT_DICTIONARY_NAME)
    real_ignore_dict = os.path.join(repo_root, "dictionary", cts.IGNORE_DICTIONARY_NAME)

    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    existing = csv_dir / cts.TRANSACTION_CSV_NAME
    # Pre-populate with 2 historical rows
    existing.write_text(
        "Date;Wallet;Type;Category name;Amount;Currency;Note;Labels;Author\n"
        "01.01.2024 10:00;OldWallet;Income;Salary;5000;PLN;Old payroll;;Lukk\n"
        "02.01.2024 12:00;OldWallet;Expense;Food;-50;PLN;Old grocery;;Lukk\n",
        encoding="utf-8",
    )

    # New import file with one row using canonical column names
    bank_csv = tmp_path / "new-import.csv"
    bank_csv.write_text(
        "Date;Wallet;Type;Category name;Amount;Currency;Note;Labels;Author\n"
        "15.01.2024;NewWallet;Expense;;100.00;PLN;new pizza;;Lukk\n",
        encoding="utf-8",
    )

    with patch("processor.transactions_importer.user_directory_path") as m:
        def side_effect(arg):
            if arg.endswith(cts.CSV_FILE_DIRECTORY_PATH):
                return str(csv_dir) + os.sep
            if arg.endswith(cts.IGNORE_DICTIONARY_NAME):
                return real_ignore_dict
            if arg.endswith(cts.IMPORT_DICTIONARY_NAME):
                return real_import_dict
            return arg
        m.side_effect = side_effect
        is_success, message = process_imported_csv(
            str(bank_csv), delimiter=";", dot_decimal_separator=True)

    assert is_success, f"Import failed: {message}"
    result = pd.read_csv(existing, delimiter=";", encoding="utf-8")
    # Should have 2 historical + 1 new = 3 rows
    assert len(result) == 3
    notes = result["Note"].astype(str).tolist()
    assert any("Old payroll" in n for n in notes)
    assert any("Old grocery" in n for n in notes)
    assert any("new pizza" in n for n in notes)


def test_process_imported_csv_returns_false_on_parser_error(tmp_path):
    """When pd.read_csv raises ParserError, the importer must return (False, message), not raise."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    real_import_dict = os.path.join(repo_root, "dictionary", cts.IMPORT_DICTIONARY_NAME)
    real_ignore_dict = os.path.join(repo_root, "dictionary", cts.IGNORE_DICTIONARY_NAME)

    csv_dir = tmp_path / "csv"
    csv_dir.mkdir()
    bank_csv = tmp_path / "bank.csv"
    bank_csv.write_text("Date;Note\n01.01.2024;hi\n", encoding="utf-8")

    with patch("processor.transactions_importer.user_directory_path") as m, \
         patch("processor.transactions_importer.pd.read_csv",
               side_effect=pd.errors.ParserError("simulated parser error")):
        def side_effect(arg):
            if arg.endswith(cts.CSV_FILE_DIRECTORY_PATH):
                return str(csv_dir) + os.sep
            if arg.endswith(cts.IGNORE_DICTIONARY_NAME):
                return real_ignore_dict
            if arg.endswith(cts.IMPORT_DICTIONARY_NAME):
                return real_import_dict
            return arg
        m.side_effect = side_effect
        is_success, message = process_imported_csv(
            str(bank_csv), delimiter=";", dot_decimal_separator=True)

    assert is_success is False
    assert "parser" in message.lower() or "error" in message.lower()


def test_process_imported_csv_returns_false_on_invalid_dictionary_json(tmp_path):
    (tmp_path / "csv").mkdir()
    (tmp_path / "dictionary").mkdir()
    (tmp_path / "dictionary" / cts.IGNORE_DICTIONARY_NAME).write_text(
        "{ not valid json", encoding="utf-8")
    (tmp_path / "dictionary" / cts.IMPORT_DICTIONARY_NAME).write_text("{}", encoding="utf-8")

    bank_csv = tmp_path / "bank.csv"
    bank_csv.write_text("Date;Note\n01.01.2024;hi\n", encoding="utf-8")

    with patch("processor.transactions_importer.user_directory_path") as m:
        m.side_effect = lambda p: str(tmp_path / p)
        is_success, message = process_imported_csv(
            str(bank_csv), delimiter=";", dot_decimal_separator=True)
    assert is_success is False
    assert "json" in message.lower() or "invalid" in message.lower()
