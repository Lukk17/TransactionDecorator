import pytest

from processor.transactions_importer import parse_date


@pytest.mark.parametrize("raw,expected", [
    ("13.10.2023", "13.10.2023 00:00"),
    ("13.10.2023 10:00:00", "13.10.2023 10:00"),
    ("13.10.2023 10:00", "13.10.2023 10:00"),
    ("2023-10-13T10:00:00+00:00", "13.10.2023 10:00"),
    ("2023-10-13", "13.10.2023 00:00"),
    ("13-10-2023", "13.10.2023 00:00"),
    ("2023-10-13T10:00:00", "13.10.2023 10:00"),
    ("2023-10-13T10:00:00.123Z", "13.10.2023 10:00"),
])
def test_supported_formats(raw, expected):
    assert parse_date(raw) == expected


def test_unparseable_returns_none(caplog):
    with caplog.at_level("ERROR"):
        assert parse_date("not-a-date") is None
    assert any("Error parsing date" in rec.message for rec in caplog.records)
