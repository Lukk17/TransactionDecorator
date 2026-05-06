# Architecture

This directory holds architecture documentation for Transaction Decorator.

- [`decisions/`](decisions/) — Architecture Decision Records (ADRs), one per significant decision.
- [`diagrams/`](diagrams/) — Mermaid (`.mmd`) diagrams for components and flows.

## Decisions

| ID | Title | Status |
| --- | --- | --- |
| [ADR-0001](decisions/adr-0001-gui-framework.md) | GUI framework: PySide6 | Accepted |
| [ADR-0002](decisions/adr-0002-categorization-model.md) | Keyword-dictionary categorization (no ML) | Accepted |
| [ADR-0003](decisions/adr-0003-path-resolution.md) | Per-environment path resolution | Accepted |
| [ADR-0004](decisions/adr-0004-backup-on-write.md) | Always snapshot before mutation | Accepted |
| [ADR-0005](decisions/adr-0005-force-update-other.md) | Force-update assigns `Other` when no rule matches | Accepted |
| [ADR-0006](decisions/adr-0006-decimal-separator.md) | Decimal separator normalization | Accepted |
| [ADR-0007](decisions/adr-0007-packaging.md) | Three packaging targets (Inno Setup / snap / deb) | Accepted |

## Diagrams

| File | Purpose |
| --- | --- |
| [components.mmd](diagrams/components.mmd) | Top-level component graph |
| [import-flow.mmd](diagrams/import-flow.mmd) | Sequence: Import CSV |
| [decorate-flow.mmd](diagrams/decorate-flow.mmd) | Sequence: Run Processing |
| [path-resolution.mmd](diagrams/path-resolution.mmd) | Decision tree for resource/user paths |
