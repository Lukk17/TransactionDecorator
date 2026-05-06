# ADR-0002 — Categorization model: keyword dictionaries

- Status: Accepted
- Date: 2024-03-01

## Context

Each transaction must be assigned a `Category` and any number of `Labels`, derived from its `Note` field. The user owns their categorization scheme and wants deterministic, auditable rules — not opaque predictions.

## Decision

Use **user-edited JSON keyword dictionaries** (`categories-dictionary.json`, `labels-dictionary.json`) where each category/label maps to a list of substring keywords. Matching is case-insensitive and works on a normalized `Note` string (whitespace-collapsed, Polish diacritics folded).

## Alternatives considered

- **Trained classifier (sklearn / spaCy)** — would require labeled training data per user, opaque decisions, and ongoing maintenance. Overkill for the scale (hundreds of monthly rows).
- **Regex rules** — more powerful but harder for non-developers to maintain.

## Consequences

- 100% deterministic — same input always yields the same output.
- Users can audit and edit the rule set freely.
- First-match wins for categories; all matches accumulate for labels.
- Category collisions resolve by dictionary iteration order (insertion order in Python 3.7+).
