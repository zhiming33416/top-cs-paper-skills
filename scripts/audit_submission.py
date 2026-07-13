#!/usr/bin/env python3
"""Audit a LaTeX/Markdown submission against source-anchored venue policies."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICIES = ROOT / "skills" / "_shared" / "venue-policies.yaml"


def finding(code: str, level: str, message: str, evidence: str | None = None) -> dict[str, str]:
    item = {"code": code, "level": level, "message": message}
    if evidence:
        item["evidence"] = evidence
    return item


def estimate_pdf_pages(path: Path) -> dict[str, Any]:
    reader = PdfReader(str(path))
    ref_page = None
    estimated_main_pages = None
    appendix_page = None
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        ref_match = re.search(r"(?im)^\s*(?:\d+\s+)?references\s*$", text)
        if ref_page is None and ref_match:
            ref_page = index
            relative_position = ref_match.start() / max(len(text), 1)
            estimated_main_pages = index - 1 if relative_position < 0.2 else index
        if appendix_page is None and re.search(r"(?im)^\s*(?:appendix|[a-z]\s+additional\b)", text):
            appendix_page = index
    metadata = reader.metadata or {}
    return {
        "total_pages": len(reader.pages),
        "estimated_main_pages": estimated_main_pages or len(reader.pages),
        "references_start_page": ref_page,
        "appendix_start_page": appendix_page,
        "metadata_author": str(metadata.get("/Author", "")).strip() or None,
        "note": "Main-page count is estimated from the first References heading and its position; visually verify the final PDF.",
    }


def audit(source: Path | None, venue: str, year: int, policies_path: Path, pdf: Path | None = None) -> dict[str, Any]:
    policies = yaml.safe_load(policies_path.read_text(encoding="utf-8"))
    policy = policies["venues"][venue]
    if source:
        text = source.read_text(encoding="utf-8", errors="replace")
    elif pdf:
        reader = PdfReader(str(pdf))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        raise ValueError("source or PDF is required")
    lower = text.lower()
    results: list[dict[str, str]] = []

    if venue != "generic" and policy.get("year") != year:
        results.append(finding("unsupported-year", "error", f"No verified {venue.upper()} policy for {year}; use generic and verify the official guide."))

    section_patterns = {
        "abstract": r"\\begin\{abstract\}|^\s*#+\s+abstract\b|^\s*abstract\s*$",
        "introduction": r"\\section\*?\{introduction\}|^\s*#+\s+introduction\b|^\s*\d+(?:\.\d+)*\.?\s+introduction\s*$|^\s*introduction\s*$",
        "references": r"\\bibliography\{|\\printbibliography|^\s*#+\s+references\b|^\s*\d+(?:\.\d+)*\.?\s+references\s*$|^\s*references\s*$",
    }
    for section, pattern in section_patterns.items():
        if not re.search(pattern, text, re.IGNORECASE | re.MULTILINE):
            results.append(finding(f"missing-{section}", "warning", f"Could not detect a {section} section in the source."))

    identity_patterns = {
        "email": r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}",
        "acknowledgement": r"\\section\*?\{acknowledg(?:e)?ments?\}|\backnowledg(?:e)?ments?\b",
        "grant": r"\b(?:grant|award)\s*(?:no\.?|number|#)?\s*[A-Z0-9][A-Z0-9-]{3,}\b",
        "named-github": r"https?://github\.com/(?!anonymous|anon(?:ymous)?)[^\s}/]+/",
    }
    if policy.get("double_blind"):
        for label, pattern in identity_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                results.append(finding(f"anonymity-{label}", "error", f"Possible anonymity leak: {label}.", match.group(0)[:120]))

    ref_position = max(lower.find("\\bibliography"), lower.find("\\printbibliography"), lower.find("# references"))
    appendix_positions = [pos for pos in (lower.find("\\appendix"), lower.find("# appendix")) if pos >= 0]
    if appendix_positions and ref_position >= 0 and min(appendix_positions) < ref_position:
        results.append(finding("appendix-before-references", "warning", "Appendix appears before references; verify venue ordering."))

    if venue == "www":
        first_page_proxy = lower[:12000]
        if "www companion" in first_page_proxy or "companion proceedings of the acm web conference" in first_page_proxy:
            results.append(finding("www-companion-mismatch", "error", "The document identifies itself as WWW Companion, not the WWW research track."))
        web_terms = re.findall(r"\b(web|online platform|web-scale|website|browser|internet|social media)\b", first_page_proxy)
        if len(web_terms) < 2:
            results.append(finding("www-first-page-relevance", "error", "WWW requires explicit Web and track relevance on the first page; the source proxy has weak evidence."))
    if venue == "iclr" and "reproducibility statement" not in lower:
        results.append(finding("iclr-reproducibility", "info", "ICLR strongly encourages a paragraph-length Reproducibility Statement before references."))

    pdf_info = None
    if pdf:
        pdf_info = estimate_pdf_pages(pdf)
        if policy.get("main_pages") and pdf_info["estimated_main_pages"] > policy["main_pages"]:
            results.append(finding("main-page-limit", "error", f"Estimated main body is {pdf_info['estimated_main_pages']} pages; policy limit is {policy['main_pages']}."))
        if policy.get("total_pages") and pdf_info["total_pages"] > policy["total_pages"]:
            results.append(finding("total-page-limit", "error", f"PDF has {pdf_info['total_pages']} pages; policy total limit is {policy['total_pages']}."))
        if policy.get("pdf_size_mb") and pdf.stat().st_size > policy["pdf_size_mb"] * 1024 * 1024:
            results.append(finding("pdf-size", "error", f"PDF exceeds {policy['pdf_size_mb']} MB."))
        if policy.get("double_blind") and pdf_info.get("metadata_author"):
            results.append(finding("pdf-metadata-author", "error", "PDF metadata contains an Author field.", pdf_info["metadata_author"][:120]))

    counts = {level: sum(1 for item in results if item["level"] == level) for level in ("error", "warning", "info")}
    return {
        "venue": venue,
        "year": year,
        "policy_source": policy.get("source"),
        "source": str(source) if source else None,
        "pdf": str(pdf) if pdf else None,
        "summary": counts,
        "pdf_analysis": pdf_info,
        "findings": results,
        "disclaimer": policy.get("warning") or "Automated checks are conservative; verify the rendered paper and current official policy.",
    }


def as_markdown(report: dict[str, Any]) -> str:
    lines = [
        f"# Submission audit: {report['venue'].upper()} {report['year']}",
        "",
        f"Policy: {report['policy_source'] or 'generic fallback'}",
        f"Summary: {report['summary']['error']} errors, {report['summary']['warning']} warnings, {report['summary']['info']} info",
        "",
    ]
    if not report["findings"]:
        lines.append("No automated findings. This is not a guarantee of compliance.")
    for item in report["findings"]:
        evidence = f" — `{item['evidence']}`" if item.get("evidence") else ""
        lines.append(f"- **{item['level'].upper()} [{item['code']}]** {item['message']}{evidence}")
    lines.extend(["", f"> {report['disclaimer']}"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--venue", choices=("www", "iclr", "icml", "generic"), required=True)
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--source", type=Path, help="LaTeX, Markdown, or text source")
    parser.add_argument("--pdf", type=Path)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--policies", type=Path, default=DEFAULT_POLICIES)
    args = parser.parse_args()
    if not args.source and not args.pdf:
        parser.error("provide --source, --pdf, or both")
    if args.source and not args.source.is_file():
        parser.error(f"source file does not exist: {args.source}")
    if args.pdf and not args.pdf.is_file():
        parser.error(f"PDF file does not exist: {args.pdf}")
    report = audit(args.source, args.venue, args.year, args.policies, args.pdf)
    print(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else as_markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
