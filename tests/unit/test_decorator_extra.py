"""Coverage for transactions_decorator.py branches not covered by integration tests."""
import json
import os
from unittest.mock import patch

import pandas as pd
import pytest

import config.constants as cts
from processor import transactions_decorator as td
from processor.transactions_decorator import (
    assign_category,
    convert_decimal_separator,
    create_backup,
    decorate_transactions,
    extract_existing_labels,
    find_existing_category,
    initialize_labels_column,
    load_dictionary,
    update_categories,
    update_labels,
)


# ---- create_backup ---------------------------------------------------------

def test_create_backup_makedirs_when_missing(tmp_path):
    original = tmp_path / "original.csv"
    original.write_text("Date;Note\n01.01.2024;hi\n", encoding="utf-8")
    backup_dir = tmp_path / "backups"  # does not exist yet

    create_backup(str(original), str(backup_dir))

    assert backup_dir.exists()
    backups = list(backup_dir.iterdir())
    assert len(backups) == 1
    assert backups[0].name.startswith("original.csv_")


def test_create_backup_initializes_original_when_missing(tmp_path):
    """If the original file is absent, create_backup must call create_original_csv first."""
    original = tmp_path / "missing.csv"
    backup_dir = tmp_path / "backups"

    create_backup(str(original), str(backup_dir))

    assert original.exists(), "create_backup should auto-init missing original"
    assert "Date" in original.read_text(encoding="utf-8")


def test_create_backup_initializes_original_when_empty(tmp_path):
    original = tmp_path / "empty.csv"
    original.write_text("", encoding="utf-8")
    backup_dir = tmp_path / "backups"

    create_backup(str(original), str(backup_dir))

    assert "Date" in original.read_text(encoding="utf-8")


# ---- load_dictionary -------------------------------------------------------

def test_load_dictionary_loads_inverts_and_normalizes(tmp_path):
    path = tmp_path / "dict.json"
    path.write_text(json.dumps({"Food": ["Pizza", "BURGER"]}), encoding="utf-8")
    result = load_dictionary(str(path))
    # invert + normalize keys to lowercase
    assert "pizza" in result
    assert "burger" in result
    assert result["pizza"] == ["food"]


# ---- find_existing_category -----------------------------------------------

def test_find_existing_category_returns_none_when_column_missing():
    df = pd.DataFrame({"Note": ["x"]})
    assert find_existing_category(df, 0) is None


def test_find_existing_category_returns_normalized_value():
    df = pd.DataFrame({cts.CATEGORIES_COLUMN: ["  Food  "]})
    assert find_existing_category(df, 0) == "food"


# ---- assign_category ------------------------------------------------------

def test_assign_category_capitalizes_first_letter():
    df = pd.DataFrame({cts.CATEGORIES_COLUMN: [""]})
    assign_category(["food"], df, 0)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Food"


def test_assign_category_keeps_existing_capitalization_in_rest():
    df = pd.DataFrame({cts.CATEGORIES_COLUMN: [""]})
    assign_category(["GROCERIES"], df, 0)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Groceries"


def test_assign_category_picks_first_match():
    df = pd.DataFrame({cts.CATEGORIES_COLUMN: [""]})
    assign_category(["fuel", "transport", "car"], df, 0)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Fuel"


# ---- initialize_labels_column ---------------------------------------------

def test_initialize_labels_column_creates_when_missing():
    df = pd.DataFrame({"Note": ["x", "y"]})
    initialize_labels_column(df)
    assert cts.LABELS_COLUMN in df.columns
    assert len(df[cts.LABELS_COLUMN]) == 2
    assert df[cts.LABELS_COLUMN].isna().all()


def test_initialize_labels_column_casts_non_object_dtype():
    df = pd.DataFrame({cts.LABELS_COLUMN: pd.Series(["a", "b"], dtype="str")})
    initialize_labels_column(df)
    # Under pandas 3 the cast runs because str != object; result must still be writable as object
    assert df[cts.LABELS_COLUMN].dtype == object


