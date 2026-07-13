#!/usr/bin/env python3
"""Resolve a skill manifest into a deterministic progressive-disclosure route."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
SUPPORTED_VENUES = {"www", "iclr", "icml", "generic"}


def parameter_spec(value: Any) -> tuple[list[str], str | None]:
    if isinstance(value, list):
        return value, None
    return list(value.get("values", [])), value.get("default")


def extend_paths(files: list[str], value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            extend_paths(files, item)
        return
    if value not in files:
        files.append(value)


def infer_needs(skill: str, selected: dict[str, Any], runtime: dict[str, Any]) -> set[str]:
    needs: set[str] = set()
    sections = selected.get("section", [])
    sections = sections if isinstance(sections, list) else [sections]
    if set(sections).intersection({"method", "experiments", "discussion", "limitations", "conclusion"}):
        needs.add("full-section-corpus")
    if skill in {"top-cs-writing", "top-cs-polishing"} and set(sections).intersection({"abstract", "introduction", "related-work", "method", "experiments", "discussion", "limitations", "conclusion"}):
        needs.add("rhetorical-moves")
    if runtime.get("artifact_scope") in {"full-manuscript", "latex-project", "manuscript-supplement", "complete-package"}:
        needs.add("full-paper")
    if skill == "top-cs-polishing" and runtime.get("artifact_scope") == "latex-project":
        needs.add("latex")
    if runtime.get("revision_mode") == "verify-revision" or runtime.get("artifact_scope") == "reviews-diff":
        needs.add("revision-verification")
    if skill == "top-cs-reviewer":
        needs.update({"paper-type-audit", "official-policy"})
    if skill == "top-cs-response" and runtime.get("venue") != "generic":
        needs.add("venue-protocol")
    if runtime.get("citation_verification") == "metadata":
        needs.add("citation-verification")
    if runtime.get("figure_handoff") not in {None, "none"}:
        needs.add("figure-handoff")
    if skill == "top-cs-response":
        needs.add("issue-board")
        if runtime.get("stress_test") == "up-to-3-rounds":
            needs.add("response-stress-test")
    if skill == "top-cs-figure":
        needs.add("figure-contract")
        needs.add("patterns")
        needs.add("visual-style")
        needs.add("palette-policy")
        family = selected.get("visual_family")
        family_values = family if isinstance(family, list) else [family]
        if set(family_values).intersection({"distribution-uncertainty", "tradeoff-frontier", "calibration-reliability", "ranking-critical-difference", "method-schematic", "qualitative-image-plate"}):
            needs.add("archetypes")
        if set(family_values).intersection({"comparison", "trend-scaling", "distribution-uncertainty", "ranking-critical-difference"}):
            needs.add("statistics")
        if "qualitative-image-plate" in family_values:
            needs.add("image-integrity")
        if runtime.get("figure_task") in {"create", "revise", "export-bundle", "layout-mockup"}:
            needs.add("python-workflow")
            needs.add("spec-rendering")
        if runtime.get("figure_task") in {"audit", "export-bundle"} or runtime.get("output_target") == "camera-ready":
            needs.add("visual-qa")
            needs.add("venue-qa")
            needs.add("accessibility")
            needs.add("revision-audit")
            needs.add("provenance")
    return needs


def resolve(skill: str, requested: dict[str, Any], year: int = 2026, needs: list[str] | None = None) -> dict[str, Any]:
    base = SKILLS / skill
    manifest = yaml.safe_load((base / "manifest.yaml").read_text(encoding="utf-8"))
    fallback_reason = None
    venue = requested.get("venue") or "generic"
    if venue not in SUPPORTED_VENUES or (year != 2026 and venue != "generic"):
        fallback_reason = f"unsupported venue/year {venue}/{year}; generic policy selected"
        venue = "generic"
    requested["venue"] = venue
    selected: dict[str, Any] = {}
    files = list(manifest.get("always_load", []))
    missing: list[str] = []
    for name, axis in manifest.get("axes", {}).items():
        value = requested.get(name, axis.get("default"))
        values = axis.get("values", {})
        chosen = value if isinstance(value, list) else [value]
        valid = [item for item in chosen if item in values]
        if not valid and axis.get("default") in values:
            valid = [axis["default"]]
        if not valid:
            missing.append(name)
            continue
        if not axis.get("multi"):
            valid = valid[:1]
        selected[name] = valid if axis.get("multi") else valid[0]
        for item in valid:
            extend_paths(files, values[item])
    runtime = {}
    for name, spec in manifest.get("runtime_parameters", {}).items():
        allowed, default = parameter_spec(spec)
        value = requested.get(name, default)
        if value is None:
            missing.append(name)
        elif allowed and value not in allowed:
            missing.append(name)
        else:
            runtime[name] = value
    if "venue" in manifest.get("runtime_parameters", {}):
        runtime["venue"] = venue
    reference_routes = manifest.get("reference_routes", {})
    requested_needs = set(needs or [])
    inferred_needs = infer_needs(skill, selected, runtime)
    automatic_needs = inferred_needs.intersection(reference_routes)
    unresolved_automatic_needs = sorted(inferred_needs - set(reference_routes))
    active_needs = requested_needs | automatic_needs
    selected_references: list[dict[str, str]] = []
    unknown_needs = sorted(need for need in requested_needs if need not in reference_routes)
    for need in sorted(active_needs):
        for path in reference_routes.get(need, []):
            extend_paths(files, path)
            selected_references.append({"need": need, "path": path})
    policies = yaml.safe_load((SKILLS / "_shared" / "venue-policies.yaml").read_text(encoding="utf-8"))
    profile = policies["venues"].get(venue, policies["venues"]["generic"])
    preparation = yaml.safe_load((ROOT / "data-preparation.yaml").read_text(encoding="utf-8"))
    required_policy_categories = preparation["official_policy"]["required_categories"]
    if venue == "generic":
        missing_policy_categories = list(required_policy_categories)
    else:
        policy_matrix = preparation["official_policy"]["venues"][venue]["categories"]
        missing_policy_categories = [
            category for category in required_policy_categories
            if policy_matrix[category]["status"] != "collected"
        ]
    freshness = {
        "status": "generic-no-policy" if venue == "generic" else "current" if profile.get("year") == year and profile.get("expires_after", year) >= year else "stale-or-unsupported",
        "last_verified": policies.get("last_verified"),
        "year": profile.get("year"),
    }
    resolved_files = []
    for path in files:
        full = (base / path).resolve()
        resolved_files.append(full.relative_to(ROOT).as_posix())
    selected_contracts = [path for path in resolved_files if path.endswith(".schema.yaml")]
    return {
        "skill": skill,
        "manifest_version": manifest.get("version"),
        "route": selected,
        "runtime_parameters": runtime,
        "load_files": resolved_files,
        "requested_needs": sorted(requested_needs),
        "automatic_needs": sorted(automatic_needs),
        "unresolved_automatic_needs": unresolved_automatic_needs,
        "unknown_needs": unknown_needs,
        "selected_references": selected_references,
        "selected_contracts": selected_contracts,
        "capability_status": {
            "citation_verification": runtime.get("citation_verification", "off"),
            "figure_handoff": runtime.get("figure_handoff", "none"),
            "stress_test": runtime.get("stress_test", "off"),
        },
        "on_demand_references": manifest.get("references", {}).get("on_demand", []),
        "missing_parameters": sorted(set(missing)),
        "policy_freshness": freshness,
        "missing_policy_categories": missing_policy_categories,
        "generic_fallback_reason": fallback_reason,
        "resolved_on": date.today().isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", required=True, choices=("top-cs-writing", "top-cs-polishing", "top-cs-reviewer", "top-cs-response", "top-cs-figure"))
    parser.add_argument("--venue", default="generic")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--paper-type")
    parser.add_argument("--section", action="append")
    parser.add_argument("--language")
    parser.add_argument("--visual-family")
    parser.add_argument("--artifact-scope")
    parser.add_argument("--revision-mode")
    parser.add_argument("--evidence-state")
    parser.add_argument("--submission-stage")
    parser.add_argument("--citation-verification", choices=("off", "metadata"))
    parser.add_argument("--figure-handoff")
    parser.add_argument("--figure-task")
    parser.add_argument("--data-state")
    parser.add_argument("--output-target")
    parser.add_argument("--stress-test", choices=("off", "up-to-3-rounds"))
    parser.add_argument("--param", action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--need", action="append", default=[], help="Select a manifest reference route deterministically")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    args = parser.parse_args()
    requested = {
        "venue": args.venue,
        "paper_type": args.paper_type,
        "section": args.section,
        "language": args.language,
        "visual_family": args.visual_family,
        "artifact_scope": args.artifact_scope,
        "revision_mode": args.revision_mode,
        "evidence_state": args.evidence_state,
        "submission_stage": args.submission_stage,
        "citation_verification": args.citation_verification,
        "figure_handoff": args.figure_handoff,
        "figure_task": args.figure_task,
        "data_state": args.data_state,
        "output_target": args.output_target,
        "stress_test": args.stress_test,
    }
    requested = {key: value for key, value in requested.items() if value is not None}
    for item in args.param:
        if "=" not in item:
            parser.error(f"invalid --param: {item}")
        key, value = item.split("=", 1)
        requested[key] = value
    result = resolve(args.skill, requested, args.year, args.need)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"skill: {result['skill']}")
        print(f"route: {json.dumps(result['route'], ensure_ascii=False)}")
        print(f"runtime: {json.dumps(result['runtime_parameters'], ensure_ascii=False)}")
        print("load:")
        for path in result["load_files"]:
            print(f"- {path}")
        if result["missing_parameters"]:
            print(f"missing: {', '.join(result['missing_parameters'])}")
        if result["generic_fallback_reason"]:
            print(f"fallback: {result['generic_fallback_reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
