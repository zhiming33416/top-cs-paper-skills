#!/usr/bin/env python3
"""Build a source-aware YAML inventory for a directory of research PDFs."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader


HEADING_RE = re.compile(
    r"^(?:\d+(?:\.\d+)*\s+)?(abstract|introduction|related work|background|"
    r"preliminaries|method(?:ology)?|approach|experiments?|results?|discussion|"
    r"limitations?|ethics|impact statement|conclusion|references|appendix)\b",
    re.IGNORECASE,
)


def normalize(text: str) -> str:
    return " ".join(text.split())


def classify(text: str) -> dict[str, str]:
    """Classify venue/status conservatively from explicit PDF markers."""
    lower = text.lower()
    if "www companion" in lower or "companion proceedings of the acm web conference" in lower:
        return {"venue": "www", "track": "companion", "status": "verified-companion", "use": "comparison-only"}
    if "published as a conference paper at iclr 2026" in lower:
        return {"venue": "iclr", "track": "conference", "status": "verified-main", "use": "style-evidence"}
    if re.search(r"proceedings of the 43\s*(?:rd)?\s*international conference on machine", lower):
        return {"venue": "icml", "track": "main", "status": "verified-main", "use": "style-evidence"}
    if "conference on empirical methods in natural language processing" in lower:
        return {"venue": "emnlp", "track": "unknown", "status": "verified-other-venue", "use": "comparison-only"}
    if "proceedings of the acm web conference 2026" in lower:
        return {"venue": "www", "track": "main-or-other", "status": "needs-track-verification", "use": "holdout"}
    if "preprint" in lower or re.search(r"arxiv:\s*\d{4}\.\d+", lower):
        return {"venue": "unknown", "track": "preprint", "status": "preprint", "use": "comparison-only"}
    return {"venue": "unknown", "track": "unknown", "status": "needs-verification", "use": "holdout"}


def inspect_pdf(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    first_pages = [(page.extract_text() or "") for page in reader.pages[:3]]
    first_text = "\n".join(first_pages)
    metadata = reader.metadata or {}
    headings: list[str] = []
    for page in reader.pages:
        for raw in (page.extract_text() or "").splitlines():
            line = normalize(raw)
            match = HEADING_RE.match(line)
            if match:
                heading = match.group(1).lower()
                if heading not in headings:
                    headings.append(heading)
    item: dict[str, Any] = {
        "file": path.name,
        "title": normalize(str(metadata.get("/Title", ""))) or None,
        "pages": len(reader.pages),
        "headings": headings,
    }
    item.update(classify(first_text))
    return item


def build_manifest(input_dir: Path) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for path in sorted(input_dir.rglob("*.pdf"), key=lambda p: p.name.lower()):
        try:
            sources.append(inspect_pdf(path))
        except Exception as exc:  # retain failures in the inventory
            sources.append({
                "file": path.name,
                "venue": "unknown",
                "status": "read-error",
                "use": "holdout",
                "error": str(exc),
            })
    counts: dict[str, int] = {}
    for source in sources:
        key = f"{source.get('venue', 'unknown')}:{source.get('status', 'unknown')}"
        counts[key] = counts.get(key, 0) + 1
    return {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "policy": {
            "official_policy_only_for_hard_constraints": True,
            "verified_main_only_for_style_evidence": True,
            "companion_preprint_unverified_use": "comparison-only-or-holdout",
        },
        "summary": {"total": len(sources), "counts": counts},
        "sources": sources,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Directory containing PDFs")
    parser.add_argument("--output", required=True, type=Path, help="YAML file to write")
    args = parser.parse_args()
    if not args.input.is_dir():
        parser.error(f"input directory does not exist: {args.input}")
    manifest = build_manifest(args.input.resolve())
    if args.output.is_file():
        existing = yaml.safe_load(args.output.read_text(encoding="utf-8")) or {}
        if "external_verified_main_sources" in existing:
            manifest["external_verified_main_sources"] = existing["external_verified_main_sources"]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(f"Wrote {manifest['summary']['total']} sources to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