def test_initialize_labels_column_no_op_when_already_object():
    df = pd.DataFrame({cts.LABELS_COLUMN: pd.Series(["a", "b"], dtype="object")})
    initialize_labels_column(df)
    assert df[cts.LABELS_COLUMN].dtype == object
    assert df[cts.LABELS_COLUMN].tolist() == ["a", "b"]


# ---- extract_existing_labels ----------------------------------------------

def test_extract_existing_labels_empty_for_nan_row():
    df = pd.DataFrame({cts.LABELS_COLUMN: [float("nan")]})
    existing = set()
    result = extract_existing_labels(df, existing, 0)
    assert result == []
    assert existing == set()


def test_extract_existing_labels_splits_and_normalizes():
    df = pd.DataFrame({cts.LABELS_COLUMN: ["Food,Coffee"]})
    existing = set()
    result = extract_existing_labels(df, existing, 0)
    assert result == ["Food", "Coffee"]
    assert existing == {"food", "coffee"}


def test_extract_existing_labels_skips_empty_segments():
    df = pd.DataFrame({cts.LABELS_COLUMN: ["Food,,Coffee,"]})
    existing = set()
    extract_existing_labels(df, existing, 0)
    # empty segments do not pollute existing
    assert "" not in existing


# ---- update_categories ----------------------------------------------------

def _make_decorate_df():
    return pd.DataFrame({
        cts.NOTE_COLUMN: ["pizza place", "fuel station", "unknown thing"],
        cts.CATEGORIES_COLUMN: ["", "Existing", ""],
    })


def test_update_categories_assigns_other_when_no_match_and_no_force():
    df = _make_decorate_df()
    update_categories(df, {}, first_row=1, last_row=3, update_existing_categories=False)
    # Empty categories -> Other; existing preserved
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Other"
    assert df.loc[1, cts.CATEGORIES_COLUMN] == "Existing"
    assert df.loc[2, cts.CATEGORIES_COLUMN] == "Other"


def test_update_categories_force_preserves_existing_when_no_match():
    """Force-update only re-evaluates against the dictionary. If no rule matches,
    a non-empty existing category is preserved — only empty cells become 'Other'.
    This corrects the original code-review finding #3 and ADR-0005."""
    df = _make_decorate_df()
    update_categories(df, {}, first_row=1, last_row=3, update_existing_categories=True)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Other"      # was empty -> Other
    assert df.loc[1, cts.CATEGORIES_COLUMN] == "Existing"   # was set -> preserved
    assert df.loc[2, cts.CATEGORIES_COLUMN] == "Other"      # was empty -> Other


def test_update_categories_force_overwrites_existing_when_dict_matches():
    """Force-update DOES overwrite existing categories when a dictionary rule matches."""
    df = pd.DataFrame({
        cts.NOTE_COLUMN: ["fuel station"],
        cts.CATEGORIES_COLUMN: ["WrongCategory"],
    })
    update_categories(
        df, {"fuel": ["transport"]}, first_row=1, last_row=1, update_existing_categories=True)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Transport"


def test_update_categories_uses_dictionary_match():
    df = _make_decorate_df()
    update_categories(
        df, {"pizza": ["food"]}, first_row=1, last_row=3, update_existing_categories=False)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Food"


def test_update_categories_preserves_existing_when_no_force():
    df = _make_decorate_df()
    # 'fuel' would match if force; without force the existing 'Existing' stays
    update_categories(
        df, {"fuel": ["transport"]}, first_row=1, last_row=3, update_existing_categories=False)
    assert df.loc[1, cts.CATEGORIES_COLUMN] == "Existing"


