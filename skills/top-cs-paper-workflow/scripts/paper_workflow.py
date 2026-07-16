#!/usr/bin/env python3
"""Maintain metadata-only workflow state for a user-selected paper project."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path, PureWindowsPath
from typing import Any, Iterable

import yaml


SCHEMA_VERSION = 1
STATE_DIR_NAME = ".top-cs-paper"
MANIFEST_NAME = "workflow.yaml"
CHECKPOINTS = (
    "brief",
    "claims",
    "evidence-and-figures",
    "manuscript",
    "review",
    "response",
)
CHECKPOINT_STATES = {"pending", "in-progress", "blocked", "ready", "not-applicable"}
EVIDENCE_STATES = {"available", "partial", "planned", "missing", "unverified"}
ISSUE_STATES = {
    "unresolved",
    "evidence-needed",
    "drafted",
    "verified",
    "planned",
    "cannot-complete",
    "author-input-needed",
}
REVISION_STATES = {"planned", "drafted", "verified", "author-input-needed"}
MATERIAL_KINDS = {"manuscript", "data", "figure", "review", "reference", "other"}


class WorkflowError(RuntimeError):
    """A safe, user-facing workflow operation failed."""


def initial_manifest() -> dict[str, Any]:
    """Return a valid but deliberately incomplete workflow manifest."""

    return {
        "schema_version": SCHEMA_VERSION,
        "project": {
            "title": "Untitled paper project",
            "venue": "generic",
            "year": None,
            "paper_type": "empirical",
            "submission_stage": "draft",
            "author_confirmation": "pending",
        },
        "materials": [],
        "claims": [],
        "evidence": [],
        "figures": [],
        "review_issues": [],
        "revisions": [],
        "checkpoints": {checkpoint: "pending" for checkpoint in CHECKPOINTS},
    }


def resolve_project(value: str, *, create: bool = False) -> Path:
    """Resolve only the root explicitly selected by the caller."""

    project = Path(value).expanduser()
    if project.exists() and not project.is_dir():
        raise WorkflowError(f"project root is not a directory: {value}")
    if not project.exists():
        if not create:
            raise WorkflowError(f"project root does not exist: {value}")
        project.mkdir(parents=True, exist_ok=True)
    return project.resolve()


def workflow_path(project: Path) -> Path:
    state_dir = project / STATE_DIR_NAME
    if state_dir.exists():
        if not state_dir.is_dir():
            raise WorkflowError(f"workflow state path is not a directory: {STATE_DIR_NAME}")
        try:
            state_dir.resolve().relative_to(project)
        except ValueError as exc:
            raise WorkflowError(f"workflow state directory escapes the project root: {STATE_DIR_NAME}") from exc
    path = state_dir / MANIFEST_NAME
    if path.is_symlink():
        raise WorkflowError(f"workflow manifest must not be a symlink: {STATE_DIR_NAME}/{MANIFEST_NAME}")
    return path


def write_manifest(path: Path, manifest: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False)
    path.write_text(rendered, encoding="utf-8")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _validate_string_list(value: Any, label: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{label} must be a list")
        return
    if not all(_is_nonempty_string(item) for item in value):
        errors.append(f"{label} must contain only non-empty strings")
    if len(set(value)) != len(value):
        errors.append(f"{label} must not contain duplicate IDs")


def _validate_record_fields(
    record: Any,
    label: str,
    required: set[str],
    allowed: set[str],
    errors: list[str],
) -> dict[str, Any] | None:
    if not isinstance(record, dict):
        errors.append(f"{label} must be an object")
        return None
    missing = required - set(record)
    unexpected = set(record) - allowed
    if missing:
        errors.append(f"{label} is missing: {', '.join(sorted(missing))}")
    if unexpected:
        errors.append(f"{label} has unsupported fields: {', '.join(sorted(unexpected))}")
    return record


def _validate_records(
    manifest: dict[str, Any],
    key: str,
    id_key: str,
    required: set[str],
    allowed: set[str],
    list_fields: Iterable[str],
    string_fields: Iterable[str],
    errors: list[str],
) -> None:
    records = manifest.get(key)
    if not isinstance(records, list):
        errors.append(f"{key} must be a list")
        return
    identifiers: list[str] = []
    for index, candidate in enumerate(records):
        label = f"{key}[{index}]"
        record = _validate_record_fields(candidate, label, required, allowed, errors)
        if record is None:
            continue
        if not _is_nonempty_string(record.get(id_key)):
            errors.append(f"{label}.{id_key} must be a non-empty string")
        else:
            identifiers.append(record[id_key])
        for field in list_fields:
            _validate_string_list(record.get(field), f"{label}.{field}", errors)
        for field in string_fields:
            if not _is_nonempty_string(record.get(field)):
                errors.append(f"{label}.{field} must be a non-empty string")
    if len(set(identifiers)) != len(identifiers):
        errors.append(f"{key} contains duplicate {id_key} values")


def validate_manifest(manifest: Any) -> list[str]:
    """Validate the public schema shape without requiring jsonschema."""

    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["workflow manifest must be a mapping"]

    required_top = {
        "schema_version",
        "project",
        "materials",
        "claims",
        "evidence",
        "figures",
        "review_issues",
        "revisions",
        "checkpoints",
    }
    missing_top = required_top - set(manifest)
    unexpected_top = set(manifest) - required_top
    if missing_top:
        errors.append(f"workflow manifest is missing: {', '.join(sorted(missing_top))}")
    if unexpected_top:
        errors.append(f"workflow manifest has unsupported fields: {', '.join(sorted(unexpected_top))}")
    if type(manifest.get("schema_version")) is not int or manifest.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"schema_version must be {SCHEMA_VERSION}")

    project = manifest.get("project")
    project_required = {
        "title",
        "venue",
        "year",
        "paper_type",
        "submission_stage",
        "author_confirmation",
    }
    if not isinstance(project, dict):
        errors.append("project must be an object")
    else:
        missing = project_required - set(project)
        unexpected = set(project) - project_required
        if missing:
            errors.append(f"project is missing: {', '.join(sorted(missing))}")
        if unexpected:
            errors.append(f"project has unsupported fields: {', '.join(sorted(unexpected))}")
        if not _is_nonempty_string(project.get("title")):
            errors.append("project.title must be a non-empty string")
        if project.get("venue") not in {"www", "iclr", "icml", "generic", "other"}:
            errors.append("project.venue is unsupported")
        year = project.get("year")
        if year is not None and (not isinstance(year, int) or isinstance(year, bool) or not 2000 <= year <= 2100):
            errors.append("project.year must be null or an integer from 2000 to 2100")
        if project.get("paper_type") not in {"empirical", "algorithmic", "theoretical", "systems", "dataset-benchmark", "other"}:
            errors.append("project.paper_type is unsupported")
        if project.get("submission_stage") not in {"planning", "draft", "pre-submission", "review", "response", "camera-ready"}:
            errors.append("project.submission_stage is unsupported")
        if project.get("author_confirmation") not in {"pending", "confirmed", "not-required"}:
            errors.append("project.author_confirmation is unsupported")

    materials = manifest.get("materials")
    if not isinstance(materials, list):
        errors.append("materials must be a list")
    else:
        paths: list[str] = []
        for index, candidate in enumerate(materials):
            label = f"materials[{index}]"
            record = _validate_record_fields(candidate, label, {"path", "kind", "bytes", "sha256"}, {"path", "kind", "bytes", "sha256"}, errors)
            if record is None:
                continue
            path = record.get("path")
            if not _is_nonempty_string(path) or not is_safe_relative_path(path):
                errors.append(f"{label}.path must be a safe project-relative path")
            else:
                paths.append(path)
            if record.get("kind") not in MATERIAL_KINDS:
                errors.append(f"{label}.kind is unsupported")
            bytes_value = record.get("bytes")
            if not isinstance(bytes_value, int) or isinstance(bytes_value, bool) or bytes_value < 0:
                errors.append(f"{label}.bytes must be a non-negative integer")
            digest = record.get("sha256")
            if not _is_nonempty_string(digest) or len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
                errors.append(f"{label}.sha256 must be a lowercase SHA-256 digest")
        if len(set(paths)) != len(paths):
            errors.append("materials contains duplicate paths")

    _validate_records(
        manifest,
        "claims",
        "claim_id",
        {"claim_id", "statement", "evidence_ids", "figure_ids"},
        {"claim_id", "statement", "evidence_ids", "figure_ids"},
        ("evidence_ids", "figure_ids"),
        ("statement",),
        errors,
    )
    _validate_records(
        manifest,
        "evidence",
        "evidence_id",
        {"evidence_id", "claim_ids", "status"},
        {"evidence_id", "claim_ids", "status"},
        ("claim_ids",),
        (),
        errors,
    )
    _validate_records(
        manifest,
        "figures",
        "figure_id",
        {"figure_id", "claim_ids", "evidence_ids", "evidence_status"},
        {"figure_id", "claim_ids", "evidence_ids", "evidence_status"},
        ("claim_ids", "evidence_ids"),
        (),
        errors,
    )
    _validate_records(
        manifest,
        "review_issues",
        "issue_id",
        {"issue_id", "claim_ids", "action", "revision_ids", "status"},
        {"issue_id", "claim_ids", "action", "revision_ids", "status"},
        ("claim_ids", "revision_ids"),
        ("action",),
        errors,
    )
    _validate_records(
        manifest,
        "revisions",
        "revision_id",
        {"revision_id", "issue_ids", "status"},
        {"revision_id", "issue_ids", "status"},
        ("issue_ids",),
        (),
        errors,
    )

    for key, allowed in (("evidence", EVIDENCE_STATES), ("figures", EVIDENCE_STATES)):
        field = "status" if key == "evidence" else "evidence_status"
        for index, record in enumerate(manifest.get(key, [])):
            if isinstance(record, dict) and record.get(field) not in allowed:
                errors.append(f"{key}[{index}].{field} is unsupported")
    for index, record in enumerate(manifest.get("review_issues", [])):
        if isinstance(record, dict) and record.get("status") not in ISSUE_STATES:
            errors.append(f"review_issues[{index}].status is unsupported")
    for index, record in enumerate(manifest.get("revisions", [])):
        if isinstance(record, dict) and record.get("status") not in REVISION_STATES:
            errors.append(f"revisions[{index}].status is unsupported")

    checkpoints = manifest.get("checkpoints")
    if not isinstance(checkpoints, dict):
        errors.append("checkpoints must be an object")
    else:
        missing = set(CHECKPOINTS) - set(checkpoints)
        unexpected = set(checkpoints) - set(CHECKPOINTS)
        if missing:
            errors.append(f"checkpoints is missing: {', '.join(sorted(missing))}")
        if unexpected:
            errors.append(f"checkpoints has unsupported fields: {', '.join(sorted(unexpected))}")
        for checkpoint in CHECKPOINTS:
            if checkpoints.get(checkpoint) not in CHECKPOINT_STATES:
                errors.append(f"checkpoints.{checkpoint} is unsupported")
    return errors


def load_manifest(project: Path) -> tuple[Path, dict[str, Any]]:
    path = workflow_path(project)
    if not path.is_file():
        raise WorkflowError(f"workflow manifest does not exist: {STATE_DIR_NAME}/{MANIFEST_NAME}; run init first")
    try:
        manifest = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise WorkflowError(f"cannot parse workflow manifest: {exc}") from exc
    errors = validate_manifest(manifest)
    if errors:
        raise WorkflowError("invalid workflow manifest:\n- " + "\n- ".join(errors))
    return path, manifest


def is_safe_relative_path(value: str) -> bool:
    """Accept only canonical forward-slash paths contained by the project."""

    if not _is_nonempty_string(value):
        return False
    # Store one portable, canonical path form in the manifest.  Forward slashes
    # work on every supported host; backslashes would make the YAML contract
    # disagree with Windows traversal rules.
    if "\\" in value:
        return False
    native = Path(value)
    windows = PureWindowsPath(value)
    if native.is_absolute() or windows.is_absolute() or windows.drive:
        return False
    normalized = value.replace("\\", "/")
    return all(part not in {"", ".", ".."} for part in normalized.split("/"))


def project_file(project: Path, raw_path: str) -> tuple[Path, str]:
    """Resolve one explicitly named file and prove that it remains in project."""

    if not is_safe_relative_path(raw_path):
        raise WorkflowError(f"--include must be a safe relative path: {raw_path}")
    if Path(raw_path).parts[0] == STATE_DIR_NAME:
        raise WorkflowError(f"--include cannot index workflow state: {raw_path}")
    candidate = project.joinpath(*raw_path.replace("\\", "/").split("/"))
    try:
        resolved = candidate.resolve(strict=True)
    except FileNotFoundError as exc:
        raise WorkflowError(f"included file does not exist: {raw_path}") from exc
    try:
        relative = resolved.relative_to(project)
    except ValueError as exc:
        raise WorkflowError(f"included file escapes the project root: {raw_path}") from exc
    if not resolved.is_file():
        raise WorkflowError(f"included path is not a file: {raw_path}")
    return resolved, relative.as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def infer_material_kind(relative_path: str) -> str:
    suffix = Path(relative_path).suffix.lower()
    lower_name = Path(relative_path).name.lower()
    if any(token in lower_name for token in ("review", "rebuttal", "response")):
        return "review"
    if suffix in {".tex", ".md", ".docx", ".odt", ".rst"}:
        return "manuscript"
    if suffix in {".csv", ".tsv", ".json", ".jsonl", ".npy", ".npz", ".parquet"}:
        return "data"
    if suffix in {".png", ".jpg", ".jpeg", ".svg", ".eps", ".pdf"}:
        return "figure"
    if suffix in {".bib", ".ris", ".csl"}:
        return "reference"
    return "other"


def status_issues(manifest: dict[str, Any]) -> list[dict[str, str]]:
    """Return advisory workflow gaps after structural validation succeeds."""

    issues: list[dict[str, str]] = []

    def warn(code: str, message: str) -> None:
        issues.append({"code": code, "message": message})

    project = manifest["project"]
    if project["author_confirmation"] == "pending":
        warn("author-confirmation-pending", "Author confirmation is pending.")

    for checkpoint in CHECKPOINTS:
        state = manifest["checkpoints"][checkpoint]
        if state in {"pending", "in-progress", "blocked"}:
            warn(f"checkpoint-{state}", f"Checkpoint '{checkpoint}' is {state}.")

    claims = {record["claim_id"]: record for record in manifest["claims"]}
    evidence = {record["evidence_id"]: record for record in manifest["evidence"]}
    figures = {record["figure_id"]: record for record in manifest["figures"]}
    review_issues = {record["issue_id"]: record for record in manifest["review_issues"]}
    revisions = {record["revision_id"]: record for record in manifest["revisions"]}

    # A checkpoint labelled ready is a claim about the recorded handoff, not a
    # way to bypass an empty project state.  Optional stages can instead be
    # marked not-applicable, so these minimum artifacts remain conservative.
    if manifest["checkpoints"]["claims"] == "ready" and not claims:
        warn("ready-claims-missing-handoff", "The ready claims checkpoint has no recorded claim.")
    if manifest["checkpoints"]["evidence-and-figures"] == "ready":
        if not evidence:
            warn("ready-evidence-missing-handoff", "The ready evidence-and-figures checkpoint has no recorded evidence.")
        if not figures:
            warn("ready-figures-missing-handoff", "The ready evidence-and-figures checkpoint has no recorded figure handoff.")
    if manifest["checkpoints"]["manuscript"] == "ready" and not any(
        material["kind"] == "manuscript" for material in manifest["materials"]
    ):
        warn("ready-manuscript-missing-handoff", "The ready manuscript checkpoint has no recorded manuscript material.")

    for claim_id, claim in claims.items():
        if not claim["evidence_ids"]:
            warn("claim-missing-evidence", f"Claim '{claim_id}' has no linked evidence.")
        for evidence_id in claim["evidence_ids"]:
            target = evidence.get(evidence_id)
            if target is None:
                warn("claim-unknown-evidence", f"Claim '{claim_id}' references missing evidence '{evidence_id}'.")
            elif claim_id not in target["claim_ids"]:
                warn("claim-evidence-link-mismatch", f"Evidence '{evidence_id}' does not link back to claim '{claim_id}'.")
        for figure_id in claim["figure_ids"]:
            target = figures.get(figure_id)
            if target is None:
                warn("claim-unknown-figure", f"Claim '{claim_id}' references missing figure '{figure_id}'.")
            elif claim_id not in target["claim_ids"]:
                warn("claim-figure-link-mismatch", f"Figure '{figure_id}' does not link back to claim '{claim_id}'.")

    for evidence_id, item in evidence.items():
        if not item["claim_ids"]:
            warn("evidence-missing-claim", f"Evidence '{evidence_id}' has no linked claim.")
        if item["status"] != "available":
            warn("evidence-not-available", f"Evidence '{evidence_id}' is {item['status']}.")
        for claim_id in item["claim_ids"]:
            target = claims.get(claim_id)
            if target is None:
                warn("evidence-unknown-claim", f"Evidence '{evidence_id}' references missing claim '{claim_id}'.")
            elif evidence_id not in target["evidence_ids"]:
                warn("evidence-claim-link-mismatch", f"Claim '{claim_id}' does not link back to evidence '{evidence_id}'.")

    for figure_id, figure in figures.items():
        if not figure["claim_ids"]:
            warn("figure-missing-claim", f"Figure '{figure_id}' has no linked claim.")
        if figure["evidence_status"] != "available":
            warn("figure-evidence-not-available", f"Figure '{figure_id}' evidence is {figure['evidence_status']}.")
        if figure["evidence_status"] == "available" and not figure["evidence_ids"]:
            warn("figure-missing-evidence", f"Figure '{figure_id}' claims available evidence but has no linked evidence ID.")
        for claim_id in figure["claim_ids"]:
            target = claims.get(claim_id)
            if target is None:
                warn("figure-unknown-claim", f"Figure '{figure_id}' references missing claim '{claim_id}'.")
            elif figure_id not in target["figure_ids"]:
                warn("figure-claim-link-mismatch", f"Claim '{claim_id}' does not link back to figure '{figure_id}'.")
        for evidence_id in figure["evidence_ids"]:
            if evidence_id not in evidence:
                warn("figure-unknown-evidence", f"Figure '{figure_id}' references missing evidence '{evidence_id}'.")

    for issue_id, issue in review_issues.items():
        if issue["status"] != "verified":
            warn("review-issue-unresolved", f"Review issue '{issue_id}' is {issue['status']}.")
        if not issue["revision_ids"]:
            warn("review-issue-missing-revision", f"Review issue '{issue_id}' has no linked revision.")
        for claim_id in issue["claim_ids"]:
            if claim_id not in claims:
                warn("review-issue-unknown-claim", f"Review issue '{issue_id}' references missing claim '{claim_id}'.")
        for revision_id in issue["revision_ids"]:
            target = revisions.get(revision_id)
            if target is None:
                warn("review-issue-unknown-revision", f"Review issue '{issue_id}' references missing revision '{revision_id}'.")
            elif issue_id not in target["issue_ids"]:
                warn("review-revision-link-mismatch", f"Revision '{revision_id}' does not link back to issue '{issue_id}'.")

    for revision_id, revision in revisions.items():
        if revision["status"] != "verified":
            warn("revision-unverified", f"Revision '{revision_id}' is {revision['status']}.")
        if not revision["issue_ids"]:
            warn("revision-missing-review-issue", f"Revision '{revision_id}' has no linked review issue.")
        for issue_id in revision["issue_ids"]:
            target = review_issues.get(issue_id)
            if target is None:
                warn("revision-unknown-review-issue", f"Revision '{revision_id}' references missing issue '{issue_id}'.")
            elif revision_id not in target["revision_ids"]:
                warn("revision-review-link-mismatch", f"Review issue '{issue_id}' does not link back to revision '{revision_id}'.")
    return issues


def markdown_report(manifest: dict[str, Any], issues: list[dict[str, str]], strict: bool) -> str:
    lines = [
        "# Top CS Paper workflow status",
        "",
        f"- Schema: valid (v{manifest['schema_version']})",
        f"- Mode: {'strict' if strict else 'advisory'}",
        f"- Warnings: {len(issues)}",
        "",
        "## Checkpoints",
        "",
        "| Checkpoint | State |",
        "| --- | --- |",
    ]
    lines.extend(f"| {checkpoint} | {manifest['checkpoints'][checkpoint]} |" for checkpoint in CHECKPOINTS)
    lines.extend(["", "## Warnings", ""])
    if issues:
        lines.extend(f"- `{issue['code']}`: {issue['message']}" for issue in issues)
    else:
        lines.append("- None. The recorded workflow links are complete.")
    return "\n".join(lines) + "\n"


def json_report(manifest: dict[str, Any], issues: list[dict[str, str]], strict: bool) -> str:
    payload = {
        "schema_valid": True,
        "strict": strict,
        "checkpoints": manifest["checkpoints"],
        "warnings": issues,
        "warning_count": len(issues),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def command_init(args: argparse.Namespace) -> int:
    project = resolve_project(args.project, create=True)
    path = workflow_path(project)
    if path.exists() and not args.force:
        raise WorkflowError(f"workflow manifest already exists: {STATE_DIR_NAME}/{MANIFEST_NAME}; use --force to replace it")
    write_manifest(path, initial_manifest())
    print(f"Initialized {STATE_DIR_NAME}/{MANIFEST_NAME}.")
    return 0


def command_inventory(args: argparse.Namespace) -> int:
    project = resolve_project(args.project)
    path, manifest = load_manifest(project)
    material_by_path = {record["path"]: record for record in manifest["materials"]}
    indexed = 0
    for raw_path in args.include:
        source, relative = project_file(project, raw_path)
        material_by_path[relative] = {
            "path": relative,
            "kind": infer_material_kind(relative),
            "bytes": source.stat().st_size,
            "sha256": sha256_file(source),
        }
        indexed += 1
    manifest["materials"] = [material_by_path[key] for key in sorted(material_by_path)]
    write_manifest(path, manifest)
    print(f"Indexed {indexed} explicitly selected file(s); no file contents were copied.")
    return 0


def command_status(args: argparse.Namespace) -> int:
    project = resolve_project(args.project)
    _, manifest = load_manifest(project)
    issues = status_issues(manifest)
    report = json_report(manifest, issues, args.strict) if args.format == "json" else markdown_report(manifest, issues, args.strict)
    print(report, end="")
    return 1 if args.strict and issues else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Maintain metadata-only Top CS paper workflow state.")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init_parser = subcommands.add_parser("init", help="create a project-local workflow manifest")
    init_parser.add_argument("--project", required=True, help="user-selected paper project root")
    init_parser.add_argument("--force", action="store_true", help="replace an existing workflow manifest")
    init_parser.set_defaults(handler=command_init)

    inventory_parser = subcommands.add_parser("inventory", help="hash explicitly selected in-project files")
    inventory_parser.add_argument("--project", required=True, help="user-selected paper project root")
    inventory_parser.add_argument("--include", action="append", required=True, help="safe relative file path; may be repeated")
    inventory_parser.set_defaults(handler=command_inventory)

    status_parser = subcommands.add_parser("status", help="report workflow links and incomplete checkpoints")
    status_parser.add_argument("--project", required=True, help="user-selected paper project root")
    status_parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    status_parser.add_argument("--strict", action="store_true", help="return non-zero when warnings remain")
    status_parser.set_defaults(handler=command_status)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (OSError, WorkflowError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
