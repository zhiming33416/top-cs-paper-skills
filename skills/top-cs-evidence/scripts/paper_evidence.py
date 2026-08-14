#!/usr/bin/env python3
"""Plan and record author-controlled claim-to-source evidence without downloading full text."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
VERIFY_SCRIPT = ROOT / "_shared" / "scripts" / "verify_citations.py"
BOUNDARY = "Metadata verification and claim entailment are separate; source support requires author-provided text or notes."
STATUSES = {"needed", "candidate", "verified", "partial", "conflicting", "not-found", "error"}
ENTAILMENT = {"not-checked", "needs-source-text", "supported", "partial", "contradicted", "not-applicable"}


class EvidenceError(RuntimeError):
    """Raise a user-safe validation error."""


def read_yaml(path: Path) -> Any:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise EvidenceError(f"cannot read YAML: {path}") from exc


def write_yaml(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value, allow_unicode=True, sort_keys=False), encoding="utf-8")


def claims_from(value: Any) -> list[dict[str, str]]:
    records = value.get("claims") if isinstance(value, dict) else value
    if not isinstance(records, list) or not records:
        raise EvidenceError("claims input must contain a non-empty 'claims' list")
    result: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise EvidenceError(f"claims[{index}] must be an object")
        claim_id, statement = record.get("claim_id"), record.get("statement")
        if not isinstance(claim_id, str) or not claim_id.strip() or not isinstance(statement, str) or not statement.strip():
            raise EvidenceError(f"claims[{index}] requires non-empty claim_id and statement")
        if claim_id in seen:
            raise EvidenceError(f"duplicate claim_id: {claim_id}")
        seen.add(claim_id)
        result.append({"claim_id": claim_id, "statement": statement})
    return result


def safe_relative(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise EvidenceError("note_path must be a non-empty project-relative POSIX path")
    if any(piece in {"", ".", ".."} for piece in value.split("/")):
        raise EvidenceError("note_path must be a canonical project-relative path")
    return value


def load_verifier() -> Any:
    spec = importlib.util.spec_from_file_location("citation_verifier", VERIFY_SCRIPT)
    if spec is None or spec.loader is None:
        raise EvidenceError("shared citation verifier is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def command_plan(args: argparse.Namespace) -> int:
    claims = claims_from(read_yaml(args.claims))
    plan = {
        "schema_version": 1,
        "boundary": BOUNDARY,
        "claims": [
            {
                **claim,
                "evidence_role": "author-result-or-literature",
                "recommended_source": "AUTHOR_INPUT_NEEDED",
            }
            for claim in claims
        ],
        "next_step": "Provide BibTeX/DOIs and author-reviewed excerpts or notes before marking support.",
    }
    write_yaml(args.output, plan)
    print(f"Wrote source plan for {len(claims)} claim(s): {args.output}")
    return 0


def command_verify(args: argparse.Namespace) -> int:
    verifier = load_verifier()
    fetcher = verifier.Fetcher(args.cache_dir, offline=not args.online, timeout=args.timeout, delay=args.delay)
    report = verifier.verify_bibliography(args.bib, list(args.sources), fetcher)
    report["online_lookup_authorized"] = bool(args.online)
    report["boundary"] = "Bibliographic metadata only; claim entailment is never inferred from metadata."
    write_yaml(args.output, report)
    print(f"Wrote citation metadata ledger: {args.output}")
    return 1 if report["summary"]["conflicting"] else 0


def command_map(args: argparse.Namespace) -> int:
    claims = claims_from(read_yaml(args.claims))
    ledger = read_yaml(args.ledger)
    notes = read_yaml(args.notes) if args.notes else {"sources": []}
    if not isinstance(ledger, dict) or not isinstance(ledger.get("records"), list):
        raise EvidenceError("ledger must be the YAML output from verify")
    notes_by_key = {
        item.get("citation_key"): item
        for item in notes.get("sources", [])
        if isinstance(item, dict) and isinstance(item.get("citation_key"), str)
    }
    claim_ids = {claim["claim_id"] for claim in claims}
    sources: list[dict[str, Any]] = []
    source_ids_by_claim: dict[str, list[str]] = {claim_id: [] for claim_id in claim_ids}
    for record in ledger["records"]:
        key = record.get("citation_key")
        if not isinstance(key, str) or not key:
            continue
        note = notes_by_key.get(key, {})
        mapped_claims = note.get("claim_ids", [])
        if not isinstance(mapped_claims, list) or not all(item in claim_ids for item in mapped_claims):
            raise EvidenceError(f"source mapping for {key} contains an unknown claim_id")
        requested_status = note.get("claim_entailment_status", "needs-source-text")
        if requested_status not in ENTAILMENT:
            raise EvidenceError(f"unsupported claim_entailment_status for {key}")
        note_path = safe_relative(note.get("note_path"))
        if requested_status in {"supported", "partial", "contradicted"} and note_path is None:
            requested_status = "needs-source-text"
        source_id = note.get("source_id", f"SRC-{len(sources) + 1:03d}")
        if not isinstance(source_id, str) or not source_id:
            raise EvidenceError("source_id must be a non-empty string")
        bibliographic_status = record.get("bibliographic_status", "error")
        if bibliographic_status not in STATUSES:
            raise EvidenceError(f"ledger has unsupported bibliographic status for {key}")
        sources.append({
            "source_id": source_id,
            "citation_key": key,
            "bibliographic_status": bibliographic_status,
            "claim_entailment_status": requested_status,
            "claim_ids": mapped_claims,
            "note_path": note_path,
        })
        for claim_id in mapped_claims:
            source_ids_by_claim[claim_id].append(source_id)
    output = {
        "schema_version": 1,
        "boundary": BOUNDARY,
        "claims": [{**claim, "source_ids": source_ids_by_claim[claim["claim_id"]]} for claim in claims],
        "sources": sources,
    }
    write_yaml(args.output, output)
    print(f"Wrote claim-to-source map: {args.output}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)
    plan = subcommands.add_parser("plan", help="create a source plan from a claim list")
    plan.add_argument("--claims", required=True, type=Path)
    plan.add_argument("--output", required=True, type=Path)
    plan.set_defaults(handler=command_plan)
    verify = subcommands.add_parser("verify", help="verify BibTeX metadata; offline by default")
    verify.add_argument("--bib", required=True, type=Path)
    verify.add_argument("--output", required=True, type=Path)
    verify.add_argument("--online", action="store_true", help="explicitly authorize public metadata lookup")
    verify.add_argument("--cache-dir", type=Path)
    verify.add_argument("--sources", nargs="+", choices=("crossref", "arxiv", "dblp"), default=["crossref", "arxiv", "dblp"])
    verify.add_argument("--timeout", type=float, default=15.0)
    verify.add_argument("--delay", type=float, default=0.2)
    verify.set_defaults(handler=command_verify)
    mapping = subcommands.add_parser("map", help="map author-reviewed notes to verified citation records")
    mapping.add_argument("--claims", required=True, type=Path)
    mapping.add_argument("--ledger", required=True, type=Path)
    mapping.add_argument("--notes", type=Path)
    mapping.add_argument("--output", required=True, type=Path)
    mapping.set_defaults(handler=command_map)
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
        return args.handler(args)
    except (EvidenceError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
