## ADDED Requirements

### Requirement: Flatpak manifest sources tracked in repo

The project SHALL maintain Flatpak build sources under `linux/flatpak/`. The directory MUST contain at minimum the build manifest, AppStream metainfo XML, desktop file, and a build helper script.

#### Scenario: All required sources present

- **WHEN** a contributor lists `linux/flatpak/`
- **THEN** the directory contains `io.github.lukk17.TransactionDecorator.yaml`, `io.github.lukk17.TransactionDecorator.metainfo.xml`, `io.github.lukk17.TransactionDecorator.desktop`, and `build.sh`

### Requirement: App ID follows Flathub convention

The Flatpak app ID SHALL be `io.github.lukk17.TransactionDecorator` everywhere it appears (manifest, metainfo, desktop file, AppStream).

#### Scenario: ID consistency across files

- **WHEN** a reviewer greps `grep -r "io.github.lukk17.TransactionDecorator" linux/flatpak/`
- **THEN** every manifest/metadata file references the exact same ID with no variants

### Requirement: KDE 6.6 runtime

The manifest SHALL declare `runtime: org.kde.Platform` with `runtime-version: '6.6'` (or a later 6.x compatible with the pinned PySide6 version).

#### Scenario: Runtime matches PySide6 Qt

- **WHEN** a contributor compares the manifest runtime against `pyproject.toml` PySide6 pin
- **THEN** the Qt major version (6) matches and the minor version is within one of the PySide6's bundled Qt

### Requirement: Permissions documented and minimal

The manifest SHALL declare exactly these `finish-args` permissions and no others without an ADR:

- `--filesystem=home` — required for reading bank-export CSVs and writing `allTransactions.csv`
- `--socket=wayland` and `--socket=fallback-x11` — required for the Qt GUI
- `--share=ipc` — required for Qt event handling

#### Scenario: Permissions are explicit and bounded

- **WHEN** a reviewer reads `finish-args` in the manifest
- **THEN** every entry is one of the four permissions above; no `--filesystem=host`, `--share=network`, or other broad grants

### Requirement: AppStream metainfo passes validation

The AppStream metainfo XML SHALL pass `appstream-util validate` with zero errors before any Flathub submission.

#### Scenario: Validation runs clean

- **WHEN** a contributor runs `appstream-util validate linux/flatpak/io.github.lukk17.TransactionDecorator.metainfo.xml`
- **THEN** the command exits 0 with no errors (warnings about translations are acceptable)

### Requirement: Path resolution handles flatpak sandbox

If empirical testing reveals that `Environment.LINUX_PACKAGE` resolver returns wrong directories under flatpak sandboxing, the project SHALL add a `FLATPAK` branch to the `Environment` enum and route resolver decisions through it.

#### Scenario: User data lands in flatpak-isolated path

- **WHEN** the app runs under `flatpak run io.github.lukk17.TransactionDecorator`
- **AND** the user clicks "Run Processing"
- **THEN** `allTransactions.csv` is written under `~/.var/app/io.github.lukk17.TransactionDecorator/data/csv/` (or whichever sandbox path the runtime exposes), AND backup snapshots go to the matching `backup/` subdirectory

### Requirement: README install table promotes flatpak as cross-distro path

The README install table SHALL include a Flatpak row showing `flatpak install flathub io.github.lukk17.TransactionDecorator` as the recommended cross-distro Linux install method, alongside the existing deb and snap rows.

#### Scenario: README clearly differentiates the three Linux paths

- **WHEN** a user reads the README install section
- **THEN** the table clearly shows: deb (Debian/Ubuntu native), snap (Ubuntu Snap Store), Flatpak (any modern Linux desktop)

### Requirement: ADR-0007 lists flatpak

ADR-0007 in `docs/architecture/decisions/` SHALL include flatpak in the distribution targets table with rationale for keeping all three Linux paths.

#### Scenario: ADR documents the additional target

- **WHEN** a contributor opens `docs/architecture/decisions/adr-0007-packaging.md`
- **THEN** the table includes a flatpak row alongside Inno Setup, deb, and snap

### Requirement: Per-release update procedure documented

The project SHALL document the flatpak update procedure in `docs/linux-flatpak.md`, covering: (a) initial Flathub submission steps, (b) local-build instructions for testing, (c) the auto-bump bot configuration, (d) manual fallback if the bot fails.

#### Scenario: Release engineer follows documented procedure

- **WHEN** the release engineer reads `docs/linux-flatpak.md`
- **THEN** the document covers initial submission, local testing, and per-release update workflows
