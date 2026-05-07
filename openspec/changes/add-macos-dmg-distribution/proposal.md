## Why

The project currently has zero macOS support. macOS users cannot use Transaction Decorator at all. Adding a downloadable `.dmg` is the cheapest way to fix that without committing to the Apple Developer Program ($99/year) and the full code-signing + notarization pipeline that Homebrew Cask submission would require.

The trade-off is explicit: users will see Gatekeeper's "cannot be opened because the developer cannot be verified" warning on first launch. The workaround (right-click → Open, or `xattr -dr com.apple.quarantine`) is documented and well-understood by macOS users — but it IS a UX wart that makes this a "tech-savvy users only" macOS path. If the audience ever broadens, a follow-up `add-macos-signed-dmg` proposal can layer signing + notarization on top.

## What Changes

- Add `FROZEN_MACOS` branch to the `Environment` enum in `src/utils/utils.py`. macOS user data lands under `~/Library/Application Support/TransactionDecorator/`.
- Add `mac/TransactionDecorator-macos.spec` PyInstaller spec producing a `.app` bundle (windowed mode, bundle identifier `com.lukk17.transactiondecorator`).
- Add `mac/build-dmg.sh` wrapping `dmgbuild` (or `create-dmg`) to produce a `.dmg` from the `.app`.
- Add a GitHub Actions workflow `.github/workflows/build-macos.yml` that builds the `.app` + `.dmg` on `macos-latest` and uploads as a release artifact when a tag is pushed.
- Update README.md install table to include macOS with the `.dmg` download URL and the Gatekeeper bypass note.
- Update ADR-0003 (path resolution) to add macOS row.
- Update ADR-0007 (packaging) to add macOS row.
- Add `docs/macos-install.md` covering the right-click → Open workaround, the `xattr` command alternative, and what users should expect (path locations, log files).

**BREAKING for any future code:** `Environment.FROZEN_MACOS` becomes a new branch. Code that pattern-matches the enum exhaustively must add a case for it.

## Capabilities

### New Capabilities

- `macos-dmg-distribution`: Defines the macOS `.app` build, `.dmg` packaging, distribution via GitHub Releases, Gatekeeper bypass workflow, and macOS-specific path resolution (`~/Library/Application Support/`).

### Modified Capabilities

(none — `openspec/specs/` does not yet contain a packaging or path-resolution capability)

## Impact

- **Code**: 1 new branch in `Environment` enum (~5 lines). New resolver path for macOS user-data directory (~5 lines). No changes to processor, GUI, or tests beyond a new branch in `tests/unit/test_path_resolution.py`.
- **New files**: `mac/TransactionDecorator-macos.spec`, `mac/build-dmg.sh`, `mac/dmgbuild-settings.py`, `.github/workflows/build-macos.yml`, `docs/macos-install.md`.
- **Docs**: README.md install table gets a macOS row. ADR-0003 + ADR-0007 updated. New `docs/macos-install.md`.
- **CI**: GitHub Actions `macos-latest` runner used per release. Free tier includes macOS minutes for public repos.
- **Costs**: zero monetary. UX cost: macOS users see Gatekeeper warning on first launch.
- **Tests**: 1 new unit test for the FROZEN_MACOS resolver branch.

## Explicitly out of scope (track separately if/when needed)

- Code-signing with Apple Developer ID
- Notarization via `notarytool`
- Homebrew Cask submission (requires signed + notarized binary)
- Universal2 binary (Intel + Apple Silicon in one) — initial proposal targets Apple Silicon only via `macos-latest` runner; an Intel-arm follow-up can layer in cross-arch builds
- Auto-update infrastructure (Sparkle framework, etc.)
