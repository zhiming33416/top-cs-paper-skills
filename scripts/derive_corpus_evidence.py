#!/usr/bin/env python3
"""Derive portable schema-v2 evidence from a read-only conference corpus.

Only hashes, source metadata, structural features, and aggregate review statistics
are emitted. Paper and review text is never copied to the output directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import statistics
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

import yaml
from pypdf import PdfReader


CONFERENCES = ("ICLR2026", "ICML2026", "WWW2026")
TRACK_PRIORITY = {"Oral": 0, "Spotlight": 1, "Regular": 2, "Poster": 3, "Research": 4,
                  "Industry": 5, "Short": 6, "Web4Good": 7}
HEADINGS = {
    "abstract": ("abstract",),
    "introduction": ("introduction",),
    "related-work": ("related work", "related works"),
    "background": ("background", "preliminaries", "preliminary"),
    "method": ("method", "methods", "methodology", "approach", "proposed method", "our approach", "problem formulation", "model and method", "implementation details"),
    "experiments": ("experiment", "experiments", "experimental setup", "evaluation", "experimental evaluation", "experiments and results", "evaluation and analysis"),
    "results": ("result", "results", "results and discussion", "experimental results"),
    "discussion": ("discussion", "discussion and analysis", "discussion and implications"),
    "limitations": ("limitation", "limitations", "limitations and future work", "discussion and limitations"),
    "impact-statement": ("impact statement", "broader impact"),
    "conclusion": ("conclusion", "conclusions", "concluding remarks", "conclusion and future work"),
    "references": ("references", "bibliography"),
    "appendix": ("appendix", "appendices"),
}
TOPIC_PATTERNS = {
    "llm-agent": r"\b(llm|large language model|agentic|multi-agent|agent)\b",
    "recommendation-search": r"\b(recommend|retrieval|search|ranking|clickbait)\b",
    "vision-multimodal": r"\b(vision|visual|multimodal|image)\b",
    "theory-optimization": r"\b(theor|bound|optimization|game-theoretic|attribution)\b",
    "systems-efficiency": r"\b(system|framework|platform|efficient|scaling|runtime)\b",
    "dataset-benchmark": r"\b(dataset|benchmark|evaluation protocol|corpus)\b",
    "security-safety": r"\b(security|safety|red team|denial-of-service|reliable)\b",
}
PAPER_TYPE_PATTERNS = (
    ("dataset-benchmark", r"\b(dataset|benchmark|corpus|evaluation protocol)\b"),
    ("theoretical", r"\b(theorem|theoretical|bound|convergence|complexity)\b"),
    ("systems", r"\b(system|platform|framework|deployment|runtime|infrastructure)\b"),
    ("algorithmic", r"\b(algorithm|optimization|decoding|search|planning)\b"),
    ("empirical", r"\b(empirical|evaluation|study|analysis|experiment)\b"),
)


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (value or "").lower()).strip()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def filename_parts(path: Path) -> tuple[str, str]:
    stem = path.stem
    if " - " not in stem:
        return "Unknown", stem
    return tuple(stem.split(" - ", 1))  # type: ignore[return-value]


def load_existing_manifest(corpus_root: Path) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    by_sha: dict[str, dict[str, str]] = {}
    by_title: dict[str, dict[str, str]] = {}
    path = corpus_root / "papers" / "verified_fulltext_manifest.csv"
    if path.is_file():
        with path.open(encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                if row.get("sha256"):
                    by_sha[row["sha256"]] = row
                if row.get("title"):
                    by_title[normalized(row["title"])] = row
    for conference in CONFERENCES:
        catalog = corpus_root / "papers" / conference / "catalog.csv"
        if catalog.is_file():
            with catalog.open(encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    title = normalized(row.get("title", ""))
                    if title and title not in by_title:
                        by_title[title] = row
    return by_sha, by_title


def load_primary_labels(corpus_root: Path) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    path = corpus_root / "papers" / "primary_labels.yaml"
    if not path.is_file():
        return {}, {}
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    rows = document.get("papers", [])
    return (
        {row["sha256"]: row for row in rows if row.get("sha256")},
        {normalized(row["title"]): row for row in rows if row.get("title")},
    )


def normalize_heading_line(value: str) -> str:
    line = " ".join(value.split()).lower()
    line = re.sub(r"^\s*(?:section\s+)?(?:\d+(?:\.\d+)*\.?|[a-z]\.)?\s*", "", line)
    line = re.sub(r"\s*[.:–—-]+\s*$", "", line)
    return line.strip()


def canonical_heading(value: str) -> str | None:
    normalized_line = normalize_heading_line(value)
    for canonical, aliases in HEADINGS.items():
        if normalized_line in {normalize_heading_line(alias) for alias in aliases}:
            return canonical
    return None


def heading_events(text: str) -> list[tuple[str, int]]:
    events: list[tuple[str, int]] = []
    offset = 0
    seen: set[str] = set()
    for raw in text.splitlines(keepends=True):
        canonical = canonical_heading(raw)
        if canonical and canonical not in seen:
            events.append((canonical, offset))
            seen.add(canonical)
        offset += len(raw)
    return events


def abstract_word_count(text: str) -> int | None:
    match = re.search(r"(?is)\babstract\b\s*(.*?)(?:\n\s*(?:1\.?\s+)?introduction\b)", text[:30000])
    if not match:
        return None
    words = re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", match.group(1))
    return len(words) if 20 <= len(words) <= 1000 else None


def page_for_pattern(page_texts: list[str], pattern: str) -> int | None:
    for number, text in enumerate(page_texts, 1):
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            return number
    return None


def topic_candidates(title: str) -> list[str]:
    return [name for name, pattern in TOPIC_PATTERNS.items() if re.search(pattern, title, re.IGNORECASE)] or ["other-unclassified"]


def paper_type_candidate(title: str) -> str:
    for name, pattern in PAPER_TYPE_PATTERNS:
        if re.search(pattern, title, re.IGNORECASE):
            return name
    return "unclassified"


def outline_titles(reader: PdfReader) -> list[str]:
    titles: list[str] = []

    def visit(items: Any) -> None:
        if isinstance(items, list):
            for item in items:
                visit(item)
            return
        title = getattr(items, "title", None)
        if title:
            titles.append(str(title))

    try:
        visit(reader.outline)
    except Exception:
        return []
    return titles


def structural_features(text: str, page_texts: list[str], bookmarks: list[str] | None = None) -> dict[str, Any]:
    events = heading_events(text)
    bookmark_sections = [section for title in (bookmarks or []) if (section := canonical_heading(title))]
    text_sections = [name for name, _ in events]
    combined_sections = text_sections + [name for name in bookmark_sections if name not in text_sections]
    positions = dict(events)
    refs = positions.get("references")
    appendix = positions.get("appendix")
    limitations = positions.get("limitations")
    figures = {int(x) for x in re.findall(r"(?im)^\s*(?:figure|fig\.)\s*(\d+)\b", text)}
    tables = {int(x) for x in re.findall(r"(?im)^\s*table\s*(\d+)\b", text)}
    return {
        "section_order": combined_sections,
        "section_detection": {
            section: {
                "detected": section in combined_sections,
                "evidence": "text-heading" if section in text_sections else "pdf-outline" if section in bookmark_sections else "none",
                "confidence": "high" if section in text_sections else "medium" if section in bookmark_sections else "none",
            }
            for section in HEADINGS
        },
        "heading_detection_confidence": (
            "high" if {"introduction", "references"}.issubset(text_sections)
            else "medium" if len(combined_sections) >= 4
            else "low"
        ),
        "main_text_boundary": {
            "references_start_page": page_for_pattern(page_texts, r"^\s*(?:references|bibliography)\s*$"),
            "appendix_detected": appendix is not None,
            "appendix_start_page": page_for_pattern(page_texts, r"^\s*(?:appendix|appendices)\s*$"),
        },
        "figure_count_detected": len(figures),
        "table_count_detected": len(tables),
        "research_question_markers": len(set(re.findall(r"\bRQ\s*[-:]?\s*(\d+)\b", text, re.IGNORECASE))),
        "explicit_contribution_statement": bool(re.search(r"(?i)\b(our|the)\s+(main\s+)?contributions?\s+(are|include|can be summarized)\b", text)),
        "limitations_position": (
            "before-references" if limitations is not None and (refs is None or limitations < refs)
            else "after-references" if limitations is not None
            else "detected-position-unknown" if "limitations" in bookmark_sections
            else "not-detected"
        ),
    }


def official_sources(corpus_root: Path, verified: str) -> list[dict[str, Any]]:
    specs = [
        ("official-iclr2026-author", "ICLR2026", ["author", "response", "anonymity", "supplement", "artifact-reproducibility"], "sources/ICLR2026/guides/author-guide.html", "https://iclr.cc/Conferences/2026/AuthorGuide"),
        ("official-iclr2026-reviewer", "ICLR2026", ["reviewer", "review-form", "ethics-llm", "artifact-reproducibility"], "sources/ICLR2026/guides/reviewer-guide.html", "https://iclr.cc/Conferences/2026/ReviewerGuide"),
        ("official-iclr2026-template", "ICLR2026", ["template"], "sources/ICLR2026/template/iclr2026.zip", "https://iclr.cc/Conferences/2026/AuthorGuide"),
        ("official-icml2026-author", "ICML2026", ["author", "anonymity", "supplement", "artifact-reproducibility", "camera-ready"], "sources/ICML2026/guides/author-instructions.html", "https://icml.cc/Conferences/2026/AuthorInstructions"),
        ("official-icml2026-reviewer", "ICML2026", ["reviewer", "review-form", "post-response", "ethics-llm"], "sources/ICML2026/guides/reviewer-instructions.html", "https://icml.cc/Conferences/2026/ReviewerInstructions"),
        ("official-icml2026-response", "ICML2026", ["response", "discussion"], "sources/ICML2026/guides/rebuttal-discussion-faq.html", "https://icml.cc/Conferences/2026/PeerReviewFAQ"),
        ("official-icml2026-ethics", "ICML2026", ["ethics-llm"], "sources/ICML2026/guides/research-ethics.html", "https://icml.cc/Conferences/2026/ResearchEthics"),
        ("official-icml2026-peer-review-ethics", "ICML2026", ["reviewer", "ethics-llm"], "sources/ICML2026/guides/peer-review-ethics.html", "https://icml.cc/Conferences/2026/PeerReviewEthics"),
        ("official-icml2026-llm-reviewing", "ICML2026", ["reviewer", "ethics-llm"], "sources/ICML2026/guides/llm-reviewing-policy.html", "https://icml.cc/Conferences/2026/LLM-Policy"),
        ("official-icml2026-template", "ICML2026", ["template"], "sources/ICML2026/template/icml2026.zip", "https://icml.cc/Conferences/2026/AuthorInstructions"),
        ("official-icml2026-example-pdf", "ICML2026", ["template"], "sources/ICML2026/template/example_paper.pdf", "https://media.icml.cc/Conferences/ICML2026/Styles/example_paper.pdf"),
        ("official-icml2026-paper-checker", "ICML2026", ["template"], "sources/ICML2026/guides/paper-checker.html", "https://papercheck.icml.cc/papercheck.html"),
        ("official-www2026-research", "WWW2026", ["author", "response", "anonymity", "supplement", "ethics-llm", "artifact-reproducibility", "camera-ready"], "sources/WWW2026/guides/research-author-rebuttal-guide.html", "https://www2026.thewebconf.org/calls/research-tracks.html"),
        ("official-www2026-template", "WWW2026", ["template"], "sources/WWW2026/template/acmart.zip", "https://www2026.thewebconf.org/calls/research-tracks.html"),
        ("official-www2026-reviewer", "WWW2026", ["reviewer", "review-form"], "sources/WWW2026/guides/reviewer-guide.html", None),
    ]
    result = []
    for source_id, conference, categories, relative, url in specs:
        path = corpus_root / relative
        available = path.is_file()
        result.append({
            "source_id": source_id,
            "conference": conference,
            "source_type": "official-policy",
            "categories": categories,
            "relative_path": relative,
            "url": url,
            "sha256": sha256(path) if available else None,
            "availability": "collected" if available else "not-public-or-not-collected",
            "verification_status": "hash-verified-local-copy" if available else "explicit-gap",
            "last_verified": verified,
            "valid_for_year": 2026,
            "expires_after_year": 2026,
        })
    return result


def scan_papers(corpus_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_sha, by_title = load_existing_manifest(corpus_root)
    labels_by_sha, labels_by_title = load_primary_labels(corpus_root)
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for conference in CONFERENCES:
        folder = corpus_root / "papers" / conference / "verified_fulltext"
        for path in sorted(folder.glob("*.pdf")):
            track, filename_title = filename_parts(path)
            digest = sha256(path)
            manifest = by_sha.get(digest) or by_title.get(normalized(filename_title), {})
            reader = PdfReader(str(path))
            page_texts = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(page_texts)
            metadata = reader.metadata or {}
            title = manifest.get("title") or str(metadata.get("/Title", "")) or filename_title
            record = {
                "conference": conference,
                "track": track,
                "title": title,
                "relative_path": path.relative_to(corpus_root).as_posix(),
                "sha256": digest,
                "bytes": path.stat().st_size,
                "pages": len(reader.pages),
                "abstract_words": abstract_word_count(text),
                "structure": structural_features(text, page_texts, outline_titles(reader)),
                "conference_source": manifest.get("conference_source") or manifest.get("paper_url") or "",
                "public_fulltext_source": manifest.get("public_fulltext_source") or manifest.get("pdf_source") or manifest.get("pdf_url") or "",
            }
            groups[digest].append(record)

    sources: list[dict[str, Any]] = []
    duplicates: list[dict[str, Any]] = []
    for digest, records in groups.items():
        records.sort(key=lambda item: TRACK_PRIORITY.get(item["track"], 99))
        canonical = records[0]
        labels = labels_by_sha.get(digest) or labels_by_title.get(normalized(canonical["title"]), {})
        conference = canonical["conference"]
        source_id = f"{conference.lower()}-{digest[:12]}"
        tracks = sorted({record["track"] for record in records}, key=lambda x: TRACK_PRIORITY.get(x, 99))
        primary = conference in {"ICLR2026", "ICML2026"} or (conference == "WWW2026" and "Research" in tracks)
        has_accepted_source = bool(canonical["conference_source"])
        source = {
            "source_id": source_id,
            "conference": conference,
            "tracks": tracks,
            "title": canonical["title"],
            "relative_path": canonical["relative_path"],
            "sha256": digest,
            "bytes": canonical["bytes"],
            "pages": canonical["pages"],
            "abstract_words": canonical["abstract_words"],
            "structure": canonical["structure"],
            "paper_type": labels.get("paper_type", "unverified"),
            "paper_type_candidate": labels.get("paper_type", paper_type_candidate(canonical["title"])),
            "research_area": labels.get("topic", "unverified"),
            "topic_tags_candidate": [labels["topic"]] if labels.get("topic") else topic_candidates(canonical["title"]),
            "label_status": labels.get("label_status", "heuristic-candidates-require-human-review"),
            "source_type": "accepted-title-verified-public-version",
            "document_version": "public-preprint-or-author-version",
            "version_status": "not-guaranteed-camera-ready",
            "official_format_evidence": False,
            "eligibility": "primary-writing-evidence" if primary else "indexed-nonresearch",
            "verification_status": "accepted-title-source-present" if has_accepted_source else "accepted-title-needs-manual-check",
            "exclusion_reason": None if primary else "WWW non-Research track excluded from Research style evidence",
            "artifact_pairs": {
                "submission": False,
                "revision": False,
                "rebuttal": False,
                "camera_ready": False,
                "pairing_verified": False,
            },
            "conference_source": labels.get("conference_source") or canonical["conference_source"],
            "public_fulltext_source": labels.get("public_fulltext_source") or canonical["public_fulltext_source"],
        }
        sources.append(source)
        if len(records) > 1:
            duplicates.append({
                "sha256": digest,
                "canonical_source_id": source_id,
                "occurrences": [{"track": r["track"], "relative_path": r["relative_path"]} for r in records],
            })
    sources.sort(key=lambda item: (item["conference"], item["tracks"], item["title"].lower()))
    return sources, duplicates


def structure_stats(sources: list[dict[str, Any]], duplicates: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": 2,
        "unique_sources": len(sources),
        "duplicate_groups": duplicates,
        "primary_writing_evidence": sum(s["eligibility"] == "primary-writing-evidence" for s in sources),
        "conferences": {},
    }
    for conference in CONFERENCES:
        rows = [s for s in sources if s["conference"] == conference]
        primary = [s for s in rows if s["eligibility"] == "primary-writing-evidence"]
        pages = [s["pages"] for s in rows]
        abstracts = [s["abstract_words"] for s in rows if s["abstract_words"] is not None]
        heading_counts = Counter(h for s in primary for h in s["structure"]["section_order"])
        topics = Counter(t for s in primary for t in s["topic_tags_candidate"])
        result["conferences"][conference] = {
            "unique_sources": len(rows),
            "primary_sources": len(primary),
            "target_primary_sources": 30,
            "readiness_gap": max(0, 30 - len(primary)),
            "track_counts": dict(Counter(track for s in rows for track in s["tracks"])),
            "page_median": statistics.median(pages) if pages else None,
            "abstract_word_median": statistics.median(abstracts) if abstracts else None,
            "heading_presence_in_primary": dict(sorted(heading_counts.items())),
            "paper_type_candidates": dict(sorted(Counter(s["paper_type_candidate"] for s in primary).items())),
            "topic_tag_candidates": dict(sorted(topics.items())),
            "human_labels_complete": all(s["label_status"] == "human-verified" for s in primary),
        }
    return result


def full_section_rules(sources: list[dict[str, Any]], generated: str) -> dict[str, Any]:
    primary = [source for source in sources if source["eligibility"] == "primary-writing-evidence"]
    specifications = {
        "method": {
            "statement": "Method headings vary substantially; require the problem setting, assumptions, mechanism, objective or procedure, and computational implications without forcing a universal heading.",
            "boundary": "Heading detection supports placement flexibility only; content requirements come from claim and reproducibility discipline.",
        },
        "experiments": {
            "statement": "Experimental or evaluation sections are prevalent but not universal; organize empirical evidence by research question, comparator, metric, result, interpretation, and boundary when the paper makes empirical claims.",
            "boundary": "Do not impose an experiments section on a purely theoretical contribution; audit the selected paper type first.",
        },
        "discussion": {
            "statement": "Dedicated discussion headings are uncommon, so interpretation may be integrated with results; still separate observation, explanation, implication, and uncertainty in the argument.",
            "boundary": "Low heading frequency does not justify omitting discussion of mechanisms, negative evidence, or scope.",
        },
        "limitations": {
            "statement": "Dedicated limitations headings are uncommon in the public-version corpus; make concrete claim boundaries explicit wherever the venue and argument require them, regardless of heading choice.",
            "boundary": "Public-version heading frequency is not evidence that limitations are optional or that a venue omits ethics requirements.",
        },
        "conclusion": {
            "statement": "Conclusion sections are common but not universal; when present, synthesize the supported contribution, decisive evidence, and boundary without introducing new claims or citations.",
            "boundary": "A detected heading is structural evidence only and does not validate the conclusion's claims.",
        },
    }
    rules = []
    for section, specification in specifications.items():
        matched = [source for source in primary if section in source["structure"]["section_order"]]
        venue_counts = {}
        for conference in CONFERENCES:
            population = [source for source in primary if source["conference"] == conference]
            venue_counts[conference] = {
                "matched": sum(section in source["structure"]["section_order"] for source in population),
                "population": len(population),
            }
        rules.append({
            "rule_id": f"cross-venue-{section}-structural-coverage",
            "skills": ["top-cs-writing", "top-cs-polishing", "top-cs-reviewer"],
            "venue": "cross-venue",
            "section": section,
            "source_type": "accepted-title-verified-public-version",
            "evidence_kind": "deterministic-structural-aggregate",
            "source_selector": f"eligibility=primary-writing-evidence AND structure.section_order CONTAINS {section}",
            "matched_source_ids": [source["source_id"] for source in matched],
            "matched_count": len(matched),
            "population_count": len(primary),
            "venue_counts": venue_counts,
            "confidence": "medium",
            "last_verified": generated,
            "statement": specification["statement"],
            "boundary": specification["boundary"],
        })
    return {
        "schema_version": 1,
        "generated": generated,
        "population_selector": "eligibility=primary-writing-evidence",
        "population_source_ids": [source["source_id"] for source in primary],
        "rules": rules,
    }


def review_items(corpus_root: Path) -> list[dict[str, Any]]:
    index_path = corpus_root / "sources" / "peer_review_public" / "review_flow_index.yaml"
    if index_path.is_file():
        document = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
        return document.get("flows", [])
    path = corpus_root / "sources" / "peer_review_public" / "Re2" / "curated_full_stage_iclr_20.jsonl"
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def review_stats(corpus_root: Path) -> dict[str, Any]:
    papers = review_items(corpus_root)
    tracks = Counter(item.get("conference_year_track", "unknown") for item in papers)
    decisions = Counter(str(item.get("decision", "unknown")) for item in papers)
    return {
        "schema_version": 2,
        "source_id": "historical-iclr-public-flow-index",
        "source_type": "historical-public-review",
        "relative_path": "sources/peer_review_public/review_flow_index.yaml",
        "license": "Apache-2.0",
        "policy_boundary": "Behavioral evidence only; not a WWW/ICML source and not an ICLR 2026 policy source.",
        "papers": len(papers),
        "target_papers_by_supported_venue": 50,
        "reviews": sum(item.get("review_count", len(item.get("reviews", []))) for item in papers),
        "discussion_threads": sum(item.get("discussion_thread_count", len(item.get("author_rebuttal_and_discussion_threads", []))) for item in papers),
        "meta_reviews": sum(item.get("has_meta_review", bool(item.get("meta_review"))) for item in papers),
        "decisions": sum(bool(item.get("decision")) for item in papers),
        "conference_year_tracks": dict(sorted(tracks.items())),
        "decision_distribution": dict(sorted(decisions.items())),
        "venue_readiness": {
            "iclr": "insufficient-for-venue-specific-v2" if len(papers) < 50 else "ready",
            "icml": "unsupported-no-local-public-flows",
            "www": "unsupported-no-public-behavioral-evidence",
        },
    }


def review_source_records(corpus_root: Path) -> list[dict[str, Any]]:
    records = []
    for item in review_items(corpus_root):
        paper_id = str(item.get("openreview_id", item.get("paper_id", "unknown")))
        stable = hashlib.sha256(paper_id.encode("utf-8")).hexdigest()[:12]
        records.append({
            "source_id": f"historical-iclr-{stable}",
            "source_type": "historical-public-review",
            "venue": "iclr",
            "conference_year_track": item.get("conference_year_track"),
            "decision": item.get("decision"),
            "reviews": item.get("review_count", len(item.get("reviews", []))),
            "discussion_threads": item.get("discussion_thread_count", len(item.get("author_rebuttal_and_discussion_threads", []))),
            "has_meta_review": item.get("has_meta_review", bool(item.get("meta_review"))),
            "has_submission_revision_pair": False,
            "relative_path": "sources/peer_review_public/review_flow_index.yaml",
            "record_locator": paper_id,
            "license": "Apache-2.0",
            "policy_boundary": "Historical ICLR behavioral evidence; not current venue policy.",
        })
    return records


def policy_matrix(official: list[dict[str, Any]], generated: str) -> dict[str, Any]:
    required = ["author", "reviewer", "review-form", "response", "anonymity", "supplement", "ethics-llm", "artifact-reproducibility", "template", "camera-ready"]
    venues: dict[str, Any] = {}
    for venue, conference in (("www", "WWW2026"), ("iclr", "ICLR2026"), ("icml", "ICML2026")):
        rows = [s for s in official if s["conference"] == conference]
        cells = {}
        for category in required:
            matches = [s for s in rows if category in s["categories"]]
            available = [s for s in matches if s["availability"] == "collected"]
            cells[category] = {
                "status": "verified" if available else "not-public-or-not-collected",
                "source_ids": [s["source_id"] for s in available],
            }
        venues[venue] = {"year": 2026, "last_verified": generated, "categories": cells}
    return {"schema_version": 2, "venues": venues}


def derive(corpus_root: Path, generated: str | None = None, schema_version: int = 2) -> dict[str, Any]:
    if schema_version != 2:
        raise ValueError("only schema version 2 is supported")
    generated = generated or date.today().isoformat()
    sources, duplicates = scan_papers(corpus_root)
    official = official_sources(corpus_root, generated)
    return {
        "index": {
            "schema_version": 2,
            "generated": generated,
            "corpus_root": "external-read-only",
            "policy": {
                "raw_text_copied": False,
                "official_policy_only_for_hard_constraints": True,
                "public_versions_not_official_format_evidence": True,
                "www_primary_track": "Research",
                "heuristic_labels_are_not_rules": True,
                "private_regression_excluded": True,
            },
            "targets": {
                "primary_papers_per_venue": 30,
                "minimum_paper_types": 4,
                "minimum_research_topics": 6,
                "maximum_single_topic_fraction": 0.25,
                "public_review_flows_per_supported_venue": 50,
                "discussion_flows_for_venue_response_rules": 30,
                "verified_version_pairs_iclr_icml": 20,
            },
            "summary": {
                "pdf_files": sum(len(d["occurrences"]) for d in duplicates) + len(sources) - len(duplicates),
                "unique_pdfs": len(sources),
                "primary_writing_evidence": sum(s["eligibility"] == "primary-writing-evidence" for s in sources),
            },
            "official_sources": official,
            "paper_sources": sources,
            "duplicates": duplicates,
            "review_sources": review_source_records(corpus_root),
        },
        "structure": structure_stats(sources, duplicates),
        "reviews": review_stats(corpus_root),
        "policy_matrix": policy_matrix(official, generated),
        "full_section_rules": full_section_rules(sources, generated),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--schema-version", type=int, choices=(2,), default=2)
    parser.add_argument("--generated-date", help="Override generated date for reproducible tests")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing files")
    args = parser.parse_args()
    corpus_root = args.corpus_root.resolve()
    if not (corpus_root / "papers").is_dir():
        parser.error(f"not a supported corpus root: {corpus_root}")
    result = derive(corpus_root, args.generated_date, args.schema_version)
    if args.dry_run:
        print(json.dumps(result["index"]["summary"], ensure_ascii=False, indent=2))
        return 0
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "corpus-index.yaml").write_text(yaml.safe_dump(result["index"], sort_keys=False, allow_unicode=True), encoding="utf-8")
    (args.output_dir / "structure-stats.json").write_text(json.dumps(result["structure"], ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "review-stats.json").write_text(json.dumps(result["reviews"], ensure_ascii=False, indent=2), encoding="utf-8")
    (args.output_dir / "policy-matrix.yaml").write_text(yaml.safe_dump(result["policy_matrix"], sort_keys=False, allow_unicode=True), encoding="utf-8")
    (args.output_dir / "full-section-rules.yaml").write_text(yaml.safe_dump(result["full_section_rules"], sort_keys=False, allow_unicode=True), encoding="utf-8")
    print(json.dumps(result["index"]["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
