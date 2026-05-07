## Context

Linux distribution today: `.deb` (Debian/Ubuntu apt) and snap (Canonical Snap Store). Coverage gaps:

- Fedora, RHEL, openSUSE, Arch, Gentoo, Alpine — none have native packages.
- Snap confinement makes filesystem access user-hostile (manual `sudo snap connect` for `home` interface, defaults often leave the app unable to read user-chosen CSVs).
- `.deb` users on rolling-release derivatives or non-apt distros either build from source or skip the app.

Flatpak fills both gaps:

1. Single binary works on any modern Linux desktop with `flatpak` installed (effectively all major distros).
2. Permission model is explicit and survives upgrades: declare `--filesystem=home` once, the user grants on first run, done.
3. Flathub provides discovery, signed binary distribution, and an automated update bot.

## Goals / Non-Goals

**Goals:**

- One-command install from any Linux distro: `flatpak install flathub io.github.lukk17.TransactionDecorator`.
- Manifest sources tracked in repo so submission history is reproducible.
- Permissions broad enough that bank-CSV imports work without manual `flatpak override` post-install.
- App ships a Flathub listing with description, screenshot, license, and version.

**Non-Goals:**

- Replacing snap or deb. They stay for users with established preferences. Flatpak is additive.
- Full sandbox isolation. We need user filesystem access (the whole point of the app). Tightening sandboxing would defeat the use case.
- Submitting to non-Flathub flatpak repos (e.g., distro-specific repos). Flathub is the de facto standard.
- Snap-style auto-update channels. Flathub handles updates centrally.

## Decisions

### Decision 1: Reverse-DNS app ID `io.github.lukk17.TransactionDecorator`

**Choice:** App ID = `io.github.lukk17.TransactionDecorator`.

**Alternatives considered:**

- `org.transactiondecorator.app` — would need to own the domain.
- `com.github.lukk17.TransactionDecorator` — `com.github` is sometimes blocked by Flathub policy.

**Rationale:** `io.github.<user>.<App>` is the Flathub-recommended pattern for projects whose canonical home is a GitHub repo. No domain ownership required.

### Decision 2: Use `org.kde.Platform//6.6` runtime

**Choice:** `runtime: org.kde.Platform`, `runtime-version: '6.6'`.

**Alternatives considered:**

- `org.freedesktop.Platform//23.08` (more minimal) — would need to vendor PySide6 + Qt entirely, which adds ~150 MB to the build.
- `org.gnome.Platform//45` — wrong toolkit.

**Rationale:** The KDE runtime ships Qt 6.6.x natively, perfectly matching PySide6 6.11.x's Qt requirement. Smaller download, faster startup, less to vendor.

### Decision 3: Permissions = `--filesystem=home`, `--socket=wayland`, `--socket=fallback-x11`, `--share=ipc`

**Choice:** Broad home-directory access; standard display sockets.

**Alternatives considered:**

- `--filesystem=xdg-documents` only — narrower, but bank CSVs are often in `~/Downloads/` or `~/Desktop/`, not Documents.
- `--filesystem=host` — too broad; Flathub reviewers reject for non-system apps.

**Rationale:** `--filesystem=home` matches the actual user workflow (pick a CSV from anywhere in `$HOME`, write outputs back). Flathub accepts this for personal-finance apps with documented justification.

### Decision 4: Manifest sources in `linux/flatpak/` alongside `linux/snap/`

**Choice:** All flatpak sources colocated with snap sources under `linux/`.

**Rationale:** Mirrors existing structure; release engineers find both Linux pipelines side by side.

### Decision 5: Manual first submission, auto-bot afterwards

**Choice:** Hand-author the first manifest and submit to Flathub. After acceptance, configure Flathub's Flatpak External Data Checker to auto-PR new versions.

**Rationale:** First submission needs human iteration with reviewers. Subsequent versions can be fully automated since the source URL pattern is stable (GitHub Release tarball).

## Risks / Trade-offs

- **[Risk] Flathub review rejects the manifest** — common reasons: AppStream metadata gaps, missing screenshots, overly broad permissions, app ID disputes. → Mitigation: validate locally with `flatpak-builder` and `appstream-util validate`; expect 2–4 weeks of review iteration; keep the PR diff focused.
- **[Risk] PySide6 doesn't run cleanly on the KDE 6.6 runtime** — runtime version mismatches manifest in subtle ways (Qt 6.6.0 vs 6.6.3 patches). → Mitigation: pin PySide6 to a 6.11 patch known to work; test in `flatpak run`; fall back to vendoring PySide6 if the platform Qt is incompatible.
- **[Risk] Path resolution under flatpak sandboxing returns wrong directories** — `$HOME` inside flatpak is `~/.var/app/<id>/`, not the real home. `Environment.LINUX_PACKAGE` resolver expects FHS paths. → Mitigation: probe during build; add a `FLATPAK` branch to `Environment` if needed (likely; treat as an in-scope code change for this proposal).
- **[Risk] User confused by sandboxed paths** — backups land in `~/.var/app/<id>/data/backup/`, invisible from the regular file manager. → Mitigation: documentation; the in-app "Open Backup Directory" button must use the sandboxed path, not assume `$HOME`.
- **[Risk] Flathub bot auto-bumps a broken version** — auto-PR runs on every GitHub release; if the release is broken, the bot pushes broken to all users. → Mitigation: configure the bot to only watch tagged releases marked stable; manually approve the first 3–5 auto-PRs to confirm the pattern.
- **[Trade-off] Three Linux packages to maintain** — deb + snap + flatpak. Per-release effort goes up. → Mitigation: Flatpak's auto-bot eliminates per-release work for it. Net effort increases ~10 min per release, not 10x.

## Migration Plan

1. Author the manifest in `linux/flatpak/`.
2. Add `FLATPAK` to `Environment` enum if path probing reveals it's needed.
3. Build locally: `flatpak-builder --user --install --force-clean build-dir linux/flatpak/io.github.lukk17.TransactionDecorator.yaml`.
4. Run the app: `flatpak run io.github.lukk17.TransactionDecorator`.
5. Run the golden-path smoke from `docs/testing-strategy.md` against the flatpak-installed app.
6. Validate AppStream: `appstream-util validate linux/flatpak/io.github.lukk17.TransactionDecorator.metainfo.xml`.
7. Submit to Flathub.
8. After merge, configure Flatpak External Data Checker for auto-bumps.
9. Update README.md, ADR-0007, ADR-0003 (if Environment enum changed), `docs/linux-flatpak.md`.

**Rollback:** Submit a PR removing the app from Flathub. Local manifest stays.
