# ADR-0008 — Pandas 3 + Copy-on-Write

- Status: Accepted
- Date: 2026-05-06

## Context

Pandas 3.0 was released in late 2025. The 3.0 line makes Copy-on-Write (CoW) the only supported memory model, removes long-deprecated APIs (`DataFrame.append`, `Series.append`, `mangle_dupe_cols`, `error_bad_lines`, `delim_whitespace`, `infer_datetime_format`, `applymap`, `date_parser`, `squeeze`), and changes the default dtype for string columns returned by `pd.read_csv` from `object` to a new native `str` dtype (`StringDtype(storage='python', na_value=nan)`).

The migration was scoped via `openspec/changes/upgrade-pandas-3/` with an audit covering 18 risk patterns + 6 targeted runtime probes. All probes pass under `pytest -W error`.

## Decision

Pin `pandas==3.0.2` in `pyproject.toml`. Adopt the following contract for source code in `src/`:

1. **Copy-on-Write is the assumed memory model.** Every `df.loc[...]` write must produce its effect on the owning DataFrame (verified). Chained assignment (`df[col][i] = value`) is FORBIDDEN — pandas 3 silently no-ops it under CoW with a non-error warning. The only sanctioned write API is `df.loc[i, col] = value`.
2. **String columns default to the `str` dtype.** Code MUST use `pd.api.types.is_string_dtype()` rather than direct comparison to `'object'`. The new dtype is `StringDtype(storage='python', na_value=nan)`, NOT `string[pyarrow]` (a common misconception in third-party tutorials).
3. **The single-shot `pd.concat` contract.** The importer batches new rows into one `pd.DataFrame(new_rows)` and concatenates once. Per-row concat in a loop is FORBIDDEN — pandas 3 deprecates the pattern more aggressively and warns loudly.
4. **`pd.to_datetime` requires `format='mixed'` for date parsing.** In `sort_dataframe_by_date`, we pass `format='mixed', dayfirst=True` because pandas 3 picks ONE format and rejects mismatches when `format` is omitted, where pandas 2 auto-inferred per element. Production data is normalized via `parse_date()` so the test fixtures don't trigger the mismatch — but a user with manually-edited rows or legacy data would crash mid-decorate. The `format='mixed'` arg is backward-compatible with pandas 2.
5. **Test fixtures are NEVER regenerated across pandas major versions.** `pd.testing.assert_frame_equal` is dtype-strict and distinguishes `str` vs `object`. Regenerating a fixture under pandas 2 while the project is pinned to pandas 3 would create silent cross-version dtype hazards. Fixture regeneration is a separate, explicit change.
6. **`initialize_labels_column` elif wrinkle.** The branch `df[LABELS_COLUMN].dtype != 'object'` now triggers on every read under pandas 3 because the dtype is `str`, not `object`. The resulting `.astype('object')` is functionally a no-op cast. The branch is preserved as-is for pandas 2 fallback compatibility; cleanup is opportunistic, tracked separately.

## Alternatives considered

- **Stay on pandas 2.x indefinitely** — defers the work but pandas 2 is in maintenance only.
- **Refactor row-by-row `.loc` loops into vectorised form** — cleaner but expands scope; no functional benefit today.
- **Adopt `dtype_backend='pyarrow'` in `pd.read_csv`** — speculative; defer until a perf measurement justifies it.
- **Pin `numpy<2` defensively** — not needed today (`pandas 3.0.2` declares `numpy>=1.26.0`); revisit when a future pandas 3.x patch tightens it.

## Consequences

- Builds reproducibly install `pandas==3.0.2` + `numpy==1.26.4` (NumPy 2 NOT forced).
- `pyinstaller --clean` is mandatory for binary rebuilds — stale `_internal/` caches can hide hidden-import regressions.
- Frozen Windows / Linux deb / Linux snap rebuilds must be installed on a clean host and smoked end-to-end against the manual checklist in `docs/testing-strategy.md`. Dev-mode pytest does not exercise the bundler.
- The GUI startup log now prints `pandas.__version__` and `numpy.__version__` so packaged-binary verification is visible at boot.
- Future pandas 3.x patches that force NumPy 2 must be bundled as a separate `upgrade-numpy-2` proposal, not silently absorbed.

## References

- Migration proposal: `openspec/changes/upgrade-pandas-3/`
- Manual smoke + packaged-binary verification: `docs/testing-strategy.md`
- Pandas 3 release notes: https://pandas.pydata.org/docs/whatsnew/v3.0.0.html
