# ADR-0005 — Force-update assigns `Other` when no rule matches

- Status: Accepted
- Date: 2026-05-06

## Context

`update_categories(..., update_existing_categories=True)` (the "Force categories update" checkbox) re-runs categorization across the selected row range. When a row's `Note` matches no dictionary keyword, the existing `Category` is replaced with the literal string `"Other"` — even if the user previously set a meaningful value by hand.

This is surprising at first read, but intentional: force-update is meant as a clean re-categorization pass driven exclusively by the dictionary. Preserving manually-set categories under force-update would defeat the feature, since users typically toggle it after a dictionary rewrite to *reset* prior decisions.

## Decision

Keep the current behavior. Document it here and in `docs/dictionaries.md` so users understand that:

- Without force-update: existing non-empty, non-`Other` categories are preserved.
- With force-update: every row in the range is re-derived from the dictionary; misses become `Other`.

Manual edits to specific rows survive as long as you do not run with force-update enabled.

## Consequences

- Users who want to keep manual categories must avoid force-update on those rows (use `First Row` / `Last Row` to scope the run).
- A future enhancement could add a third mode "force, but skip rows without a dictionary match" — out of scope for now.
