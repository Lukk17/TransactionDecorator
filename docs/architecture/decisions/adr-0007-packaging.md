# ADR-0007 — Packaging targets and bundled-Python policy

- Status: Accepted
- Date: 2024-03-01
- Revised: 2026-05-07 (locked the bundled-Python policy across all channels)

## Context

The app targets individual end users on personal machines, not engineers running `pip install`. Each platform has a dominant install convention.

The earlier deb build attempted to declare `python3-pandas`, `python3-pyside6` etc. as `Depends:` so the system Python would supply the deps. That model is rejected — see "Bundled-Python policy" below.

## Decision

### Packaging targets

| Channel | Build | Status |
| --- | --- | --- |
| **Windows installer (.exe)** | PyInstaller frozen exe wrapped with Inno Setup | Active |
| **Linux .deb** | PyInstaller frozen binary wrapped with `dpkg-deb` | Active |
| **Linux snap** | PyInstaller frozen binary wrapped with `snapcraft` | Active |
| **Windows winget** | Same Inno Setup `.exe` published to GitHub Releases + winget manifest | Proposed (`add-winget-distribution`) |
| **Linux Flatpak** | PyInstaller frozen binary wrapped with `flatpak-builder` | Proposed (`add-flatpak-distribution`) |
| **macOS .dmg** | PyInstaller `.app` bundle wrapped with `dmgbuild` | Proposed (`add-macos-dmg-distribution`) |

### Bundled-Python policy (locked)

**Every distribution channel SHIPS a self-contained PyInstaller binary that embeds Python and every runtime dep from `pyproject.toml`.** No channel relies on the host's Python or on system-package versions of pandas / PySide6 / chardet / openpyxl. Concretely:

- `linux/createDebFile.sh` runs PyInstaller against `TransactionDecorator.spec` first, then packages the resulting binary into the `.deb`. The deb's `Depends:` line lists ONLY low-level Qt runtime libs (`libxcb-*`, `libx11-*`, `libfontconfig1`, `libdbus-1-3`, etc.) — no `python3-*` packages.
- `snapcraft.yaml` runs PyInstaller in the snap build, then dumps the binary into the snap. Same — no `python3-*` apt packages staged.
- Windows installer ships the PyInstaller `.exe` directly (always has).
- macOS dmg ships a PyInstaller `.app` bundle (per `add-macos-dmg-distribution`).
- Flatpak builds the same PyInstaller binary inside the Flathub build container (per `add-flatpak-distribution`).
- winget pulls the same Inno Setup `.exe` already produced for Windows (per `add-winget-distribution`).

This guarantees that **the user gets the exact same pinned versions** of pandas, PySide6, chardet, etc. that `pyproject.toml` declares — no apt-version-drift surprises, no "works on my distro, broken on the user's distro" reports.

## Rationale

- Inno Setup is the de-facto Windows installer for small open-source apps.
- `.deb` is the native package for Debian/Ubuntu users; we just stop using its Python dep model.
- Snap covers Ubuntu 18.04+ and other distros that ship `snapd`, with auto-updates.
- PyInstaller produces a single binary per platform — same build approach everywhere makes the release process uniform and predictable.

## Trade-offs of the bundled-Python policy

- **Larger artifacts.** Each channel ships ~80 MB instead of ~5 MB (the rest is bundled Python + Qt runtime). Acceptable on modern bandwidth.
- **PyInstaller hook compatibility.** New pip deps need to be checked against PyInstaller's hidden-imports list; see the comment block at the top of `TransactionDecorator.spec`.
- **One PyInstaller bug affects all channels.** Mitigated by the manual smoke checklist in `docs/testing-strategy.md` requiring per-platform verification before release.

## Consequences

- Per-release build effort is consistent across channels (run PyInstaller, wrap with the channel's packager, smoke test).
- Path resolution (see ADR-0003) handles five environments (IDE / Win frozen / non-Win frozen / deb / snap / macOS frozen / unknown).
- Adding a new runtime pip dep requires: (a) bump `pyproject.toml`, (b) add to `hiddenimports` in `TransactionDecorator.spec` if PyInstaller doesn't auto-discover, (c) re-smoke per platform.
- No more "but it works in dev, broken on Debian" — dev and packaged environments now run the exact same dep versions.
