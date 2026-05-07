## Context

The app currently ships on Windows via a self-hosted Inno Setup `.exe` installer. Users discover it through the README, download manually, and bypass SmartScreen warnings. winget (Windows Package Manager, shipped with Windows 11 by default) is the closest thing to a native package manager for Windows and the dominant install path for modern Windows tooling.

Adding winget distribution is unusual among packaging additions because it requires NO new build artifact — winget pulls the exact same `.exe` we already produce. The work is purely manifest authoring + submission.

## Goals / Non-Goals

**Goals:**

- One-command install on Windows 11: `winget install Lukk17.TransactionDecorator`.
- Reproducible per-release manifest update so the version stays in sync with what we publish on GitHub Releases.
- Manifest sources live in this repo so the submission history is tracked alongside the code.

**Non-Goals:**

- Microsoft Store distribution. Different process (UWP/MSIX), much more work, not aligned with the existing Inno Setup pipeline.
- Code-signing the `.exe`. Worth doing eventually for SmartScreen, but orthogonal — winget accepts unsigned installers.
- Automating the PR submission to microsoft/winget-pkgs. Manual PR is fine for our release cadence.

## Decisions

### Decision 1: Manifest sources live in `winget/manifests/<version>/`

**Choice:** Keep all manifests in-repo at `winget/manifests/<version>/`.

**Alternatives considered:**

- Store only the latest manifest. Loses history; can't reproduce older submissions.
- Store in a separate repo. Splits release context.

**Rationale:** Per-release manifests are tiny (3 YAML files, ~20 lines each); historical record is valuable for diffing against past submissions when the winget reviewers ask questions.

### Decision 2: Use the publisher prefix `Lukk17`

**Choice:** Package ID = `Lukk17.TransactionDecorator`.

**Rationale:** Matches the GitHub username, which is already the canonical identifier for this project. winget review process matches publisher identity to GitHub repository ownership.

### Decision 3: Pin GitHub Releases URL pattern

**Choice:** The installer URL in the winget manifest MUST match `https://github.com/Lukk17/TransactionDecorator/releases/download/v<version>/TransactionDecoratorInstaller-<version>.exe`.

**Rationale:** winget validates URL stability — a 404 fails the PR. Fixing the pattern in this proposal forces the release process to upload the artifact to a predictable URL. Bonus: makes README install instructions copy-pasteable per version.

### Decision 4: Manual PR, not automation

**Choice:** Each release submits a hand-crafted PR to microsoft/winget-pkgs.

**Alternatives considered:** GitHub Actions integration via `wingetcreate` or `Komac`.

**Rationale:** Release cadence is low (a few times a year). Automation cost > manual cost at this rate.

## Risks / Trade-offs

- **[Risk] winget reviewer rejects the manifest** — common reasons: SHA-256 mismatch, invalid silent-install args, missing publisher metadata. → Mitigation: dry-run with `winget validate <manifest>` and `winget install --manifest <local-path>` before submitting.
- **[Risk] User installs old version because winget cache is stale** — winget refreshes on schedule; users can `winget source update` manually. → Acceptable.
- **[Risk] SmartScreen still triggers for unsigned installer** — winget does not bypass SmartScreen. Users see the same warning. → Mitigation: documented in ADR-0007. Code-signing is a separate proposal if/when we want to address it.
- **[Risk] Repo cluttered with old manifests** — every release adds 3 files. → Mitigation: the directory is small (~60 KB after 50 releases).

## Migration Plan

1. Author manifests for the current version under `winget/manifests/1.0.1/`.
2. Validate locally (`winget validate winget/manifests/1.0.1/`).
3. Test install from local path (`winget install --manifest winget/manifests/1.0.1/`).
4. Submit PR to microsoft/winget-pkgs.
5. After merge, update README.md and ADR-0007.
6. Document the per-release update procedure in `docs/windows-winget.md`.

**Rollback:** Submit a PR removing the manifest from microsoft/winget-pkgs. Local manifest sources stay (for history).
