# ADR-0001 — GUI framework: PySide6

- Status: Accepted
- Date: 2024-03-01

## Context

The app needs a cross-platform desktop GUI shipping on Windows and Linux, with a custom (frameless) window, themed widgets, and a small dependency footprint.

## Decision

Use **PySide6** (Qt for Python, LGPL).

## Rationale

- LGPL allows distribution in proprietary or freely licensed binaries without source-disclosure obligations on the application code.
- Native look + frameless-window support out of the box.
- Stable Python bindings maintained by Qt Company.
- pandas + chardet ecosystem already pulls in heavy dependencies; one Qt binding is acceptable.

## Alternatives considered

- **Tkinter** — built into Python, but the look feels dated and theming is limited.
- **PyQt5/6** — GPL by default, requires a commercial license for proprietary distribution.
- **Electron / web-based** — much larger binary footprint and a JS runtime to maintain.

## Consequences

- The packaged binary is large (~80 MB) due to bundled Qt runtime.
- Requires PySide6 6.6+ at build time on each target platform.
