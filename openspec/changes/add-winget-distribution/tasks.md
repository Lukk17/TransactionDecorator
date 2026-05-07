## 1. Author the manifest

- [ ] 1.1 Create `winget/manifests/<current-version>/` (e.g., `winget/manifests/1.0.1/`)
- [ ] 1.2 Author `Lukk17.TransactionDecorator.yaml` (version manifest, schema 1.6.0+)
- [ ] 1.3 Author `Lukk17.TransactionDecorator.installer.yaml` with InstallerType: `inno`, the GitHub Releases URL, SHA-256, and silent-install args
- [ ] 1.4 Author `Lukk17.TransactionDecorator.locale.en-US.yaml` with publisher, package name, description, license, copyright

## 2. Local validation

- [ ] 2.1 Install winget CLI tools if not already present (`winget install Microsoft.WingetCreate`)
- [ ] 2.2 Run `winget validate winget/manifests/<version>/` — must return zero errors
- [ ] 2.3 Test local install: `winget install --manifest winget/manifests/<version>/` on a clean Windows account or VM
- [ ] 2.4 Run the golden-path smoke from `docs/testing-strategy.md` against the winget-installed app
- [ ] 2.5 Uninstall via winget (`winget uninstall Lukk17.TransactionDecorator`) and verify clean removal

## 3. Submit to microsoft/winget-pkgs

- [ ] 3.1 Fork `microsoft/winget-pkgs`
- [ ] 3.2 Copy the local manifests to `manifests/l/Lukk17/TransactionDecorator/<version>/` in the fork
- [ ] 3.3 Open a PR; address any reviewer feedback (typical issues: silent-install flags, publisher metadata, scope)
- [ ] 3.4 After merge, verify `winget install Lukk17.TransactionDecorator` works from a clean Windows machine

## 4. Documentation

- [ ] 4.1 Update README.md install table — add a Windows row showing `winget install Lukk17.TransactionDecorator` as the primary method, with manual `.exe` download as fallback
- [ ] 4.2 Create `docs/windows-winget.md` documenting the per-release manifest update procedure (bump version dir, recompute SHA-256, validate, submit PR)
- [ ] 4.3 Link `docs/windows-winget.md` from README docs section AND from `docs/windows-build.md` (cross-reference)
- [ ] 4.4 Update `docs/architecture/decisions/adr-0007-packaging.md` to add a winget row
- [ ] 4.5 Update `docs/architecture/index.md` if needed (no new ADR; just verify cross-references stay clean)

## 5. Release-process integration

- [ ] 5.1 Update `docs/development.md` "Releasing" section (introduced by `upgrade-pytest-9` §5.5) to add the winget step after the GitHub Release upload
- [ ] 5.2 Confirm the version-bump command from `upgrade-pytest-9` §5.5 also touches the winget manifest version directory name (or document that the winget manifest is bumped manually post-release)

## 6. Spec lifecycle

- [ ] 6.1 Run `openspec validate add-winget-distribution`
- [ ] 6.2 After §1–§5 done, run `openspec archive add-winget-distribution`
