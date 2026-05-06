import pytest

from utils.utils import normalize_number_format


@pytest.mark.parametrize("raw,expected", [
    ("1.234,56", "1234.56"),
    ("1234,56", "1234.56"),
    ("1,234.56", "1234.56"),
    ("1234.56", "1234.56"),
    ("100", "100"),
    ("100.00", "100.00"),
    ("-99.99", "-99.99"),
    ("-1.234,56", "-1234.56"),
    ("400.00000000", "40000000000"),  # historical European interpretation, see ADR-0006
])
def test_to_dot(raw, expected):
    assert normalize_number_format(raw, dot_decimal_separator=True) == expected


@pytest.mark.parametrize("raw,expected", [
    ("1.234,56", "1234,56"),
    ("1,234.56", "1234,56"),
    ("1234.56", "1234,56"),
    ("100", "100"),
    ("-99.99", "-99,99"),
])
def test_to_comma(raw, expected):
    assert normalize_number_format(raw, dot_decimal_separator=False) == expected


def test_unknown_format_falls_back_with_warning(caplog):
    with caplog.at_level("WARNING"):
        result = normalize_number_format("abc,def", dot_decimal_separator=True)
    assert result == "abc.def"
    assert any("Unrecognized number format" in rec.message for rec in caplog.records)
