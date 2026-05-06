import numpy as np
import pandas as pd
import pytest

from processor.transactions_decorator import (
    add_label_if_new,
    invert_dictionary,
    normalize_string,
    replace_multiple_whitespaces,
    sort_dataframe_by_date,
)


def test_normalize_string_handles_polish_diacritics_and_whitespace():
    # Diacritic map is lowercase-only; uppercase letters pass through and are then lowercased.
    assert normalize_string("  żółta  łódka  ") == "zolta lodka"


def test_normalize_string_uppercase_diacritics_pass_through():
    # Documents current behavior: uppercase Polish chars are not folded, only lowercased.
    assert normalize_string("ŻÓŁW") == "żółw"


def test_normalize_string_handles_null_and_non_string():
    assert normalize_string(None) == ""
    assert normalize_string(np.nan) == ""
    assert normalize_string(42) == "42"


def test_invert_dictionary_swaps_keys_and_values():
    raw = {"Food": ["Pizza", "BURGER"], "Travel": ["Uber"]}
    inverted = invert_dictionary(raw)
    assert inverted["pizza"] == ["food"]
    assert inverted["burger"] == ["food"]
    assert inverted["uber"] == ["travel"]


def test_invert_dictionary_handles_label_collisions():
    raw = {"Food": ["Cafe"], "Drinks": ["Cafe"]}
    inverted = invert_dictionary(raw)
    assert sorted(inverted["cafe"]) == ["drinks", "food"]


def test_add_label_if_new_appends_when_absent():
    existing = set()
    labels = []
    first_update = add_label_if_new(existing, labels, ["Coffee"], False, True)
    assert labels == ["Coffee"]
    assert "coffee" in existing
    assert first_update is True


def test_add_label_if_new_skips_duplicates():
    existing = {"coffee"}
    labels = ["Coffee"]
    add_label_if_new(existing, labels, ["coffee"], False, True)
    assert labels == ["Coffee"]


def test_add_label_if_new_force_clears_then_appends():
    existing = {"old"}
    labels = ["old"]
    first_update = add_label_if_new(existing, labels, ["NEW"], True, True)
    assert labels == ["NEW"]
    assert existing == {"new"}
    assert first_update is False


def test_replace_multiple_whitespaces_collapses_strings():
    df = pd.DataFrame({"a": ["x   y", "z\t\tw"], "b": [1, 2]})
    out = replace_multiple_whitespaces(df)
    assert list(out["a"]) == ["x y", "z w"]
    assert list(out["b"]) == [1, 2]


def test_sort_dataframe_by_date_descending():
    df = pd.DataFrame({"Date": ["01.01.2024", "03.01.2024", "02.01.2024"], "v": [1, 3, 2]})
    out = sort_dataframe_by_date(df)
    assert list(out["v"]) == [3, 2, 1]


def test_sort_dataframe_missing_date_column_logs_and_returns(caplog):
    df = pd.DataFrame({"v": [1, 2]})
    with caplog.at_level("WARNING"):
        out = sort_dataframe_by_date(df)
    assert list(out["v"]) == [1, 2]
    assert any("not found" in rec.message for rec in caplog.records)
