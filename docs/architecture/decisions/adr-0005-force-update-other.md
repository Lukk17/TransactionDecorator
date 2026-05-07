# ADR-0005 — Force-update assigns `Other` only to empty cells; existing values are preserved

- Status: Accepted
- Date: 2026-05-06
- Revised: 2026-05-07 (corrected to match actual code behavior — see "Correction note" below)

## Context

`update_categories(..., update_existing_categories=True)` (the "Force categories update" checkbox) re-runs categorization across the selected row range. The original ADR text claimed that force-update overwrites every non-matching row with `"Other"` even when a manual category was already set. **That was wrong.** A direct trace of the code (subsequently confirmed by `tests/unit/test_decorator_extra.py::test_update_categories_force_preserves_existing_when_no_match`) shows the actual behavior is more conservative.

## Decision

The `"Other"` fallback assignment runs only when **both** of these hold:

1. No dictionary keyword matched the row's `Note`, AND
2. Either the user did NOT enable force-update, OR the existing category cell is empty (`NaN`, `None`, `''`, `'nan'`).

Concretely:

| Existing category | Force-update | Dict matches? | Final value |
|---|---|---|---|
| empty / `Other` | off | yes | matched category |
| empty / `Other` | off | no | `Other` |
| non-empty (not `Other`) | off | — | preserved (no re-evaluation) |
| empty / `Other` | on | yes | matched category |
| empty / `Other` | on | no | `Other` |
| non-empty (not `Other`) | on | yes | overwritten with matched category |
| **non-empty (not `Other`)** | **on** | **no** | **preserved (NOT overwritten with `Other`)** |

The last row is the surprising one. Force-update means "re-evaluate against the dictionary," not "wipe everything that doesn't match." A manually-set category survives a force-update run as long as no dictionary rule contradicts it.

## Why this matters

A user who manually categorizes one row as `"Gift"`, then bumps a dictionary version that doesn't include "Gift" anywhere, then runs force-update: their manual `"Gift"` survives. They are NOT silently reset to `"Other"`.

The original (incorrect) ADR would have warned users to scope force-update to specific row ranges to protect manual edits. That advice is unnecessary — manual edits are protected automatically by the actual logic.

## Correction note

The first version of this ADR documented behavior that the code does not implement. Findings #3 in the original code review and the first version of this ADR both extrapolated from incomplete reading. Verified by direct execution in unit tests under `tests/unit/test_decorator_extra.py`. If a future contributor wants the "force = overwrite to Other on miss" behavior, they should propose it as an explicit change rather than assume it from this ADR.

## Consequences

- Manual category edits are durable across force-update runs — only the dictionary can supersede them.
- The `"Other"` value remains a sentinel for "I'm an empty cell that was processed but matched nothing" — never a marker for "I was a deliberate user choice that the dictionary disagrees with."
- The code-review finding #3 (recorded in chat history) is retracted. Documented here so future audits don't re-introduce the misconception.
