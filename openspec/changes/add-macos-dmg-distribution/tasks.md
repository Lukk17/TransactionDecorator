## 1. Source code: macOS Environment branch

- [ ] 1.1 Add `Environment.FROZEN_MACOS` value to the enum in `src/utils/utils.py`
- [ ] 1.2 Update `_detect_environment()` to return `FROZEN_MACOS` when `sys.frozen` is set AND `sys.platform == "darwin"` (this branch must come BEFORE the existing `FROZEN_OTHER` fallback)
- [ ] 1.3 Add `FROZEN_MACOS` resolver branch to `resource_path()`: returns paths under `<.app>/Contents/Resources/`. PyInstaller exposes this via `sys._MEIPASS` in onefile mode or `os.path.dirname(sys.executable) + "/../Resources/"` in onedir mode — verify the spec uses onedir for `.app` bundles
- [ ] 1.4 Add `FROZEN_MACOS` resolver branch to `user_directory_path()`: returns `os.path.expanduser("~/Library/Application Support/TransactionDecorator/" + rel)`
- [ ] 1.5 Add unit tests in `tests/unit/test_path_resolution.py` mirroring the existing snap-branch tests, using `monkeypatch.setattr(sys, "frozen", True)` + `monkeypatch.setattr(sys, "platform", "darwin")`
- [ ] 1.6 Run `pytest -W error` — all tests must pass

## 2. PyInstaller spec for macOS

- [ ] 2.1 Create `mac/TransactionDecorator-macos.spec` modeled on `TransactionDecorator.spec` but with `windowed=True`, `bundle_identifier='com.lukk17.transactiondecorator'`, and `console=False`
- [ ] 2.2 Generate or commit `icons/logo.icns` (macOS prefers `.icns`; convert from `icons/logo.png` via `iconutil` or use an online converter as a one-shot)
- [ ] 2.3 Test local build IF Mac available: `pyinstaller --clean mac/TransactionDecorator-macos.spec`. Otherwise defer to CI (§4)

## 3. .dmg build pipeline

- [ ] 3.1 Add `dmgbuild` to `[project.optional-dependencies] dev` (under a `mac` extras group if extras get crowded; otherwise reuse `dev`)
- [ ] 3.2 Create `mac/dmgbuild-settings.py` configuring: title (`Transaction Decorator <version>`), icon, background, window size, file layout (the `.app` bundle and an Applications symlink for drag-to-install)
- [ ] 3.3 Create `mac/build-dmg.sh` wrapping `dmgbuild -s mac/dmgbuild-settings.py "Transaction Decorator" out/TransactionDecorator-<version>.dmg`

## 4. GitHub Actions CI

- [ ] 4.1 Create `.github/workflows/build-macos.yml` triggered on `push: tags: ['v[0-9]+.[0-9]+.[0-9]+*']`
- [ ] 4.2 Workflow steps: checkout → setup Python 3.11 → `pip install -e .[dev]` → `pyinstaller --clean mac/TransactionDecorator-macos.spec` → `bash mac/build-dmg.sh` → upload `.dmg` as release artifact via `softprops/action-gh-release` or equivalent
- [ ] 4.3 Tag a pre-release (e.g., `v1.1.0-rc1`) to exercise the workflow end-to-end
- [ ] 4.4 Download the artifact onto a real Mac (or use a self-hosted Apple Silicon runner). Run the Gatekeeper bypass + golden-path smoke from `docs/testing-strategy.md`
- [ ] 4.5 If smoke fails: triage in CI logs first; iterate on the spec or workflow until smoke passes

## 5. Documentation

- [ ] 5.1 Create `docs/macos-install.md` covering:
  - Where to download the `.dmg` (GitHub Releases link template)
  - Drag-to-install instructions (open `.dmg`, drag app to Applications)
  - Gatekeeper bypass: right-click → Open (recommended) AND `xattr -dr com.apple.quarantine /Applications/TransactionDecorator.app` alternative
  - Where user data lives (`~/Library/Application Support/TransactionDecorator/`) and how to reach it (Finder > Go > Library, or `open ~/Library/Application\ Support/TransactionDecorator/` in Terminal)
  - Intel Mac users: build-from-source walkthrough
  - Uninstall instructions (drag `.app` to Trash, optionally delete `~/Library/Application Support/TransactionDecorator/`)
- [ ] 5.2 Update README.md install table — add a macOS row with the GitHub Release `.dmg` download URL and a footnote pointing to `docs/macos-install.md` for the Gatekeeper bypass
- [ ] 5.3 Update `docs/architecture/decisions/adr-0003-path-resolution.md` to add macOS to the per-environment decision tree
- [ ] 5.4 Update `docs/architecture/diagrams/path-resolution.mmd` to add the `FROZEN_MACOS` branch
- [ ] 5.5 Update `docs/architecture/decisions/adr-0007-packaging.md` to add a macOS row, marking it explicitly as "unsigned, Apple Silicon only" with a follow-up note about signing
- [ ] 5.6 Update `docs/project-structure.md` if needed — add `mac/` to the source-layout tree
- [ ] 5.7 Update `docs/testing-strategy.md` "Packaged binary verification" section to add a macOS subsection mirroring Windows / deb / snap

## 6. Release-process integration

- [ ] 6.1 Update `docs/development.md` "Releasing" section (introduced by `upgrade-pytest-9` §5.5) to include the macOS step (push tag → workflow auto-builds → manual smoke download → mark release "stable")
- [ ] 6.2 Confirm the version-bump command from `upgrade-pytest-9` §5.5 also touches `mac/TransactionDecorator-macos.spec` if it has version strings (PyInstaller specs typically don't, but verify)

## 7. Spec lifecycle

- [ ] 7.1 Run `openspec validate add-macos-dmg-distribution`
- [ ] 7.2 After §1–§6 done AND a successful real-Mac smoke, run `openspec archive add-macos-dmg-distribution`
