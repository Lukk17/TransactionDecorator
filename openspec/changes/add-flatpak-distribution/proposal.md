## Why

The project currently distributes on Linux via `.deb` (Debian/Ubuntu only) and snap (Ubuntu-flavored, with confinement quirks). Neither covers Fedora, openSUSE, Arch, or other major distros, and snap users frequently complain about confinement restrictions on filesystem access. **Flatpak** is the closest thing to a universal Linux package format: works on every modern desktop distro, has a centralized app store ([Flathub](https://flathub.org)), and supports straightforward `--filesystem=home` permissions for the kind of filesystem access this app needs (reading bank-export CSVs, writing `allTransactions.csv` and dictionaries).

Adding Flatpak fills the cross-distro gap without abandoning the existing deb/snap targets — they remain for users who prefer them.

## What Changes

- Add a Flatpak manifest at `linux/flatpak/io.github.lukk17.TransactionDecorator.yaml` defining the build using `org.kde.Platform//6.6` runtime (matches PySide6 6.x).
- Configure permissions: `--filesystem=home` (read/write for user CSVs and dictionaries), `--share=ipc`, `--socket=wayland`, `--socket=fallback-x11`.
- Add AppStream metadata (`io.github.lukk17.TransactionDecorator.metainfo.xml`) and a desktop file matching Flathub conventions.
- Add a screenshot to ship with the AppStream metadata (Flathub listing requires it).
- Provide a build script at `linux/flatpak/build.sh` for local testing (`flatpak-builder --user --install build-dir <manifest>`).
- Submit the manifest to [Flathub](https://github.com/flathub/flathub) as a PR; iterate through review (~2–4 weeks).
- Update README.md install table and ADR-0007.

## Capabilities

### New Capabilities

- `linux-flatpak-distribution`: Defines the manifest format, runtime, permissions, build process, and Flathub submission contract.

### Modified Capabilities

(none — `openspec/specs/` does not yet contain a Linux-distribution capability)

## Impact

- **Code**: none in `src/`. Path resolution already handles "linux user-package" environment correctly; flatpak's `~/.var/app/io.github.lukk17.TransactionDecorator/data/` is reached via standard `XDG_DATA_HOME` semantics — verify `Environment.LINUX_PACKAGE` resolver works under flatpak sandboxing during the build.
- **New files**: `linux/flatpak/io.github.lukk17.TransactionDecorator.yaml` (manifest), `linux/flatpak/io.github.lukk17.TransactionDecorator.metainfo.xml` (AppStream), `linux/flatpak/io.github.lukk17.TransactionDecorator.desktop`, `linux/flatpak/build.sh`, plus screenshot(s) under `linux/flatpak/screenshots/`.
- **Docs**: README.md install table gets a Flatpak row. ADR-0007 gets a Flatpak row. New `docs/linux-flatpak.md` documents local build + Flathub submission.
- **Path resolution**: may need a `FLATPAK` branch in `Environment` enum if `LINUX_PACKAGE` doesn't naturally cover sandboxed paths. Confirmed during build.
- **Maintenance**: Flathub has a bot that auto-PRs version bumps when the source URL is a GitHub release; effectively zero per-release work after initial setup.
- **Costs**: zero. No accounts, no fees.
