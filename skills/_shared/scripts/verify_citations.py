#!/usr/bin/env python3
"""Verify BibTeX metadata through public bibliographic services without downloading full text."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Callable


USER_AGENT = "top-cs-paper-skills/2.3 citation-metadata-verifier"
SOURCES = ("crossref", "arxiv", "dblp")


def normalize_title(value: str | None) -> str:
    text = re.sub(r"[{}]", "", value or "")
    return re.sub(r"[^a-z0-9]+", " ", text.casefold()).strip()


def title_score(left: str | None, right: str | None) -> float:
    a, b = normalize_title(left), normalize_title(right)
    return SequenceMatcher(None, a, b).ratio() if a and b else 0.0


def author_tokens(authors: list[str]) -> set[str]:
    result: set[str] = set()
    for author in authors:
        clean = re.sub(r"[^A-Za-z0-9 -]", " ", author).strip().casefold()
        if clean:
            result.add(clean.split()[-1])
    return result


def split_top_level(text: str, delimiter: str = ",") -> list[str]:
    parts: list[str] = []
    start = 0
    brace = 0
    quoted = False
    escaped = False
    for index, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if char == '"' and brace == 0:
            quoted = not quoted
        elif not quoted:
            if char == "{":
                brace += 1
            elif char == "}":
                brace = max(0, brace - 1)
            elif char == delimiter and brace == 0:
                parts.append(text[start:index])
                start = index + 1
    parts.append(text[start:])
    return parts


def unwrap(value: str) -> str:
    value = value.strip().rstrip(",").strip()
    while len(value) >= 2 and ((value[0] == "{" and value[-1] == "}") or (value[0] == '"' and value[-1] == '"')):
        value = value[1:-1].strip()
    return re.sub(r"\s+", " ", value)


def parse_bibtex(text: str) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    cursor = 0
    while True:
        match = re.search(r"@([A-Za-z]+)\s*([({])", text[cursor:])
        if not match:
            break
        entry_type = match.group(1).casefold()
        opener = match.group(2)
        start = cursor + match.end()
        closer = "}" if opener == "{" else ")"
        depth = 1
        quoted = False
        escaped = False
        end = start
        while end < len(text) and depth:
            char = text[end]
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif not quoted:
                if char == opener:
                    depth += 1
                elif char == closer:
                    depth -= 1
            end += 1
        body = text[start:end - 1]
        cursor = end
        if entry_type in {"comment", "preamble", "string"}:
            continue
        pieces = split_top_level(body)
        if not pieces:
            continue
        key = pieces[0].strip()
        fields: dict[str, str] = {}
        for piece in pieces[1:]:
            if "=" not in piece:
                continue
            name, value = piece.split("=", 1)
            fields[name.strip().casefold()] = unwrap(value)
        authors = [part.strip() for part in re.split(r"\s+and\s+", fields.get("author", ""), flags=re.IGNORECASE) if part.strip()]
        year_match = re.search(r"\d{4}", fields.get("year", ""))
        doi = fields.get("doi")
        if doi:
            doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi, flags=re.IGNORECASE).strip()
        arxiv_id = fields.get("eprint") if fields.get("archiveprefix", "").casefold() == "arxiv" else None
        entries.append({
            "citation_key": key,
            "entry_type": entry_type,
            "title": fields.get("title"),
            "authors": authors,
            "year": int(year_match.group()) if year_match else None,
            "doi": doi,
            "arxiv_id": arxiv_id,
        })
    return entries


class Fetcher:
    def __init__(self, cache_dir: Path | None, offline: bool, timeout: float, delay: float, opener: Callable[..., Any] = urllib.request.urlopen):
        self.cache_dir = cache_dir
        self.offline = offline
        self.timeout = timeout
        self.delay = delay
        self.opener = opener

    def get(self, source: str, url: str) -> tuple[str, bool]:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
        cache_path = self.cache_dir / source / f"{digest}.txt" if self.cache_dir else None
        if cache_path and cache_path.is_file():
            return cache_path.read_text(encoding="utf-8"), True
        if self.offline:
            raise RuntimeError("offline cache miss")
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json, application/atom+xml, text/xml"})
        try:
            with self.opener(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8", errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise RuntimeError(str(exc)) from exc
        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(body, encoding="utf-8")
        if self.delay:
            time.sleep(self.delay)
        return body, False


def crossref_candidate(entry: dict[str, Any], fetcher: Fetcher) -> tuple[dict[str, Any] | None, bool]:
    if entry.get("doi"):
        url = "https://api.crossref.org/works/" + urllib.parse.quote(entry["doi"], safe="")
    elif entry.get("title"):
        query = urllib.parse.urlencode({"query.title": entry["title"], "rows": 3, "select": "DOI,title,author,published"})
        url = "https://api.crossref.org/works?" + query
    else:
        return None, False
    body, cached = fetcher.get("crossref", url)
    message = json.loads(body).get("message", {})
    items = message.get("items", [message]) if isinstance(message, dict) else []
    if not items:
        return None, cached
    best = max(items, key=lambda item: title_score(entry.get("title"), " ".join(item.get("title", []))))
    year_parts = best.get("published", {}).get("date-parts", [[None]])
    return {
        "title": " ".join(best.get("title", [])),
        "authors": [" ".join(filter(None, [a.get("given"), a.get("family")])) for a in best.get("author", [])],
        "year": year_parts[0][0] if year_parts and year_parts[0] else None,
        "identifier": best.get("DOI"),
        "url": f"https://doi.org/{best.get('DOI')}" if best.get("DOI") else None,
        "exact_identifier": bool(entry.get("doi") and best.get("DOI", "").casefold() == entry["doi"].casefold()),
    }, cached


def arxiv_candidate(entry: dict[str, Any], fetcher: Fetcher) -> tuple[dict[str, Any] | None, bool]:
    if entry.get("arxiv_id"):
        query = urllib.parse.urlencode({"id_list": entry["arxiv_id"], "max_results": 1})
    elif entry.get("title"):
        query = urllib.parse.urlencode({"search_query": f'ti:"{entry["title"]}"', "max_results": 3})
    else:
        return None, False
    body, cached = fetcher.get("arxiv", "https://export.arxiv.org/api/query?" + query)
    root = ET.fromstring(body)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    candidates = []
    for item in root.findall("atom:entry", ns):
        identifier = (item.findtext("atom:id", default="", namespaces=ns).rsplit("/", 1)[-1])
        title = re.sub(r"\s+", " ", item.findtext("atom:title", default="", namespaces=ns)).strip()
        candidates.append({
            "title": title,
            "authors": [node.findtext("atom:name", default="", namespaces=ns) for node in item.findall("atom:author", ns)],
            "year": int(item.findtext("atom:published", default="0000", namespaces=ns)[:4]) or None,
            "identifier": identifier,
            "url": item.findtext("atom:id", default=None, namespaces=ns),
            "exact_identifier": bool(entry.get("arxiv_id") and identifier.split("v", 1)[0] == entry["arxiv_id"].split("v", 1)[0]),
        })
    return (max(candidates, key=lambda item: title_score(entry.get("title"), item["title"])) if candidates else None), cached


def dblp_candidate(entry: dict[str, Any], fetcher: Fetcher) -> tuple[dict[str, Any] | None, bool]:
    if not entry.get("title"):
        return None, False
    query = urllib.parse.urlencode({"q": entry["title"], "format": "json", "h": 3})
    body, cached = fetcher.get("dblp", "https://dblp.org/search/publ/api?" + query)
    hits = json.loads(body).get("result", {}).get("hits", {}).get("hit", [])
    candidates = []
    for hit in hits:
        info = hit.get("info", {})
        author_value = info.get("authors", {}).get("author", [])
        if isinstance(author_value, dict):
            author_value = [author_value]
        authors = [a.get("text", "") if isinstance(a, dict) else str(a) for a in author_value]
        candidates.append({
            "title": html.unescape(re.sub(r"<[^>]+>", "", info.get("title", ""))),
            "authors": authors,
            "year": int(info["year"]) if str(info.get("year", "")).isdigit() else None,
            "identifier": info.get("doi") or info.get("key"),
            "url": info.get("url"),
            "exact_identifier": bool(entry.get("doi") and str(info.get("doi", "")).casefold() == entry["doi"].casefold()),
        })
    return (max(candidates, key=lambda item: title_score(entry.get("title"), item["title"])) if candidates else None), cached


LOOKUPS = {"crossref": crossref_candidate, "arxiv": arxiv_candidate, "dblp": dblp_candidate}


def assess_source(source: str, entry: dict[str, Any], candidate: dict[str, Any] | None, cached: bool) -> tuple[dict[str, Any], list[str]]:
    if candidate is None:
        return {"name": source, "status": "not-found", "identifier": None, "url": None, "cached": cached}, []
    score = title_score(entry.get("title"), candidate.get("title"))
    exact = bool(candidate.get("exact_identifier"))
    status = "matched" if exact or score >= 0.92 else "partial" if score >= 0.75 else "conflicting"
    conflicts: list[str] = []
    if entry.get("year") and candidate.get("year") and entry["year"] != candidate["year"]:
        conflicts.append(f"{source}: year {entry['year']} != {candidate['year']}")
    expected_authors, found_authors = author_tokens(entry.get("authors", [])), author_tokens(candidate.get("authors", []))
    if expected_authors and found_authors and not expected_authors.intersection(found_authors):
        conflicts.append(f"{source}: author set has no overlap")
    if conflicts and status == "matched":
        status = "conflicting"
    return {
        "name": source,
        "status": "cached" if cached and status == "matched" else status,
        "match_status": status,
        "identifier": candidate.get("identifier"),
        "url": candidate.get("url"),
        "title_score": round(score, 3),
        "cached": cached,
    }, conflicts


def verify_entry(entry: dict[str, Any], sources: list[str], fetcher: Fetcher) -> dict[str, Any]:
    results: list[dict[str, Any]] = []
    conflicts: list[str] = []
    exact_match = False
    for source in sources:
        try:
            candidate, cached = LOOKUPS[source](entry, fetcher)
            result, source_conflicts = assess_source(source, entry, candidate, cached)
            exact_match = exact_match or bool(candidate and candidate.get("exact_identifier") and not source_conflicts)
            conflicts.extend(source_conflicts)
        except Exception as exc:  # service and parse failures are report data
            result = {"name": source, "status": "error", "identifier": None, "url": None, "error": str(exc)}
        results.append(result)
    effective = [item.get("match_status", item["status"]) for item in results]
    matches = sum(status == "matched" for status in effective)
    partials = sum(status == "partial" for status in effective)
    if conflicts or "conflicting" in effective:
        status = "conflicting"
    elif exact_match or matches >= 2:
        status = "verified"
    elif matches or partials:
        status = "partial"
    elif effective and all(item == "not-found" for item in effective):
        status = "not-found"
    elif effective and all(item == "error" for item in effective):
        status = "error"
    else:
        status = "not-found" if "not-found" in effective else "error"
    return {
        **entry,
        "bibliographic_status": status,
        "claim_entailment_status": "needs-source-text" if status in {"verified", "partial"} else "not-checked",
        "sources": results,
        "conflicts": conflicts,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def verify_bibliography(path: Path, sources: list[str], fetcher: Fetcher) -> dict[str, Any]:
    entries = parse_bibtex(path.read_text(encoding="utf-8"))
    records = [verify_entry(entry, sources, fetcher) for entry in entries]
    counts = {status: sum(record["bibliographic_status"] == status for record in records) for status in ("verified", "partial", "conflicting", "not-found", "error")}
    return {"schema_version": 1, "source_file": str(path), "sources": sources, "records": records, "summary": {"total": len(records), **counts}, "boundary": "Bibliographic metadata only; claim entailment is not automatically verified."}


def to_markdown(report: dict[str, Any]) -> str:
    lines = ["# Citation metadata verification", "", report["boundary"], "", "| Key | Status | DOI/arXiv | Conflicts |", "|---|---|---|---|"]
    for record in report["records"]:
        identifier = record.get("doi") or record.get("arxiv_id") or ""
        lines.append(f"| {record['citation_key']} | {record['bibliographic_status']} | {identifier} | {'; '.join(record['conflicts'])} |")
    lines += ["", "Unverified propositions must retain `[CITATION NEEDED: proposition]` until source text is checked."]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bib", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--sources", default=",".join(SOURCES))
    parser.add_argument("--cache-dir", type=Path)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--delay", type=float, default=0.2)
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    sources = [item.strip().casefold() for item in args.sources.split(",") if item.strip()]
    unknown = sorted(set(sources) - set(SOURCES))
    if unknown:
        parser.error(f"unknown source(s): {', '.join(unknown)}")
    report = verify_bibliography(args.bib, sources, Fetcher(args.cache_dir, args.offline, args.timeout, args.delay))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) if args.format == "json" else to_markdown(report), encoding="utf-8")
    return 0 if not report["summary"]["conflicting"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
