#!/usr/bin/env python3
"""Install or verify Top CS Paper Skills for Codex or Claude Code.

The canonical distribution is ``skills/`` in this repository.  Installations
only copy files owned by this project and record their hashes in a hidden,
host-specific manifest inside the selected skills directory.  The installer
never reads or writes a host settings file.
"""

from __future__ import annotations

import argparse
import filecmp
import hashlib
import json
import shutil
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills"
EVIDENCE = ROOT / "evidence" / "derived"
SKILLS = (
    "top-cs-writing",
    "top-cs-polishing",
    "top-cs-reviewer",
    "top-cs-response",
    "top-cs-figure",
)
WORKFLOW_SKILL = "top-cs-paper-workflow"
UNITS = ("_shared", *SKILLS)
ALL_UNITS = (*UNITS, WORKFLOW_SKILL)
HOSTS = ("codex", "claude")
MANIFEST_PREFIX = ".top-cs-paper-skills-"
MANIFEST_SUFFIX = ".install.json"


def default_target(host: str = "codex") -> Path:
    """Return the conventional skills directory for a supported host."""
    if host == "claude":
        return Path.home() / ".claude" / "skills"
    return Path.home() / ".codex" / "skills"


def manifest_path(target: Path, host: str) -> Path:
    return target / f"{MANIFEST_PREFIX}{host}{MANIFEST_SUFFIX}"


def selected_units(skills: Sequence[str] | None, workflow: bool = False) -> tuple[str, ...]:
    """Select core skills, always including their shared dependency."""
    if workflow:
        return (*UNITS, WORKFLOW_SKILL)
    if not skills:
        return UNITS
    selected = set(skills)
    return ("_shared", *(skill for skill in SKILLS if skill in selected))


def differences(source: Path, target: Path) -> list[str]:
    """Compare every source file with its matching target file.

    This backwards-compatible helper intentionally has no host filtering;
    installation verification uses :func:`source_files` below.
    """
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


def _is_host_file(relative_to_unit: Path, host: str) -> bool:
    """Return whether a canonical skill file belongs in a host installation."""
    # ``agents/openai.yaml`` is Codex metadata, not part of Claude's skill
    # interface.  Everything else remains canonical and shared.
    return not (host == "claude" and relative_to_unit.parts[-2:] == ("agents", "openai.yaml"))


def _unit_source_files(unit: str, host: str, *, missing_ok: bool = False) -> dict[Path, Path]:
    source_unit = SOURCE / unit
    if not source_unit.is_dir():
        if missing_ok:
            return {}
        raise FileNotFoundError(f"Required skill source is missing: {source_unit}")

    result: dict[Path, Path] = {}
    for source_file in sorted(source_unit.rglob("*")):
        if not source_file.is_file():
            continue
        relative_to_unit = source_file.relative_to(source_unit)
        if _is_host_file(relative_to_unit, host):
            result[Path(unit) / relative_to_unit] = source_file
    return result


def source_files(units: Iterable[str], host: str, *, missing_ok: bool = False) -> dict[Path, Path]:
    """Map target-relative paths to canonical source files for selected units."""
    result: dict[Path, Path] = {}
    for unit in units:
        result.update(_unit_source_files(unit, host, missing_ok=missing_ok))

    if not EVIDENCE.is_dir():
        if not missing_ok:
            raise FileNotFoundError(f"Derived evidence source is missing: {EVIDENCE}")
        return result
    for source_file in sorted(EVIDENCE.rglob("*")):
        if source_file.is_file():
            result[Path("_shared") / "evidence" / "derived" / source_file.relative_to(EVIDENCE)] = source_file
    return result


def canonical_source_files(host: str) -> dict[Path, Path]:
    """Return all current public files that this host could own.

    ``missing_ok`` deliberately lets an old ownership manifest report a
    removed source file as stale instead of making verification crash.
    """
    return source_files(ALL_UNITS, host, missing_ok=True)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(value: str) -> Path | None:
    candidate = Path(value)
    if (
        candidate.is_absolute()
        or candidate.drive
        or not candidate.parts
        or any(part in {"", ".", ".."} for part in candidate.parts)
    ):
        return None
    return candidate


def _read_manifest(target: Path, host: str, *, required: bool = False) -> dict[str, Any] | None:
    path = manifest_path(target, host)
    if not path.is_file():
        if required:
            raise ValueError(f"Ownership manifest is missing: {path}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Ownership manifest is invalid: {path}") from error

    if not isinstance(payload, dict) or payload.get("schema_version") != 1 or payload.get("host") != host:
        raise ValueError(f"Ownership manifest has an unexpected format: {path}")
    if not isinstance(payload.get("files"), dict):
        raise ValueError(f"Ownership manifest has no file inventory: {path}")
    return payload


