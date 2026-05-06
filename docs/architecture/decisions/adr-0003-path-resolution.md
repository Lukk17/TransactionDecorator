# ADR-0003 — Per-environment path resolution

- Status: Accepted
- Date: 2024-06-01 (codified 2026-05-06)

## Context

The app runs in five distinct environments, each with different filesystem conventions:

1. **IDE / source checkout** — repo root contains `.idea/`, everything is colocated under the working tree.
2. **PyInstaller frozen Windows exe** — bundled resources live next to `sys.executable`; user data goes to `%APPDATA%\TransactionDecorator\`.
3. **PyInstaller frozen non-Windows** — fall back to a dev-style layout (best-effort).
4. **Linux `.deb` install** — bundled resources at `/usr/lib/transaction-decorator/`, user data at `/usr/share/transaction-decorator/`.
5. **Snap** — bundled resources under `$SNAP/usr/share/<snap-name>/`, user data under `$SNAP_USER_DATA/`.

Earlier code mixed all five branches into a single nested `if/elif` chain that was hard to reason about.

## Decision

Two clearly separated functions in `src/utils/utils.py`:

- `resource_path(rel)` — read-only bundled resources (icons, etc.).
- `user_directory_path(rel)` — user-writable data (CSVs, dictionaries, backups).

Both delegate to a single `_detect_environment()` returning an `Environment` enum, then dispatch to a small per-env resolver. Snap detection precedes the frozen check because snap can also set `sys.frozen`.

## Consequences

- Adding a new platform requires one new `Environment` value and two short resolvers.
- Environment detection is testable in isolation by monkeypatching `os.environ` and `sys.frozen`.
- `_repo_root()` is computed from `__file__`, never from `os.getcwd()`, so the IDE branch is robust to working-directory changes.
