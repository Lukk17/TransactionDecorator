# ADR-0004 — Always snapshot `allTransactions.csv` before mutation

- Status: Accepted
- Date: 2024-03-01

## Context

The app rewrites `allTransactions.csv` in place on every "Run Processing" invocation. A bad dictionary edit, a buggy code path, or an unexpected file format can silently corrupt the user's only ledger.

## Decision

Before any write to `allTransactions.csv`, copy it into `backup/allTransactions.csv_<YYYYMMDDHHMMSS>.csv`. The backup is unconditional — no diffing, no retention policy.

## Consequences

- Recovery from any bad processing run is a manual file copy.
- The `backup/` directory grows unbounded; the user is expected to prune it occasionally.
- A future ADR may introduce a retention policy (keep last N, or last 30 days).
