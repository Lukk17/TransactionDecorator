## Why

Pandas 3.0 was released in late 2025 and is now the upstream-supported line; pandas 2.x is in maintenance and will not receive new feature work. The 3.0 release also makes Copy-on-Write (CoW) the default and only supported memory model, removes a number of long-deprecated APIs (`DataFrame.append`, `Series.append`, several `read_csv` arguments), and changes the default dtype for string columns returned by `pd.read_csv` from `object` to a new native `str` dtype (`StringDtype(storage='python', na_value=nan)`). Migrating now lets us track upstream support, codify our reliance on the CoW model in source review, and verify that none of those surface changes silently regress our integration fixtures before pandas 2.x reaches EOL.

This proposal is grounded in two layers of evidence (not just "the test suite passes"):

1. **Source grep** of `src/` for every known pandas 3 removal/regression pattern (18 distinct patterns audited — see `design.md`).
2. **Targeted runtime probes** with `pandas==3.0.2` installed and `pytest -W error` (every warning category as an error). The probes deliberately exercise risk surfaces the existing test suite does not cover (empty-CSV concat, str-vs-object `assert_frame_equal`, chained-assignment behavior, CoW slice semantics, `dt.strftime` dtype, etc.).

Both layers ran clean. The audit surfaces two wrinkles (the `initialize_labels_column` elif always triggers under pandas 3 because string columns default to `str` not `object`; chained assignment now silently no-ops under CoW) — both already understood and captured in mitigations rather than requiring code changes.

## What Changes

- Bump `pandas==2.3.3` → `pandas==3.0.2` in `pyproject.toml` `[project] dependencies`.
- **BREAKING** for any future code: Copy-on-Write becomes always-on. Chained assignment (`df[col][i] = x`) silently no-ops. (Current code does not use this pattern; verified by grep.)
- **NUMPY (corrected)**: Probe install of pandas 3.0.2 against the project venv kept `numpy==1.26.4` — pandas 3.0.2 declares `numpy>=1.26.0`, NOT `>=2.0`. So no NumPy ABI bump is forced today. A future pandas 3.x patch may tighten this; the migration plan therefore includes pinning a known-good NumPy ceiling if the next bump shows drift.
- **BEHAVIORAL**: `pd.read_csv` returns string columns as the new `str` dtype rather than `object`. `is_string_dtype()` (already used in `replace_multiple_whitespaces`) handles both. `assert_frame_equal` will distinguish them in strict mode — risk only materializes if a fixture is regenerated under pandas 2 and compared under pandas 3, which the tasks explicitly forbid.
- **WRINKLE**: `initialize_labels_column`'s elif branch (`df[LABELS_COLUMN].dtype != 'object'`) now triggers on every read under pandas 3, casting `str` → `object`. Functionally a no-op; cosmetic cleanup deferred to a separate change.
- Add ADR-0008 capturing the CoW + `str` dtype + single-shot `pd.concat` + no-chained-assignment contract.

## Capabilities

### New Capabilities

- `pandas-runtime`: Defines which pandas major version the app targets, the CoW memory model assumption, the `str` dtype default for string columns, the single-shot `pd.concat` contract for the importer, the `df.loc[i, COL] = value` mutation pattern as the only sanctioned write API, and the dtype-strict `assert_frame_equal` contract for integration tests.

### Modified Capabilities

(none — `openspec/specs/` is currently empty; this proposal introduces the first capability touching pandas.)

## Impact

- **Code**: No source changes required. The two files that touch pandas extensively — `src/processor/transactions_decorator.py` and `src/processor/transactions_importer.py` — already pass under pandas 3 (verified via 18-pattern audit + 19 targeted probes + full pytest suite under `-W error`).
- **Tests**: All 59 tests pass on pandas 3.0.2 with strict warnings. No fixture regeneration required (and explicitly prohibited by the tasks to avoid str-vs-object dtype hazards).
- **Build/CI**: `pyproject.toml` pin update only. PyInstaller bundle size change is driven by pandas 3 alone (NumPy is unchanged); expect a few MB increase, not a wholesale ABI shift.
- **Packaging**: Frozen Windows exe and Linux deb/snap rebuild with new wheels. No Inno Setup or snapcraft.yaml changes required.
- **Runtime**: User CSV files unaffected — output format is unchanged.
- **ADR-0008** added to `docs/architecture/decisions/`.