def _write_manifest(target: Path, host: str, files: Mapping[str, str]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "host": host,
        "files": dict(sorted(files.items())),
    }
    path = manifest_path(target, host)
    temporary = path.with_name(f"{path.name}.tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _manifest_files(manifest: Mapping[str, Any]) -> dict[str, str]:
    files = manifest.get("files", {})
    return {path: digest for path, digest in files.items() if isinstance(path, str) and isinstance(digest, str)}


def _verify_file(target: Path, relative: Path, source: Path) -> str | None:
    destination = target / relative
    if not destination.is_file():
        return f"missing: {relative.as_posix()}"
    if _sha256(source) != _sha256(destination):
        return f"different: {relative.as_posix()}"
    return None


def _assert_unsymlinked_parent(target: Path, relative: Path) -> None:
    """Keep an owned installation write inside its selected target directory."""
    current = target
    for part in relative.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise RuntimeError(f"Refusing to write through a symlinked install directory: {current}")


def verify_installation(target: Path, units: Sequence[str], host: str = "codex") -> list[str]:
    """Return source, ownership, and stale-file differences without copying."""
    target = target.expanduser().resolve()
    issues: list[str] = []
    expected = source_files(units, host)
    canonical = canonical_source_files(host)
    try:
        manifest = _read_manifest(target, host)
    except ValueError as error:
        return [str(error)]

    if manifest is None:
        issues.append(f"missing: {manifest_path(target, host).name}")
        tracked: dict[str, str] = {}
    else:
        tracked = _manifest_files(manifest)

    # The requested installation is checked even when it was not previously
    # owned (which makes --check useful after a manual/legacy copy).
    files_to_check = dict(expected)
    for raw_relative in tracked:
        relative = _safe_relative_path(raw_relative)
        if relative is None:
            issues.append(f"invalid tracked path: {raw_relative}")
            continue
        source = canonical.get(relative)
        if source is None:
            issues.append(f"stale: {relative.as_posix()}")
        else:
            files_to_check.setdefault(relative, source)

    for relative, source in sorted(files_to_check.items(), key=lambda item: item[0].as_posix()):
        issue = _verify_file(target, relative, source)
        if issue:
            issues.append(issue)
        if (
            relative in expected
            and raw_relative_key(relative) not in tracked
            and (target / relative).is_file()
            and manifest is not None
        ):
            issues.append(f"untracked: {relative.as_posix()}")
    return issues


def raw_relative_key(relative: Path) -> str:
    return relative.as_posix()


def install(target: Path, units: Sequence[str], host: str = "codex") -> None:
    """Copy selected canonical files and extend this host's ownership record."""
    target = target.expanduser().resolve()
    selected_files = source_files(units, host)
    target.mkdir(parents=True, exist_ok=True)
    try:
        existing = _read_manifest(target, host)
    except ValueError as error:
        raise RuntimeError(str(error)) from error
    owned = _manifest_files(existing) if existing is not None else {}

    for relative, source in sorted(selected_files.items(), key=lambda item: item[0].as_posix()):
        destination = target / relative
        _assert_unsymlinked_parent(target, relative)
        if destination.is_symlink():
            raise RuntimeError(f"Refusing to overwrite a symlinked installed file: {destination}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        owned[relative.as_posix()] = _sha256(destination)

    _write_manifest(target, host, owned)
    for unit in units:
        print(f"Installed {unit} -> {target / unit}")
    print(f"Installed derived evidence -> {target / '_shared' / 'evidence' / 'derived'}")


def prune_stale_files(target: Path, host: str) -> list[str]:
    """Delete only unchanged files tracked by this host that are no longer canonical."""
    target = target.expanduser().resolve()
    try:
        manifest = _read_manifest(target, host, required=True)
    except ValueError as error:
        raise RuntimeError(str(error)) from error

    canonical = canonical_source_files(host)
    owned = _manifest_files(manifest)
    retained: dict[str, str] = {}
    messages: list[str] = []
    for raw_relative, installed_hash in sorted(owned.items()):
        relative = _safe_relative_path(raw_relative)
        if relative is None:
            retained[raw_relative] = installed_hash
            messages.append(f"Preserved invalid tracked path: {raw_relative}")
            continue
        if relative in canonical:
            retained[raw_relative] = installed_hash
            continue

        destination = target / relative
        if not destination.exists():
            messages.append(f"Cleared missing stale record: {relative.as_posix()}")
            continue
        if not destination.is_file():
            retained[raw_relative] = installed_hash
            messages.append(f"Preserved stale non-file: {relative.as_posix()}")
            continue
        if _sha256(destination) != installed_hash:
            retained[raw_relative] = installed_hash
            messages.append(f"Preserved modified stale file: {relative.as_posix()}")
            continue
        destination.unlink()
        messages.append(f"Pruned stale file: {relative.as_posix()}")

    _write_manifest(target, host, retained)
    return messages


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        choices=HOSTS,
        default="codex",
        help="Skill host (default: codex)",
    )
    parser.add_argument(
        "--target",
        type=Path,
        help="Skills directory (default: ~/.codex/skills or ~/.claude/skills)",
    )
    parser.add_argument(
        "--skill",
        action="append",
        choices=SKILLS,
        help="Install one core skill; repeat for multiple skills (default: all core skills)",
    )
    parser.add_argument(
        "--workflow",
        action="store_true",
        help="Install the optional workflow coordinator and all five core skills",
    )
    parser.add_argument("--check", action="store_true", help="Verify without copying")
    parser.add_argument("--prune", action="store_true", help="Prune unchanged stale files owned by this host")
    parser.add_argument("--list", action="store_true", help="List available skills and exit")
    args = parser.parse_args(argv)
    if args.workflow and args.skill:
        parser.error("--workflow cannot be combined with --skill; it always installs all core skills")
    if args.check and args.prune:
        parser.error("--check cannot be combined with --prune")
    if args.list:
        print("\n".join((*SKILLS, WORKFLOW_SKILL)))
        return 0

    target = (args.target or default_target(args.host)).expanduser().resolve()
    units = selected_units(args.skill, workflow=args.workflow)
    if args.check:
        all_issues = verify_installation(target, units, args.host)
        if all_issues:
            print("Skill installation differs:")
            print("\n".join(f"- {item}" for item in all_issues))
            return 1
        print("Skill installation matches this repository.")
        return 0

    install(target, units, args.host)
    if args.prune:
        for message in prune_stale_files(target, args.host):
            print(message)
    session_name = "Codex" if args.host == "codex" else "Claude Code"
    print(f"Start a new {session_name} session to load the installed skills.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
