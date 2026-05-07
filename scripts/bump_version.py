#!/usr/bin/env python3
"""Single-command version bump.

Updates the version string everywhere the release process touches it.
See ADR-0009 / upgrade-pytest-9 §5.5.

Usage:
    python scripts/bump_version.py 1.1.0
    python scripts/bump_version.py --check 1.1.0   # dry-run
"""
import argparse
import os
import re
import sys


# Each entry: (path, regex with ONE capture group around the version, replacement template)
# The replacement uses {VERSION} as a placeholder for the new value.
TARGETS = [
    ("pyproject.toml",
     r'^(version\s*=\s*")[^"]+(")',
     r'\g<1>{VERSION}\g<2>'),
    ("linux/createDebFile.sh",
     r'^(PACKAGE_VERSION=")[^"]+(")',
     r'\g<1>{VERSION}\g<2>'),
    ("windows/installer/windowsInstallScript.iss",
     r'^(#define MyAppVersion ")[^"]+(")',
     r'\g<1>{VERSION}\g<2>'),
    ("snapcraft.yaml",
     r"^(version:\s*')[^']+(')",
     r"\g<1>{VERSION}\g<2>"),
    ("linux/snap/transaction_decorator.desktop",
     r'^(Version=)\S+',
     r'\g<1>{VERSION}'),
]


def bump_file(path: str, pattern: str, replacement: str, new_version: str, check_only: bool) -> bool:
    if not os.path.exists(path):
        print(f"  SKIP  {path}  (file not present)")
        return True

    with open(path, "r", encoding="utf-8") as f:
        original = f.read()

    repl = replacement.format(VERSION=new_version)
    updated, n_subs = re.subn(pattern, repl, original, flags=re.MULTILINE)

    if n_subs == 0:
        print(f"  WARN  {path}  (pattern not found — version line missing or already drifted)")
        return False
    if n_subs > 1:
        print(f"  WARN  {path}  (matched {n_subs} times — expected exactly 1)")
        return False

    if updated == original:
        print(f"  ok    {path}  (already at {new_version})")
        return True

    if check_only:
        print(f"  WOULD {path}")
        return True

    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(updated)
    print(f"  ok    {path}  (-> {new_version})")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="New version, e.g. 1.1.0")
    parser.add_argument("--check", action="store_true",
                        help="Dry-run: report what would change without writing")
    args = parser.parse_args()

    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[.-][\w.-]+)?", args.version):
        print(f"ERROR: invalid version format: {args.version}", file=sys.stderr)
        return 2

    print(f"{'CHECK' if args.check else 'BUMP'} -> {args.version}")
    all_ok = True
    for path, pattern, replacement in TARGETS:
        if not bump_file(path, pattern, replacement, args.version, args.check):
            all_ok = False

    if not all_ok:
        print("\nOne or more files could not be updated. Inspect WARN lines above.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
