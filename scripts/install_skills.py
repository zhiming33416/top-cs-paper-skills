#!/usr/bin/env python3
"""Install or verify the skills and their shared dependency."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
EVIDENCE = ROOT / "evidence" / "derived"
UNITS = ("_shared", "top-cs-writing", "top-cs-polishing", "top-cs-reviewer", "top-cs-response", "top-cs-figure")


def differences(source: Path, target: Path) -> list[str]:
    issues: list[str] = []
    for src in sorted(source.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(source)
        dst = target / rel
        if not dst.is_file():
            issues.append(f"missing: {rel}")
        elif not filecmp.cmp(src, dst, shallow=False):
            issues.append(f"different: {rel}")
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="Codex skills directory")
    parser.add_argument("--check", action="store_true", help="Verify without copying")
    args = parser.parse_args()
    target = args.target.expanduser().resolve()
    if args.check:
        all_issues: list[str] = []
        for unit in UNITS:
            all_issues.extend(f"{unit}/{item}" for item in differences(SOURCE / unit, target / unit))
        all_issues.extend(
            f"_shared/evidence/derived/{item}"
            for item in differences(EVIDENCE, target / "_shared" / "evidence" / "derived")
        )
        if all_issues:
            print("Skill installation differs:")
            print("\n".join(f"- {item}" for item in all_issues))
            return 1
        print("Skill installation matches this repository.")
        return 0

    target.mkdir(parents=True, exist_ok=True)
    for unit in UNITS:
        shutil.copytree(SOURCE / unit, target / unit, dirs_exist_ok=True)
        print(f"Installed {unit} -> {target / unit}")
    shutil.copytree(EVIDENCE, target / "_shared" / "evidence" / "derived", dirs_exist_ok=True)
    print(f"Installed derived evidence -> {target / '_shared' / 'evidence' / 'derived'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
