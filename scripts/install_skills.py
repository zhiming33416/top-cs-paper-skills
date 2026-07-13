#!/usr/bin/env python3
"""Install or verify Top CS Paper Skills for Codex."""

from __future__ import annotations

import argparse
import filecmp
import shutil
from collections.abc import Sequence
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
EVIDENCE = ROOT / "evidence" / "derived"
SKILLS = ("top-cs-writing", "top-cs-polishing", "top-cs-reviewer", "top-cs-response", "top-cs-figure")
UNITS = ("_shared", *SKILLS)


def default_target() -> Path:
    return Path.home() / ".codex" / "skills"


def selected_units(skills: Sequence[str] | None) -> tuple[str, ...]:
    if not skills:
        return UNITS
    selected = set(skills)
    return ("_shared", *(skill for skill in SKILLS if skill in selected))


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


def verify_installation(target: Path, units: Sequence[str]) -> list[str]:
    issues: list[str] = []
    for unit in units:
        issues.extend(f"{unit}/{item}" for item in differences(SOURCE / unit, target / unit))
    issues.extend(
        f"_shared/evidence/derived/{item}"
        for item in differences(EVIDENCE, target / "_shared" / "evidence" / "derived")
    )
    return issues


def install(target: Path, units: Sequence[str]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    for unit in units:
        shutil.copytree(SOURCE / unit, target / unit, dirs_exist_ok=True)
        print(f"Installed {unit} -> {target / unit}")
    shutil.copytree(EVIDENCE, target / "_shared" / "evidence" / "derived", dirs_exist_ok=True)
    print(f"Installed derived evidence -> {target / '_shared' / 'evidence' / 'derived'}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=default_target(),
        help="Codex skills directory (default: ~/.codex/skills)",
    )
    parser.add_argument(
        "--skill",
        action="append",
        choices=SKILLS,
        help="Install or verify one skill; repeat for multiple skills (default: all)",
    )
    parser.add_argument("--check", action="store_true", help="Verify without copying")
    parser.add_argument("--list", action="store_true", help="List available skills and exit")
    args = parser.parse_args(argv)
    if args.list:
        print("\n".join(SKILLS))
        return 0

    target = args.target.expanduser().resolve()
    units = selected_units(args.skill)
    if args.check:
        all_issues = verify_installation(target, units)
        if all_issues:
            print("Skill installation differs:")
            print("\n".join(f"- {item}" for item in all_issues))
            return 1
        print("Skill installation matches this repository.")
        return 0

    install(target, units)
    print("Start a new Codex session to load the installed skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
