# AGENTS.md

This file provides shared instructions to all AI coding agents working in this repository (Claude Code, Kilo Code, OpenCode, Codex CLI). Standards and skills are imported from [agent-standards](https://github.com/Lukk17/agent-standards).

## Skills

This project includes agent skills in `.agents/skills/`. Invoke relevant skills before starting implementation work. Examples:

- `/code-reviewer` before reviewing code
- `/security-review` before auditing for vulnerabilities
- `/coding-standards` before writing new code
- `/tdd-workflow` before adding features or fixing bugs

Slash commands may appear as `/name` or `/name.md` in your agent's autocomplete — use whichever your agent shows.

## Working With Agents

All supported agents read this `AGENTS.md` from the project root and auto-discover skills from `.agents/skills/`. Start your agent from the project root:

- **Claude Code** — run `claude`. Reads `.claude/CLAUDE.md`, which imports this file.
- **Kilo Code** — reads `AGENTS.md` automatically. Optional `kilo.jsonc` for extra config.
- **OpenCode** — reads `AGENTS.md` automatically. Optional `opencode.json` at project root.
- **Codex CLI** — run `codex`. Reads `AGENTS.md` automatically. Global settings in `~/.codex/config.toml`.

## OpenSpec Workflow

This project uses [OpenSpec](https://github.com/Fission-AI/OpenSpec) for spec-driven development. Specs and changes live under `openspec/`.

The full lifecycle (run inside your agent shell):

1. **Propose a change** — agent generates proposal, design, and `tasks.md` under `openspec/changes/`:
   ```text
   /opsx:propose add dark mode support
   ```
2. **Apply the code** — after reviewing/editing `tasks.md`, agent implements and checks off tasks:
   ```text
   /opsx:apply
   ```
3. **Verify and refine** — pass back logs or bug reports to refine:
   ```text
   /opsx:verify The toggle button is invisible on mobile. Fix it.
   ```
4. **Archive** — once tested, merge delta specs into `openspec/specs/` and archive the change folder:
   ```text
   /opsx:archive
   ```

Some agents render commands as `/opsx-propose.md` instead of `/opsx:propose` — both work; use what appears in your autocomplete.

Use multiline prompts when you need to include logs or detailed context with a command.

## What This Repo Is

Transaction Decorator is a desktop GUI application for cleaning, categorizing, and labeling personal bank transaction CSV exports. It imports raw bank CSVs, normalizes them, applies user-defined keyword dictionaries to assign `Category` and `Labels` columns, and produces a consolidated `allTransactions.csv`. The app is for individual end users managing their own finances and ships as a Windows installer (Inno Setup) and Linux `.deb` / snap packages.

Stack: Python 3.11, PySide6 6.6 (Qt), pandas 2.1, chardet, PyInstaller, pytest.

## Architecture

- **Framework**: PySide6 (Qt for Python) desktop GUI; frameless window with a custom title bar and themed widgets.
- **Layout**: Source under `src/`, tests under `test/`, dictionaries under `dictionary/`, working CSV data under `csv/`, automatic snapshots under `backup/`. Platform packaging lives in `windows/` (Inno Setup) and `linux/` (snap + deb).
- **Data flow**: bank CSV → import normalization (UTF-8, date unification, column mapping via `import-dictionary.json`, ignore rules) → `allTransactions.csv` → categorize + label pass driven by `dictionary/` JSON → decorated CSV. Every run snapshots the prior `allTransactions.csv` into `backup/` before mutation.
- **Required CSV schema**: `allTransactions.csv` must contain at least `Note` and `Labels`; categories and labels are derived from `Note`.
- **Packaging**: PyInstaller produces a frozen binary (see `TransactionDecorator.spec`); Inno Setup wraps it on Windows; `snapcraft.yaml` and `linux/` build the Linux artifacts.
- **Constraints**: Cross-platform (Windows + Linux); user-data paths differ per platform (see `docs/project-structure.md`); no network/server component — fully local desktop app.
- **Tests**: pytest, IDE run configs under `.run/`.