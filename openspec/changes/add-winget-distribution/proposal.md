## Why

The Windows 11 default package manager is winget (`winget install <id>`). End users on modern Windows expect any consumer app to be installable that way; manually downloading an `.exe` and running an installer with SmartScreen warnings is an inferior path. Adding winget distribution is the cheapest packaging win available — the existing Inno Setup `.exe` already works as the underlying installer; we only add a manifest and submit a PR.

## What Changes

- Host the Inno Setup `.exe` on **GitHub Releases** with a stable URL pattern (already partially done; codify the pattern).
- Author a winget manifest set under `winget/` in the repo (3 YAML files per version: installer, defaultLocale, version).
- Submit the manifest as a PR to [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs) under the path `manifests/l/Lukk17/TransactionDecorator/<version>/`.
- On every subsequent release, regenerate the manifest with the new version and SHA-256 checksum, and submit a follow-up PR.
- Update README.md to document `winget install Lukk17.TransactionDecorator` as the recommended Windows install method.
- Update ADR-0007 (packaging) to add winget as a fourth distribution target.

## Capabilities

### New Capabilities

- `windows-winget-distribution`: Defines the manifest format, the GitHub Releases URL contract, and the per-release update workflow for winget submissions.

### Modified Capabilities

(none — `openspec/specs/` does not yet contain a packaging capability)

## Impact

- **Code**: none. Existing `windows/installer/windowsInstallScript.iss` produces the artifact winget will fetch.
- **New files**: `winget/manifests/<version>/Lukk17.TransactionDecorator.installer.yaml`, `Lukk17.TransactionDecorator.locale.en-US.yaml`, `Lukk17.TransactionDecorator.yaml`.
- **Docs**: README.md install table gets a winget row. ADR-0007 gets a winget row. New `docs/windows-winget.md` documents the per-release manifest update procedure.
- **Maintenance**: ~10 minutes per release to bump the manifest and submit the PR; first submission takes a few days for review.
- **Costs**: zero. No accounts, no fees.
