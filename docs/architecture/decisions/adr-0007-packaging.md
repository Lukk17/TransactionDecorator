# ADR-0007 — Three packaging targets

- Status: Accepted
- Date: 2024-03-01

## Context

The app targets individual end users on personal machines, not engineers running `pip install`. Each platform has a dominant install convention.

## Decision

Build and publish three artifacts:

1. **Windows** — PyInstaller-frozen exe wrapped with **Inno Setup** into a single `.exe` installer.
2. **Debian / Ubuntu** — `.deb` package built via `dpkg-deb`, installs to `/usr/lib/transaction-decorator/` with user data under `/usr/share/transaction-decorator/`.
3. **Snap** — `snapcraft.yaml`-driven snap with confined filesystem access; user data lives under `$SNAP_USER_DATA`.

## Rationale

- Inno Setup is the de-facto Windows installer for small open-source apps.
- `.deb` is the native package for Debian/Ubuntu and integrates with apt/dpkg tooling.
- Snap covers Ubuntu 18.04+ and other distros that ship `snapd`, with auto-updates.

## Consequences

- Three release builds to maintain and version-bump in lockstep.
- Path resolution (see ADR-0003) must handle five environments (IDE / Win frozen / non-Win frozen / deb / snap).
- Snap confinement requires explicit interfaces; misconfiguration can hide files from the app.
