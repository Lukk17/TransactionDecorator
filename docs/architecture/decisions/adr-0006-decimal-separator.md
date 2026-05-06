# ADR-0006 — Decimal separator normalization rules

- Status: Accepted
- Date: 2026-05-06

## Context

Bank exports come in two locale conventions:

- **European / "standard"** — `1.234,56` (dot is thousand separator, comma is decimal).
- **English** — `1,234.56` (comma is thousand separator, dot is decimal).

Plus a long tail of edge cases: integers (`1234`), plain decimals with no thousand separator, sign-prefixed values, and unusual exports like `400.00000000` (probably an English plain decimal, but could be parsed as European thousand-grouped).

## Decision

`utils.normalize_number_format(s, dot_decimal_separator)` uses two permissive regexes:

- `_STANDARD_FORMAT = ^-?\d{1,3}(?:\.\d{3})*,?\d*$` — European
- `_ENGLISH_FORMAT  = ^-?\d{1,3}(?:,\d{3})*\.?\d*$` — English

Standard is checked **first**. A value like `400.00000000` matches the European pattern (`400` + `.000` + `00000`) and is therefore stripped to `40000000000`. This is intentional for backward compatibility with existing user CSVs and integration fixtures (`test/testing/import/expected/correctly-testData-semicolon-with-artefacts-importing.csv`).

If neither pattern matches, the function logs a warning and falls back to a best-effort `replace(',', '.')` (or the inverse).

## Known ambiguities

- `400.00000000` is treated as European `400_000_000_00` (= 40 billion when read as int). Users with English-locale exports of large precision must pre-normalize their CSVs.
- `1.234` could be either the integer 1234 (European) or the decimal 1.234 (English); we resolve as European.

## Consequences

- The behavior is consistent and testable.
- Users with unusual locales should choose the "English [.] decimal separator" checkbox at import time and verify a few sample rows after first import.
- Changing the regex would break existing user data already normalized under the current rules; do not do so without a migration plan.
