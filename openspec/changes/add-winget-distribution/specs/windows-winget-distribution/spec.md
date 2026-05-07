## ADDED Requirements

### Requirement: Manifest sources tracked in repo

The project SHALL keep winget manifest sources under `winget/manifests/<version>/` for every published version. Each version directory MUST contain three YAML files: `Lukk17.TransactionDecorator.installer.yaml`, `Lukk17.TransactionDecorator.locale.en-US.yaml`, `Lukk17.TransactionDecorator.yaml`.

#### Scenario: Manifest exists for the current pinned version

- **WHEN** a contributor reads `pyproject.toml [project] version` and looks under `winget/manifests/<that version>/`
- **THEN** all three required YAML files exist

### Requirement: GitHub Releases URL pattern

Every winget installer manifest SHALL reference an installer URL matching `https://github.com/Lukk17/TransactionDecorator/releases/download/v<version>/TransactionDecoratorInstaller-<version>.exe`. The release process MUST upload the Inno Setup `.exe` to that exact path.

#### Scenario: URL is valid before manifest submission

- **WHEN** a release engineer prepares to submit a winget manifest
- **THEN** `curl -fIL <installer URL>` returns HTTP 200 (or follows a redirect to 200)

### Requirement: SHA-256 checksum recorded in manifest

Every winget installer manifest SHALL include a SHA-256 checksum that matches the actual `.exe` at the release URL. Mismatched checksums MUST cause the PR to fail review.

#### Scenario: Checksum matches uploaded artifact

- **WHEN** a release engineer computes `Get-FileHash -Algorithm SHA256 <local .exe>` (PowerShell) or `sha256sum <local .exe>` (bash)
- **THEN** the value equals the `InstallerSha256` field in the installer manifest

### Requirement: Single-command install on Windows 11

The README SHALL document `winget install Lukk17.TransactionDecorator` as the recommended Windows install method, ahead of manual `.exe` download.

#### Scenario: README install table promotes winget

- **WHEN** a user reads the Windows row of the README install table
- **THEN** the first line is the winget command and the manual `.exe` download is shown as a fallback

### Requirement: Per-release update procedure documented

The project SHALL document the manifest update procedure in `docs/windows-winget.md`, covering: (a) bumping the version directory, (b) recomputing SHA-256, (c) running `winget validate`, (d) submitting the PR to microsoft/winget-pkgs.

#### Scenario: Release engineer follows the documented procedure

- **WHEN** the release engineer reads `docs/windows-winget.md` for a new release
- **THEN** the document walks them from a freshly-uploaded `.exe` to a submitted winget PR with no implicit knowledge required

### Requirement: ADR-0007 (packaging) lists winget

ADR-0007 in `docs/architecture/decisions/` SHALL list winget as one of the project's distribution targets, with rationale for why it does not replace the Inno Setup direct download.

#### Scenario: ADR documents the new target

- **WHEN** a contributor opens `docs/architecture/decisions/adr-0007-packaging.md`
- **THEN** the table of distribution targets includes a row for winget alongside Inno Setup, deb, and snap
