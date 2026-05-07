## 1. Author the manifest

- [ ] 1.1 Create `linux/flatpak/io.github.lukk17.TransactionDecorator.yaml` declaring the KDE 6.6 runtime, PySide6 + chardet + pandas modules, and the `finish-args` permission list
- [ ] 1.2 Create `linux/flatpak/io.github.lukk17.TransactionDecorator.metainfo.xml` (AppStream metadata: name, summary, description, screenshots, OARS content rating, license, releases, content)
- [ ] 1.3 Create `linux/flatpak/io.github.lukk17.TransactionDecorator.desktop` (matching the snap desktop file but with the flatpak app ID)
- [ ] 1.4 Add at least one screenshot under `linux/flatpak/screenshots/` and reference it in the metainfo XML
- [ ] 1.5 Create `linux/flatpak/build.sh` wrapping `flatpak-builder --user --install --force-clean build-dir <manifest>` for local testing

## 2. Local build + smoke

- [ ] 2.1 Install `flatpak` and `flatpak-builder` on a Linux dev machine (any modern distro)
- [ ] 2.2 Run `linux/flatpak/build.sh` — must complete without errors
- [ ] 2.3 Validate AppStream: `appstream-util validate linux/flatpak/io.github.lukk17.TransactionDecorator.metainfo.xml` — must exit 0
- [ ] 2.4 Run the app: `flatpak run io.github.lukk17.TransactionDecorator`
- [ ] 2.5 Run the full golden-path smoke from `docs/testing-strategy.md` against the flatpak-installed app, paying close attention to: (a) file-picker can reach `~/Downloads/` and `~/Desktop/`, (b) `allTransactions.csv` writes succeed, (c) backup snapshots appear, (d) "Open CSV Directory" opens the right path

## 3. Path resolution probe (Environment enum)

- [ ] 3.1 During §2.5 smoke, verify `user_directory_path("csv")` returns a path the user can locate in their file manager. If the path is `~/.var/app/.../data/csv/` and the file manager reaches it, no code change needed
- [ ] 3.2 If the path resolution misbehaves under sandboxing (e.g., backups land outside `$XDG_DATA_HOME`), add a `FLATPAK` branch to `Environment` enum in `src/utils/utils.py` and route flatpak-specific paths through it. Add unit tests under `tests/unit/test_path_resolution.py` mirroring the existing snap-branch tests
- [ ] 3.3 If §3.2 was needed: update `docs/architecture/decisions/adr-0003-path-resolution.md` to add the FLATPAK row to the path-resolution decision tree, plus the corresponding Mermaid diagram (`docs/architecture/diagrams/path-resolution.mmd`)

## 4. Submit to Flathub

- [ ] 4.1 Fork `flathub/flathub`
- [ ] 4.2 Open a new-app submission PR per the Flathub submission guidelines, attaching the manifest, metainfo, desktop, and screenshot
- [ ] 4.3 Address reviewer feedback (typical first-round issues: tighten permissions, AppStream metadata gaps, screenshot dimensions). Iterate until merged
- [ ] 4.4 After merge, configure Flatpak External Data Checker (or its equivalent at the time) to auto-PR new releases when GitHub tags appear

## 5. Documentation

- [ ] 5.1 Update README.md install table — add a Flatpak row promoting `flatpak install flathub io.github.lukk17.TransactionDecorator` as the cross-distro Linux method
- [ ] 5.2 Create `docs/linux-flatpak.md` covering: initial Flathub submission, local-build instructions, the auto-bump bot config, manual fallback
- [ ] 5.3 Link `docs/linux-flatpak.md` from README docs section AND cross-reference from `linux/linux.md`
- [ ] 5.4 Update `docs/architecture/decisions/adr-0007-packaging.md` to add a Flatpak row alongside Inno Setup, deb, and snap. Include the rationale for keeping all three Linux paths (deb for apt-native users, snap for Ubuntu Software defaults, flatpak for everyone else)
- [ ] 5.5 Update `docs/architecture/index.md` if any new ADRs were created (ADR-0003 update only — no new ADR)

## 6. Release-process integration

- [ ] 6.1 Update `docs/development.md` "Releasing" section (if introduced by `upgrade-pytest-9` §5.5) to mention that flatpak is auto-bumped via the External Data Checker — no per-release action required after initial setup
- [ ] 6.2 Document manual override procedure for cases when the bot fails (most common: AppStream metainfo needs an updated `<release>` entry)

## 7. Spec lifecycle

- [ ] 7.1 Run `openspec validate add-flatpak-distribution`
- [ ] 7.2 After §1–§6 done, run `openspec archive add-flatpak-distribution`
