#!/usr/bin/env python3
"""Evaluate a skill output against an executable acceptance-case contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
import re

import yaml


def load_case(path: Path, case_id: str | None) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "cases" not in data:
        return data
    if not case_id:
        raise ValueError("--case-id is required for a multi-case file")
    for case in data["cases"]:
        if case.get("id") == case_id:
            return case
    raise ValueError(f"case not found: {case_id}")


def markdown_headings(text: str) -> set[str]:
    return {re.sub(r"\s+", " ", match).strip().lower() for match in re.findall(r"(?m)^#{1,6}\s+(.+?)\s*$", text)}


def source_tokens(text: str, kind: str) -> set[str]:
    if kind == "numbers":
        return set(re.findall(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:%|\b)", text))
    if kind == "citations":
        groups = re.findall(r"\\cite\w*\{([^}]+)\}", text)
        return {key.strip() for group in groups for key in group.split(",") if key.strip()}
    if kind == "labels":
        return set(re.findall(r"\\(?:label|ref|eqref|autoref)\{([^}]+)\}", text))
    raise ValueError(f"unsupported preservation token kind: {kind}")


def evaluate(case: dict[str, Any], output: str, source: str | None = None) -> dict[str, Any]:
    lower = output.lower()
    required = []
    forbidden = []
    for value in case.get("must_include", []):
        required.append({"text": value, "present": value.lower() in lower})
    for value in case.get("must_not_include", []):
        forbidden.append({"text": value, "present": value.lower() in lower})
    required_placeholders = case.get("required_placeholders", [])
    placeholders = [{"text": value, "present": value in output} for value in required_placeholders]
    failures = [f"missing required text: {x['text']}" for x in required if not x["present"]]
    failures += [f"forbidden text present: {x['text']}" for x in forbidden if x["present"]]
    failures += [f"missing placeholder: {x['text']}" for x in placeholders if not x["present"]]
    contract = case.get("semantic_contract", {})
    semantic_checks: list[dict[str, Any]] = []
    headings = markdown_headings(output)
    for heading in contract.get("required_sections", []):
        present = heading.lower() in headings
        semantic_checks.append({"type": "required-section", "value": heading, "passed": present})
        if not present:
            failures.append(f"missing required section heading: {heading}")
    for invariant in contract.get("fact_invariants", []):
        present = invariant in output
        semantic_checks.append({"type": "fact-invariant", "value": invariant, "passed": present})
        if not present:
            failures.append(f"fact invariant missing or changed: {invariant}")
    for pattern in contract.get("forbidden_claim_patterns", []):
        present = bool(re.search(pattern, output, flags=re.IGNORECASE | re.MULTILINE))
        semantic_checks.append({"type": "forbidden-claim-pattern", "value": pattern, "passed": not present})
        if present:
            failures.append(f"forbidden claim pattern present: {pattern}")
    for claim_id, status in contract.get("required_claim_statuses", {}).items():
        present = bool(re.search(rf"(?im)^.*\b{re.escape(claim_id)}\b.*\b{re.escape(status)}\b.*$", output))
        semantic_checks.append({"type": "claim-status", "value": f"{claim_id}={status}", "passed": present})
        if not present:
            failures.append(f"required claim status missing: {claim_id}={status}")
    for columns in contract.get("required_table_columns", []):
        present = any(all(column.lower() in line.lower() for column in columns) for line in output.splitlines() if "|" in line)
        semantic_checks.append({"type": "table-columns", "value": columns, "passed": present})
        if not present:
            failures.append(f"required table columns missing: {', '.join(columns)}")
    for kind in contract.get("preserve_from_source", []):
        if source is None:
            failures.append(f"source required for preservation check: {kind}")
            semantic_checks.append({"type": f"preserve-{kind}", "passed": False, "missing_source": True})
            continue
        expected = source_tokens(source, kind)
        actual = source_tokens(output, kind)
        missing_tokens = sorted(expected - actual)
        semantic_checks.append({"type": f"preserve-{kind}", "passed": not missing_tokens, "missing": missing_tokens})
        if missing_tokens:
            failures.append(f"source {kind} missing or changed: {', '.join(missing_tokens)}")
    for record_type, fields in contract.get("required_record_fields", {}).items():
        missing_fields = [field for field in fields if not re.search(rf"(?i)(?:\b|[`|\"']){re.escape(field)}(?:\b|[`|\"'])", output)]
        passed = not missing_fields
        semantic_checks.append({"type": f"{record_type}-record-fields", "passed": passed, "missing": missing_fields})
        if missing_fields:
            failures.append(f"{record_type} record fields missing: {', '.join(missing_fields)}")
    for transition in contract.get("forbidden_status_transitions", []):
        before, after = transition
        pattern = rf"(?i)\b{re.escape(before)}\b\s*(?:->|→|to)\s*\b{re.escape(after)}\b"
        present = bool(re.search(pattern, output))
        semantic_checks.append({"type": "forbidden-status-transition", "value": transition, "passed": not present})
        if present:
            failures.append(f"forbidden status transition present: {before} -> {after}")
    max_round = contract.get("max_round")
    if max_round is not None:
        rounds = [int(value) for value in re.findall(r"(?i)\bround\s*[:#-]?\s*(\d+)\b", output)]
        passed = not rounds or max(rounds) <= int(max_round)
        semantic_checks.append({"type": "max-round", "value": max_round, "passed": passed, "observed": rounds})
        if not passed:
            failures.append(f"stress-test round exceeds {max_round}")
    if contract.get("forbid_metadata_as_claim_support"):
        pattern = r"(?is)metadata[- ]verified.{0,120}(?:therefore\b|thus\b|proves?\b|entails?\b|claim[- ]verified\b|supports?\s+the\s+(?:manuscript\s+)?claim\b)"
        present = bool(re.search(pattern, output))
        semantic_checks.append({"type": "citation-boundary", "passed": not present})
        if present:
            failures.append("bibliographic metadata is presented as claim support")
    manual = {
        name: {"score": None, "scale": "1-5", "status": "manual-review-required"}
        for name in case.get("manual_rubric", ["fact_fidelity", "argument_structure", "venue_fit", "usability"])
    }
    return {
        "case_id": case.get("id"),
        "skill": case.get("skill"),
        "passed_automatic_checks": not failures,
        "failures": failures,
        "required": required,
        "forbidden": forbidden,
        "placeholders": placeholders,
        "semantic_checks": semantic_checks,
        "manual_rubric": manual,
    }


def markdown(result: dict[str, Any]) -> str:
    lines = [f"# Evaluation: {result.get('case_id')}", "", f"Automatic checks: **{'PASS' if result['passed_automatic_checks'] else 'FAIL'}**"]
    if result["failures"]:
        lines += ["", "## Failures"] + [f"- {item}" for item in result["failures"]]
    if result["semantic_checks"]:
        lines += ["", "## Structured semantic checks"]
        lines += [f"- {'PASS' if item['passed'] else 'FAIL'}: {item['type']}" for item in result["semantic_checks"]]
    lines += ["", "## Manual rubric"] + [f"- {name}: manual review required (1-5)" for name in result["manual_rubric"]]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", required=True, type=Path)
    parser.add_argument("--case-id")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--source", type=Path, help="Optional source passage for number/citation/label preservation checks")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    try:
        case = load_case(args.case, args.case_id)
    except ValueError as exc:
        parser.error(str(exc))
    source_path = args.source
    if source_path is None and case.get("source_file"):
        source_path = (args.case.parent / case["source_file"]).resolve()
    source = source_path.read_text(encoding="utf-8") if source_path else None
    result = evaluate(case, args.output.read_text(encoding="utf-8"), source)
    print(json.dumps(result, ensure_ascii=False, indent=2) if args.format == "json" else markdown(result))
    return 0 if result["passed_automatic_checks"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
