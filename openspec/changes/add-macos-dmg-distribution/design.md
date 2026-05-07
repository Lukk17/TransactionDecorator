## Context

macOS support is a clean greenfield. The app is PySide6-based and pure Python — there is no fundamental reason it cannot run on macOS, only that we have never built it there.

Two paths exist for distributing macOS GUI apps to users:

1. **Mac App Store (MAS)** — sandboxed, requires Apple Developer Program ($99/yr), MAS-only API restrictions.
2. **Direct download (signed + notarized OR unsigned)** — flexible, supports any app, but unsigned binaries trigger Gatekeeper warnings.

This proposal targets path 2 in its UNSIGNED variant. Reasoning:

- Single-developer hobby app; $99/year is a meaningful ongoing cost.
- macOS user base is unknown — investing in the signed pipeline before validating demand is premature.
- Homebrew Cask requires code-signing, so it is also blocked by the same decision.
- The Gatekeeper bypass workflow is well-documented and widely accepted in the open-source macOS community (Audacity, Inkscape, etc. all distributed unsigned for years).

## Goals / Non-Goals

**Goals:**

- Working `.dmg` downloadable from GitHub Releases on every tagged version.
- macOS-aware path resolution: user data under `~/Library/Application Support/TransactionDecorator/`, NOT in `~/.local/share` (Linux-style) or alongside the `.app` bundle.
- Clear documentation of the Gatekeeper bypass so users know what to expect on first launch.
- CI-built artifacts so the maintainer never needs personal macOS hardware just for releases.

**Non-Goals:**

- Code-signing (Apple Developer Program required).
- Notarization (depends on signing).
- Homebrew Cask submission (depends on both above).
- Universal2 (Intel + Apple Silicon) binary in the first iteration — `macos-latest` GitHub runners are Apple Silicon, so the initial `.dmg` is ARM-only. Intel users can build from source (or wait for a follow-up).
- Auto-update (Sparkle, etc.).

## Decisions

### Decision 1: Bundle identifier `com.lukk17.transactiondecorator`

**Choice:** Bundle ID = `com.lukk17.transactiondecorator`.

**Alternatives considered:**

- `io.github.lukk17.transactiondecorator` (matching the flatpak ID) — macOS convention is `com.<entity>.<app>`, not `io.github.*`.

**Rationale:** macOS conventions matter for things like `defaults read` namespacing and App Store submission (if we ever go there). Aligning early avoids painful migration later.

### Decision 2: Path = `~/Library/Application Support/TransactionDecorator/`

**Choice:** macOS user data lives under `~/Library/Application Support/TransactionDecorator/`.

**Alternatives considered:**

- Reuse `~/.local/share/transaction-decorator/` (Linux-style) — works but violates macOS conventions, hides data from `Finder > Go > Library` users expect.
- `~/Documents/TransactionDecorator/` — too visible; Apple guidelines reserve Documents for user-curated files.

**Rationale:** Apple's File System Programming Guide is explicit: app-managed data goes in `~/Library/Application Support/<bundle name>/`. Matches user expectation and survives macOS migration tools.

### Decision 3: Apple Silicon only (no Universal2) for initial release

**Choice:** Build on `macos-latest` (Apple Silicon since GitHub deprecated Intel runners), ship ARM-only `.dmg`.

**Alternatives considered:**

- Universal2 — requires `lipo` to merge ARM + Intel binaries; doubles CI time; PySide6 wheels for Intel may need separate handling.
- Intel only — abandons new Mac users.

**Rationale:** Apple has effectively migrated the Mac line to Apple Silicon. Intel users who still need the app can build from source (documented in `docs/macos-install.md`). A future `add-macos-universal2` proposal can address the long tail when it matters.

### Decision 4: GitHub Actions `macos-latest` for builds

**Choice:** All macOS builds happen in CI; the maintainer never needs personal Mac hardware.

**Rationale:** GitHub-hosted `macos-latest` runners are free for public repos. Eliminates the "I don't own a Mac" blocker for the project maintainer.

### Decision 5: `dmgbuild` over `create-dmg`

**Choice:** Use `dmgbuild` (Python package) to produce the `.dmg`.

**Alternatives considered:**

- `create-dmg` (Bash / Node-based wrappers) — more deps, less Python-native.
- Hand-roll with `hdiutil` — too low-level.

**Rationale:** `dmgbuild` is pip-installable, works in CI without extra system tooling, and is configurable via a Python settings file that lives next to the spec.

## Risks / Trade-offs

- **[Risk] Gatekeeper warning scares away non-technical users.** → Mitigation: documented in `docs/macos-install.md` AND in README install table footnote. Loud and explicit. If audience ever broadens, file `add-macos-signed-dmg` proposal.
- **[Risk] First-launch `xattr` workaround stops working on a future macOS version.** Apple has tightened Gatekeeper several times. → Mitigation: monitor; if Apple removes the right-click bypass, move to signed builds. Failure mode: app installs but won't launch — visible immediately, not silent corruption.
- **[Risk] PySide6 macOS wheels lag Linux/Windows by a few patches.** → Mitigation: pin PySide6 to a version known to have macOS wheels (most recent 6.11.x do); test in CI on each pin bump.
- **[Risk] `Environment.FROZEN_MACOS` resolver is incorrect under PyInstaller `--windowed` mode.** PyInstaller bundles the Python interpreter inside `.app/Contents/MacOS/`; `sys.executable` points there, NOT to the user-visible `.app` location. → Mitigation: probe during build; resolve user data via `os.path.expanduser("~/Library/Application Support/TransactionDecorator")` rather than relative to `sys.executable`.
- **[Risk] CI builds work, but user-installed `.app` doesn't.** → Mitigation: download the CI artifact onto a real Mac (or Apple Silicon GitHub runner via `actions/cache`), install, run smoke. Cannot ship without this.
- **[Risk] `~/Library/Application Support/` invisible to user in Finder by default.** → Mitigation: app provides "Open Backup Directory" / "Open CSV Directory" buttons (already in GUI). User reaches the data via the app, not Finder navigation.
- **[Trade-off] Apple Silicon only.** Intel users cut off from the easy path. → Acceptable; Intel users can build from source. Universal2 is a future concern.
- **[Trade-off] No auto-update.** Users must manually re-download. → Acceptable for hobby app cadence.

## Migration Plan

1. Add `FROZEN_MACOS` to `Environment` enum + a resolver branch.
2. Write `mac/TransactionDecorator-macos.spec` PyInstaller spec.
3. Write `mac/dmgbuild-settings.py` and `mac/build-dmg.sh`.
4. Set up `.github/workflows/build-macos.yml` triggered on tag push, building both `.app` and `.dmg`, uploading as release asset.
5. Tag a pre-release version (e.g., `v1.1.0-rc1`) to exercise the workflow end-to-end.
6. Download the artifact, install on a real Mac (or Apple Silicon CI runner), verify Gatekeeper bypass works and the golden-path smoke passes.
7. Update README, ADR-0003, ADR-0007, write `docs/macos-install.md`.
8. Promote the pre-release to a real release once smoke passes.

**Rollback:** Remove the GitHub Actions workflow and stop publishing the `.dmg`. Existing downloads keep working; `Environment.FROZEN_MACOS` branch in source can stay (harmless dead code) or be removed in a follow-up.
