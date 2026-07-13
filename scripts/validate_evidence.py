#!/usr/bin/env python3
"""Validate evidence lineage, promotion thresholds, and policy freshness."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import yaml


RAW_KEYS = {"full_text", "abstract", "content", "review_content", "rebuttal_text", "response_text"}


def policy_diff(current: dict[str, Any], previous: dict[str, Any] | None) -> list[dict[str, Any]]:
    if previous is None:
        return []
    old = {item["source_id"]: item for item in previous.get("official_sources", [])}
    changes = []
    for item in current.get("official_sources", []):
        prior = old.get(item["source_id"])
        if prior is None:
            changes.append({"source_id": item["source_id"], "change": "added"})
        elif prior.get("sha256") != item.get("sha256") or prior.get("availability") != item.get("availability"):
            changes.append({"source_id": item["source_id"], "change": "content-or-availability-changed", "old_sha256": prior.get("sha256"), "new_sha256": item.get("sha256")})
    current_ids = {item["source_id"] for item in current.get("official_sources", [])}
    changes.extend({"source_id": source_id, "change": "removed"} for source_id in old if source_id not in current_ids)
    return changes


def validate(index: dict[str, Any], rules_doc: dict[str, Any], strict: bool = False, previous: dict[str, Any] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if index.get("schema_version") != 2:
        errors.append("corpus index must use schema_version 2")
    groups = ("official_sources", "paper_sources", "review_sources")
    sources = {}
    for group in groups:
        for source in index.get(group, []):
            source_id = source.get("source_id")
            if not source_id or source_id in sources:
                errors.append(f"missing or duplicate source_id: {source_id}")
            sources[source_id] = source
            if RAW_KEYS.intersection(source):
                errors.append(f"raw text field found in {source_id}")
            relative = Path(str(source.get("relative_path", "")))
            if relative.is_absolute() or ".." in relative.parts:
                errors.append(f"non-portable source path: {source_id}")
    heuristic_sources = []
    for source in index.get("paper_sources", []):
        if source.get("official_format_evidence") is not False:
            errors.append(f"public paper used as official format evidence: {source['source_id']}")
        if source.get("eligibility") == "primary-writing-evidence" and source.get("label_status") != "human-verified":
            heuristic_sources.append(source["source_id"])
    if heuristic_sources:
        warnings.append(f"heuristic labels require human review: {len(heuristic_sources)} paper sources")
    for source in index.get("official_sources", []):
        if source.get("availability") == "collected":
            if not source.get("sha256") or not source.get("last_verified"):
                errors.append(f"incomplete official provenance: {source['source_id']}")
            if int(source.get("expires_after_year", 0)) < int(source.get("valid_for_year", 0)):
                errors.append(f"invalid policy validity range: {source['source_id']}")
        elif source.get("verification_status") != "explicit-gap":
            errors.append(f"unavailable official source lacks explicit gap: {source['source_id']}")
    for rule in rules_doc.get("rules", []):
        rule_id = rule.get("rule_id", "unknown")
        ids = rule.get("source_ids", [])
        if rule.get("support_count") != len(ids) or len(ids) != len(set(ids)):
            errors.append(f"support count mismatch: {rule_id}")
            continue
        selected = []
        for source_id in ids:
            if source_id not in sources:
                errors.append(f"unresolved source {source_id}: {rule_id}")
            else:
                selected.append(sources[source_id])
                if sources[source_id].get("source_type") != rule.get("source_type"):
                    errors.append(f"source type mismatch {source_id}: {rule_id}")
        if rule.get("source_type") == "official-policy":
            if not selected or any(s.get("availability") != "collected" for s in selected):
                errors.append(f"hard rule lacks collected official source: {rule_id}")
        elif rule.get("source_type") == "accepted-title-verified-public-version":
            if rule.get("venue") == "cross-venue":
                if len(selected) < 6 or len({s.get("conference") for s in selected}) < 2:
                    errors.append(f"cross-venue threshold failed: {rule_id}")
            elif rule.get("venue") == "www":
                if len(selected) < 3 or any("Research" not in s.get("tracks", []) for s in selected):
                    errors.append(f"WWW Research threshold failed: {rule_id}")
            elif len(selected) < 3 or len({t for s in selected for t in s.get("tracks", [])}) < 2:
                errors.append(f"venue soft-rule threshold failed: {rule_id}")
        elif rule.get("source_type") == "historical-public-review":
            if len(selected) < 5 or len({s.get("decision") for s in selected}) < 2:
                errors.append(f"historical-review threshold failed: {rule_id}")
    targets = index.get("targets", {})
    for conference in ("ICLR2026", "ICML2026", "WWW2026"):
        count = sum(
            s.get("conference") == conference and s.get("eligibility") == "primary-writing-evidence"
            for s in index.get("paper_sources", [])
        )
        target = int(targets.get("primary_papers_per_venue", 0))
        if count < target:
            warnings.append(f"readiness gap {conference}: {count}/{target} primary papers")
    if strict and not rules_doc.get("promotion_policy"):
        errors.append("strict mode requires promotion_policy")
    changes = policy_diff(index, previous)
    if changes:
        warnings.append(f"official policy snapshot changed: {len(changes)} source records require semantic review")
    return {
        "valid": not errors,
        "checked": date.today().isoformat(),
        "errors": errors,
        "warnings": warnings,
        "summary": {"sources": len(sources), "rules": len(rules_doc.get("rules", []))},
        "policy_changes": changes,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path)
    parser.add_argument("--rules", required=True, type=Path)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--previous-index", type=Path, help="Compare official source hashes with an earlier index")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    previous = yaml.safe_load(args.previous_index.read_text(encoding="utf-8")) if args.previous_index else None
    result = validate(yaml.safe_load(args.index.read_text(encoding="utf-8")), yaml.safe_load(args.rules.read_text(encoding="utf-8")), args.strict, previous)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"valid: {result['valid']}; sources: {result['summary']['sources']}; rules: {result['summary']['rules']}")
        for level in ("errors", "warnings"):
            for item in result[level]:
                print(f"{level[:-1]}: {item}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
