# Bank-export integration test fixtures

These files are **anonymized real bank exports**. Every transaction from the original is preserved (same row count, same columns, same delimiter, same encoding, same line endings) so the importer is exercised against the exact format quirks each bank emits. **All identifying values have been replaced** so nothing committed here can be linked back to a real person:

| What was replaced | How |
|---|---|
| Personal & business names | Consistent fictional Polish surnames (cross-file consistent: same person in two files gets the same fake name) |
| Account numbers / IBANs | All zeros, exact original spacing preserved (`00 0000 0000 0000 0000 0000 0000`) |
| Card masks | `*0000` |
| Phone numbers (full + masked) | `48000000000` / `48000***000` |
| Personal addresses | `Anon Street X, 00-000 Anon City` (consistent mapping) |
| Apartment / unit numbers | `0000` |
| Policy / customer / invoice numbers | All zeros, format preserved |
| Specific identifying merchants (local restaurants, foreign-trip merchants, named businesses) | `Anon Merchant <letter>` (deterministic, consistent within a file) |
| Generic public merchants (Netflix / Allegro / Biedronka / Bolt / Uber / IKEA / etc.) | **Shuffled**: each occurrence randomly reassigned from a pool of 25 generic merchants. Frequency profile is destroyed (the user's actual subscription/spending pattern is no longer recoverable) but format-stress is preserved |
| Amounts | Multiplied by 1.17, format preserved (decimal separator, thousand separator, currency suffix all kept) |

| What was NOT changed | Why |
|---|---|
| Dates | Per user decision — without identifying linkage (names/accounts/exact-merchants/exact-amounts), dates alone aren't OSINT-correlatable |
| Row count / column count | Format-coverage requires the parser to handle the exact same shape as a real export |
| Polish diacritics, multi-line preambles, header-artifact patterns | These are the format quirks that the importer must handle correctly |

## Files

| File | Bank | Format quirks tested |
|---|---|---|
| `mbank.csv` | mBank (PL) | UTF-8 + `;` delim + multi-line preamble that `find_start_row` must skip + `#`-prefixed column headers + `YYYY-MM-DD` dates + `X,XX PLN` amounts with currency suffix |
| `nestbank_utf8.csv` | NestBank (PL) | UTF-8 + `,` delim + single-line preamble + `DD-MM-YYYY` dates + integer amounts + `Tytuł operacji` description column |
| `pekaobp.csv` | Pekao (PL) | UTF-8 + `;` delim + single header row + `DD.MM.YYYY` dates + comma-decimal amounts with space thousand separator (`5 390,74`) + apostrophe-prefixed account numbers (`'00...`) |
| `alior.csv` | Alior (PL) | UTF-8 + `;` delim + 1-line `Kryteria` preamble + `DD-MM-YYYY` dates + comma-decimal amounts + space-separated 7-group IBAN format + dual-account rows (Nadawcy/Odbiorcy) |

## Expected outputs

Each `expected/<bank>-expected.csv` is the canonical `allTransactions.csv` produced by `process_imported_csv` against the matching fixture. Used by `tests/import/bank_exports_test.py` for `pd.testing.assert_frame_equal` round-trip comparison.

## If you need to re-anonymize a fresh real export

These fixtures were anonymized once. If a future bank changes its export format and you need to regenerate, ask for a re-anonymization round — do **not** commit raw exports under any circumstances.
