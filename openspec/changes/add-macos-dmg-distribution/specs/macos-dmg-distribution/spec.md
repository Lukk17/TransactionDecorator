## ADDED Requirements

### Requirement: macOS Environment branch

The `Environment` enum in `src/utils/utils.py` SHALL include a `FROZEN_MACOS` value. The `_detect_environment()` function MUST return `FROZEN_MACOS` when `sys.frozen` is truthy AND `sys.platform == "darwin"`.

#### Scenario: Frozen macOS detection

- **WHEN** the app runs from a PyInstaller-built `.app` bundle on macOS
- **THEN** `_detect_environment()` returns `Environment.FROZEN_MACOS`

### Requirement: macOS user-data path

`user_directory_path(rel)` SHALL return `~/Library/Application Support/TransactionDecorator/<rel>` when the environment is `FROZEN_MACOS`. The path MUST be expanded via `os.path.expanduser`, NOT computed relative to `sys.executable` (PyInstaller `--windowed` puts the executable inside the bundle).

#### Scenario: User data lands under Library/Application Support

- **WHEN** the macOS app calls `user_directory_path("csv")`
- **THEN** the result is `<expanded ~>/Library/Application Support/TransactionDecorator/csv`

### Requirement: macOS resource path

`resource_path(rel)` under `FROZEN_MACOS` SHALL return paths under the `.app` bundle's `Contents/Resources/` directory (PyInstaller convention).

#### Scenario: Bundled icon resolves under .app

- **WHEN** the macOS app loads its window icon via `resource_path("icons/logo.png")`
- **THEN** the path resolves to `<.app>/Contents/Resources/icons/logo.png` and the file exists

### Requirement: PyInstaller spec produces a `.app` bundle

The project SHALL include a `mac/TransactionDecorator-macos.spec` file producing a windowed `.app` bundle with bundle identifier `com.lukk17.transactiondecorator`.

#### Scenario: Spec file exists with correct bundle ID

- **WHEN** a contributor reads `mac/TransactionDecorator-macos.spec`
- **THEN** the spec declares `windowed=True`, `bundle_identifier='com.lukk17.transactiondecorator'`, and references the icon under `icons/logo.icns`

### Requirement: `.dmg` build script

The project SHALL include `mac/build-dmg.sh` and `mac/dmgbuild-settings.py` that together wrap `dmgbuild` to produce a `.dmg` from the built `.app` bundle.

#### Scenario: Script produces .dmg from .app

- **WHEN** a developer runs `bash mac/build-dmg.sh` after a successful PyInstaller build
- **THEN** a `.dmg` file appears in the project's output directory containing the `.app` bundle and an Applications symlink for drag-to-install

### Requirement: GitHub Actions workflow builds and publishes on tag

The project SHALL include `.github/workflows/build-macos.yml` that triggers on tag push (e.g., `v1.*`), runs the PyInstaller + dmgbuild pipeline on `macos-latest`, and attaches the `.dmg` as a release asset.

#### Scenario: Tag push produces a release asset

- **WHEN** a maintainer pushes a tag matching `v[0-9]*.[0-9]*.[0-9]*`
- **THEN** the workflow runs, builds the `.dmg`, and uploads it to the matching GitHub Release

### Requirement: Gatekeeper bypass documented

The project SHALL include `docs/macos-install.md` documenting the Gatekeeper bypass workflow (right-click → Open OR `xattr -dr com.apple.quarantine TransactionDecorator.app`) and explaining what users should expect on first launch.

#### Scenario: User encounters the warning and resolves it

- **WHEN** a macOS user follows `docs/macos-install.md` after downloading the `.dmg`
- **THEN** the document walks them from "downloaded the dmg" through "successfully launched the app" with no implicit knowledge required

### Requirement: README install table includes macOS

The README install table SHALL include a macOS row showing the GitHub Release `.dmg` download URL and a clear note about the Gatekeeper bypass step.

#### Scenario: macOS user finds installation instructions

- **WHEN** a macOS user reads the README install section
- **THEN** they see a macOS row with the `.dmg` download link AND a footnote pointing to `docs/macos-install.md` for the Gatekeeper bypass

### Requirement: ADR-0003 lists macOS path resolution

ADR-0003 (`docs/architecture/decisions/adr-0003-path-resolution.md`) SHALL include macOS in the per-environment resolver decision tree, AND the corresponding Mermaid diagram (`docs/architecture/diagrams/path-resolution.mmd`) SHALL be updated to add the `FROZEN_MACOS` branch.

#### Scenario: ADR-0003 covers macOS

- **WHEN** a contributor reads ADR-0003
- **THEN** the document explicitly addresses macOS path conventions (Library/Application Support) AND the Mermaid diagram shows the FROZEN_MACOS decision branch

### Requirement: ADR-0007 lists macOS

ADR-0007 (`docs/architecture/decisions/adr-0007-packaging.md`) SHALL include macOS in the distribution targets table, with the unsigned status documented and the future-signed-build follow-up referenced.

#### Scenario: ADR-0007 documents macOS

- **WHEN** a contributor opens ADR-0007
- **THEN** the table includes a macOS row, the unsigned status is explicit, and a "Future: signed + notarized via Apple Developer Program ($99/yr) — separate proposal if/when justified" note appears

### Requirement: Apple Silicon only (initial release)

The first macOS release SHALL be Apple Silicon only (built on `macos-latest` GitHub runner). Universal2 (Intel + Apple Silicon) is explicitly out of scope; Intel users build from source per `docs/macos-install.md`.

#### Scenario: Workflow targets Apple Silicon

- **WHEN** the GitHub Actions workflow runs
- **THEN** it uses `runs-on: macos-latest` and produces an arm64 `.dmg`. Intel build instructions appear in `docs/macos-install.md` under "Intel Macs"