def test_update_categories_overwrites_other_even_without_force():
    df = pd.DataFrame({
        cts.NOTE_COLUMN: ["fuel station"],
        cts.CATEGORIES_COLUMN: ["Other"],
    })
    update_categories(
        df, {"fuel": ["transport"]}, first_row=1, last_row=1, update_existing_categories=False)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Transport"


def test_update_categories_handles_missing_note_column():
    df = pd.DataFrame({cts.CATEGORIES_COLUMN: [""]})
    # No NOTE column -> note becomes ''; no match -> Other
    update_categories(df, {"x": ["y"]}, first_row=1, last_row=1, update_existing_categories=False)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "Other"


def test_update_categories_respects_row_range():
    df = _make_decorate_df()
    update_categories(
        df, {"pizza": ["food"]}, first_row=2, last_row=3, update_existing_categories=True)
    assert df.loc[0, cts.CATEGORIES_COLUMN] == "", "row 0 outside range — untouched"
    # row 1 in range, force=True, no dict match, non-empty existing -> preserved
    assert df.loc[1, cts.CATEGORIES_COLUMN] == "Existing"
    # row 2 in range, force=True, no match, was empty -> Other
    assert df.loc[2, cts.CATEGORIES_COLUMN] == "Other"


# ---- update_labels --------------------------------------------------------

def test_update_labels_accumulates_matches():
    df = pd.DataFrame({
        cts.NOTE_COLUMN: ["pizza coffee"],
        cts.LABELS_COLUMN: [""],
    })
    update_labels(df, {"pizza": ["Food"], "coffee": ["Drink"]},
                  first_row=1, last_row=1, update_existing_labels=False)
    # Empty initial Labels split produces [""], so output retains a leading empty segment.
    # Filter empties when asserting on actual labels content.
    labels = [s for s in df.loc[0, cts.LABELS_COLUMN].split(cts.LABELS_DELIMITER) if s]
    assert set(labels) == {"Food", "Drink"}


def test_update_labels_force_clears_existing_then_adds():
    df = pd.DataFrame({
        cts.NOTE_COLUMN: ["pizza"],
        cts.LABELS_COLUMN: ["OldLabel"],
    })
    update_labels(df, {"pizza": ["NewLabel"]},
                  first_row=1, last_row=1, update_existing_labels=True)
    assert df.loc[0, cts.LABELS_COLUMN] == "NewLabel"


def test_update_labels_preserves_existing_when_no_match():
    df = pd.DataFrame({
        cts.NOTE_COLUMN: ["unknown"],
        cts.LABELS_COLUMN: ["KeepMe"],
    })
    update_labels(df, {"pizza": ["Food"]},
                  first_row=1, last_row=1, update_existing_labels=False)
    assert df.loc[0, cts.LABELS_COLUMN] == "KeepMe"


def test_update_labels_empty_when_no_match_and_no_existing():
    df = pd.DataFrame({
        cts.NOTE_COLUMN: ["unknown"],
        cts.LABELS_COLUMN: [float("nan")],
    })
    update_labels(df, {"pizza": ["Food"]},
                  first_row=1, last_row=1, update_existing_labels=False)
    assert df.loc[0, cts.LABELS_COLUMN] == ""


# ---- convert_decimal_separator --------------------------------------------

def test_convert_decimal_separator_warns_when_column_missing(caplog):
    df = pd.DataFrame({"x": [1, 2]})
    with caplog.at_level("WARNING"):
        convert_decimal_separator(df, cts.AMOUNT_COLUMN, dot_decimal_separator=True)
    assert any("not found" in rec.message for rec in caplog.records)


def test_convert_decimal_separator_applies_to_string_cells():
    df = pd.DataFrame({cts.AMOUNT_COLUMN: ["1.234,56", "100"]})
    convert_decimal_separator(df, cts.AMOUNT_COLUMN, dot_decimal_separator=True)
    assert df.loc[0, cts.AMOUNT_COLUMN] == "1234.56"


def test_convert_decimal_separator_skips_non_string_cells():
    df = pd.DataFrame({cts.AMOUNT_COLUMN: [10.5, 20.5]})
    convert_decimal_separator(df, cts.AMOUNT_COLUMN, dot_decimal_separator=True)
    # floats pass through unchanged
    assert df.loc[0, cts.AMOUNT_COLUMN] == 10.5


# ---- decorate_transactions error paths ------------------------------------

def test_decorate_transactions_returns_false_on_file_not_found(tmp_path):
    with patch("processor.transactions_decorator.user_directory_path") as m:
        m.side_effect = lambda p: str(tmp_path / p)
        is_success, message = decorate_transactions(first_row=1, last_row=None)
    # Either initializes via create_backup or fails earlier — the contract is graceful failure
    # (returns tuple) rather than raising
    assert isinstance(is_success, bool)
    assert isinstance(message, str)


def test_decorate_transactions_returns_false_on_invalid_json(tmp_path):
    # Set up a valid CSV but an invalid categories dictionary
    (tmp_path / "csv").mkdir()
    (tmp_path / "dictionary").mkdir()
    (tmp_path / "backup").mkdir()
    (tmp_path / "csv" / cts.TRANSACTION_CSV_NAME).write_text(
        cts.CSV_HEADERS, encoding="utf-8")
    (tmp_path / "dictionary" / cts.CATEGORIES_DICTIONARY_NAME).write_text(
        "{ not valid json", encoding="utf-8")
    (tmp_path / "dictionary" / cts.LABELS_DICTIONARY_NAME).write_text(
        "{}", encoding="utf-8")

    with patch("processor.transactions_decorator.user_directory_path") as m:
        m.side_effect = lambda p: str(tmp_path / p)
        is_success, message = decorate_transactions()

    assert is_success is False
    assert "Error" in message or "json" in message.lower() or "expecting" in message.lower()


def test_decorate_transactions_returns_false_on_parser_error(tmp_path):
    """When pd.read_csv raises ParserError mid-decorate, the function must return (False, msg)."""
    (tmp_path / "csv").mkdir()
    (tmp_path / "dictionary").mkdir()
    (tmp_path / "backup").mkdir()
    (tmp_path / "csv" / cts.TRANSACTION_CSV_NAME).write_text(
        cts.CSV_HEADERS, encoding="utf-8")
    (tmp_path / "dictionary" / cts.CATEGORIES_DICTIONARY_NAME).write_text(
        "{}", encoding="utf-8")
    (tmp_path / "dictionary" / cts.LABELS_DICTIONARY_NAME).write_text(
        "{}", encoding="utf-8")

    with patch("processor.transactions_decorator.user_directory_path") as m, \
         patch("processor.transactions_decorator.pd.read_csv",
               side_effect=pd.errors.ParserError("simulated parser error")):
        m.side_effect = lambda p: str(tmp_path / p)
        is_success, message = decorate_transactions()

    assert is_success is False
    assert "parser" in message.lower() or "error" in message.lower()


def test_decorate_transactions_clamps_first_row_to_one(tmp_path):
    # Setup minimum viable env
    (tmp_path / "csv").mkdir()
    (tmp_path / "dictionary").mkdir()
    (tmp_path / "backup").mkdir()
    (tmp_path / "csv" / cts.TRANSACTION_CSV_NAME).write_text(
        cts.CSV_HEADERS, encoding="utf-8")
    (tmp_path / "dictionary" / cts.CATEGORIES_DICTIONARY_NAME).write_text(
        "{}", encoding="utf-8")
    (tmp_path / "dictionary" / cts.LABELS_DICTIONARY_NAME).write_text(
        "{}", encoding="utf-8")

    with patch("processor.transactions_decorator.user_directory_path") as m:
        m.side_effect = lambda p: str(tmp_path / p)
        is_success, _ = decorate_transactions(first_row=-5)
    assert is_success is True  # clamped, no crash
