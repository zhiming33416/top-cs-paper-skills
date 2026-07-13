#!/usr/bin/env python3
"""Collect public PDFs for aggregate visual-style evidence.

Raw PDFs are written only under the external corpus root. The repository keeps
only a source manifest with provenance, hashes, and verification status.
"""

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
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

import yaml

try:
    import fitz  # type: ignore
except ImportError:  # pragma: no cover - verification falls back to byte checks
    fitz = None


ROOT = Path(__file__).resolve().parents[1]
VENUE_CONFERENCES = {"www": "WWW2026", "iclr": "ICLR2026", "icml": "ICML2026"}
OPENREVIEW_GROUPS = {"iclr": "ICLR.cc/2026/Conference", "icml": "ICML.cc/2026/Conference"}
WWW_ACCEPTED_URL = "https://www2026.thewebconf.org/accepted/research-tracks.html"
ICML_VIRTUAL_PAPERS_URL = "https://icml.cc/virtual/2026/papers.html"
ICML_VIRTUAL_ROOT = "https://icml.cc/virtual/2026/"
USER_AGENT = "top-cs-paper-skills-visual-style-collector/1.0"
CACHE_SCHEMA_VERSION = 2
RESOLVER_VERSION = "2026-main-v2"
CACHE_TTLS = {
    "success": None,
    "no-match": timedelta(days=7),
    "network-error": timedelta(days=1),
    "rate-limited": timedelta(hours=6),
}
SOURCE_PRIORITY = {
    "openreview-accepted": 10,
    "openreview-legacy-accepted": 12,
    "openreview-submissions-public-page": 14,
    "icml-virtual-official": 15,
    "pmlr-official": 20,
    "arxiv-title-exact": 40,
    "author-public-pdf": 45,
    "official-public-pdf": 25,
    "www-accepted-research-index": 70,
    "corpus-index-public-version": 80,
}
PUBLIC_FULLTEXT_SOURCE_KINDS = {
    "arxiv-title-exact",
    "author-public-pdf",
    "official-public-pdf",
}
OPENREVIEW_ACCEPTED_TRACKS = {
    "iclr": ("Oral", "Poster"),
    "icml": ("Oral", "Spotlight", "Poster", "Regular"),
}


def normalize_title(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<[^>]+>", " ", value)
    value = value.replace("_", " ")
    value = re.sub(r"[\u2010-\u2015]", "-", value)
    value = re.sub(r"[^a-zA-Z0-9]+", " ", value).strip().lower()
    return re.sub(r"\s+", " ", value)


def title_fingerprint(title: str) -> str:
    return hashlib.sha256(normalize_title(title).encode("utf-8")).hexdigest()[:16]


def safe_name(value: str, limit: int = 120) -> str:
    value = html.unescape(value)
    value = re.sub(r"[<>:\"/\\|?*\x00-\x1f]", "_", value)
    value = re.sub(r"\s+", " ", value).strip().rstrip(".")
    return (value[:limit].rstrip() or "untitled").rstrip(".")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_url(url: str, timeout: int = 60, user_agent: str = USER_AGENT) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def content_value(content: dict[str, Any], key: str) -> str:
    value = content.get(key)
    if isinstance(value, dict) and "value" in value:
        value = value["value"]
    if isinstance(value, list):
        return " ".join(str(item) for item in value)
    return "" if value is None else str(value)


def detect_openreview_track(venue: str, venue_text: str) -> str | None:
    lower = venue_text.lower()
    if any(word in lower for word in ("reject", "withdraw", "desk reject", "submission", "submitted")):
        return None
    for track in OPENREVIEW_ACCEPTED_TRACKS[venue]:
        if track.lower() in lower:
            return track
    if f"{venue.upper()} 2026 Conference".lower() in lower:
        return "Regular" if venue == "icml" else "Poster"
    return None


def openreview_candidate(note: dict[str, Any], venue: str, year: int) -> dict[str, Any] | None:
    content = note.get("content", {})
    if not isinstance(content, dict):
        return None
    note_id = str(note.get("id") or note.get("forum") or "").strip()
    title = content_value(content, "title").strip()
    venue_text = " ".join(
        value for value in (
            content_value(content, "venue"),
            content_value(content, "venueid"),
            content_value(content, "presentation"),
        )
        if value
    )
    track = detect_openreview_track(venue, venue_text)
    if not note_id or not title or not track:
        return None
    group = f"{venue.upper()} {year} Conference"
    if group.lower() not in venue_text.lower() and f"{venue.upper()}.cc/{year}/Conference".lower() not in venue_text.lower():
        return None
    return {
        "source_id": f"{venue}{year}-{note_id}",
        "venue": venue,
        "conference": VENUE_CONFERENCES[venue],
        "year": year,
        "track": track,
        "title": title,
        "title_fingerprint": title_fingerprint(title),
        "public_url": f"https://openreview.net/pdf?id={urllib.parse.quote(note_id)}",
        "source_page_url": f"https://openreview.net/forum?id={urllib.parse.quote(note_id)}",
        "source_kind": "openreview-accepted",
        "source_priority": SOURCE_PRIORITY["openreview-accepted"],
        "candidate_discovery_sources": ["openreview-api2"],
        "license": "openreview-public-paper-pdf",
        "eligibility": "holdout",
        "verification_status": "not-downloaded",
        "collection_status": "candidate",
    }


def parse_openreview_notes(payload: str | bytes | dict[str, Any], venue: str, year: int = 2026, target_per_venue: int = 30) -> list[dict[str, Any]]:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    data = json.loads(payload) if isinstance(payload, str) else payload
    candidates: list[dict[str, Any]] = []
    for note in data.get("notes", []):
        candidate = openreview_candidate(note, venue, year)
        if candidate:
            candidates.append(candidate)
        if len(candidates) >= target_per_venue:
            break
    return candidates


def openreview_api_url(venue: str, year: int, offset: int = 0, limit: int = 1000) -> str:
    group = OPENREVIEW_GROUPS[venue].replace("/2026/", f"/{year}/")
    query = urllib.parse.urlencode({"content.venueid": group, "limit": limit, "offset": offset})
    return f"https://api2.openreview.net/notes?{query}"


def legacy_openreview_api_url(venue: str, year: int, offset: int = 0, limit: int = 1000) -> str:
    invitation = f"{venue.upper()}.cc/{year}/Conference/-/Submission"
    query = urllib.parse.urlencode({"invitation": invitation, "details": "directReplies", "limit": limit, "offset": offset})
    return f"https://api.openreview.net/notes?{query}"


def legacy_openreview_candidate(note: dict[str, Any], venue: str, year: int) -> dict[str, Any] | None:
    content = note.get("content", {})
    if not isinstance(content, dict):
        return None
    title = content_value(content, "title").strip()
    note_id = str(note.get("forum") or note.get("id") or "").strip()
    replies = ((note.get("details") or {}).get("directReplies") or []) if isinstance(note.get("details"), dict) else []
    decision_text = " ".join(
        content_value(reply.get("content", {}), "decision") + " " + content_value(reply.get("content", {}), "venue")
        for reply in replies
        if isinstance(reply, dict)
    )
    lower = decision_text.lower()
    if not title or not note_id or "accept" not in lower or any(word in lower for word in ("reject", "withdraw")):
        return None
    track = "Oral" if "oral" in lower else "Poster"
    return {
        "source_id": f"{venue}{year}-{note_id}",
        "venue": venue,
        "conference": VENUE_CONFERENCES[venue],
        "year": year,
        "track": track,
        "title": title,
        "title_fingerprint": title_fingerprint(title),
        "public_url": f"https://openreview.net/pdf?id={urllib.parse.quote(note_id)}",
        "source_page_url": f"https://openreview.net/forum?id={urllib.parse.quote(note_id)}",
        "source_kind": "openreview-legacy-accepted",
        "source_priority": SOURCE_PRIORITY["openreview-legacy-accepted"],
        "candidate_discovery_sources": ["openreview-legacy-api"],
        "license": "openreview-public-paper-pdf",
        "eligibility": "holdout",
        "verification_status": "not-downloaded",
        "collection_status": "candidate",
    }


def discover_openreview(venue: str, year: int, target_per_venue: int, timeout: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while len(rows) < target_per_venue and offset < 5000:
        url = openreview_api_url(venue, year, offset=offset)
        payload = read_url(url, timeout=timeout)
        batch = parse_openreview_notes(payload, venue, year, target_per_venue * 2)
        seen = {row["source_id"] for row in rows}
        rows.extend(row for row in batch if row["source_id"] not in seen)
        data = json.loads(payload.decode("utf-8"))
        note_count = len(data.get("notes", []))
        if note_count == 0:
            break
        offset += note_count
    return rows[:target_per_venue]


def discover_openreview_legacy(venue: str, year: int, target_per_venue: int, timeout: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    offset = 0
    while len(rows) < target_per_venue and offset < 5000:
        payload = read_url(legacy_openreview_api_url(venue, year, offset=offset), timeout=timeout)
        data = json.loads(payload.decode("utf-8"))
        notes = data.get("notes", [])
        for note in notes:
            candidate = legacy_openreview_candidate(note, venue, year)
            if candidate:
                rows.append(candidate)
            if len(rows) >= target_per_venue:
                break
        if not notes:
            break
        offset += len(notes)
    return rows[:target_per_venue]


def parse_www_research_html(payload: str | bytes, year: int = 2026, target_per_venue: int = 30) -> list[dict[str, Any]]:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8", errors="replace")
    text = html.unescape(payload)
    text = re.sub(r"</(?:li|p|div|h\d)>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = text.replace("\u2014", " -- ").replace("\u2013", " -- ")
    candidates: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        match = re.search(r"\((rfp\d+)\)\s+(.+?)\s+--\s+(.+)$", line, flags=re.IGNORECASE)
        if not match:
            continue
        paper_id, title, authors = match.groups()
        candidates.append({
            "source_id": f"www{year}-{paper_id.lower()}",
            "venue": "www",
            "conference": "WWW2026",
            "year": year,
            "track": "Research",
            "title": title.strip(),
            "title_fingerprint": title_fingerprint(title),
            "public_url": None,
            "source_page_url": WWW_ACCEPTED_URL,
            "source_kind": "www-accepted-research-index",
            "source_priority": SOURCE_PRIORITY["www-accepted-research-index"],
            "candidate_discovery_sources": ["www-accepted-research-index"],
            "license": "official-public-title-index",
            "eligibility": "holdout",
            "verification_status": "public-fulltext-not-resolved",
            "collection_status": "candidate",
            "authors_fingerprint": hashlib.sha256(normalize_title(authors).encode("utf-8")).hexdigest()[:16],
        })
        if len(candidates) >= target_per_venue:
            break
    return candidates


def parse_pmlr_volume_html(payload: str | bytes, year: int = 2026, target_per_venue: int = 30) -> list[dict[str, Any]]:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8", errors="replace")
    blocks = re.split(r"<div[^>]+class=[\"'][^\"']*paper[^\"']*[\"'][^>]*>", payload, flags=re.IGNORECASE)
    rows: list[dict[str, Any]] = []
    for block in blocks:
        title_match = re.search(r"<p[^>]+class=[\"']title[\"'][^>]*>(.*?)</p>", block, flags=re.IGNORECASE | re.DOTALL)
        pdf_match = re.search(r'href=["\']([^"\']+\.pdf)["\']', block, flags=re.IGNORECASE)
        if not title_match or not pdf_match:
            continue
        title = re.sub(r"<[^>]+>", " ", title_match.group(1))
        pdf = urllib.parse.urljoin("https://proceedings.mlr.press/", html.unescape(pdf_match.group(1)))
        rows.append({
            "source_id": f"icml{year}-pmlr-{title_fingerprint(title)}",
            "venue": "icml",
            "conference": "ICML2026",
            "year": year,
            "track": "Main",
            "title": html.unescape(title).strip(),
            "title_fingerprint": title_fingerprint(title),
            "public_url": pdf,
            "source_page_url": "https://proceedings.mlr.press/",
            "source_kind": "pmlr-official",
            "source_priority": SOURCE_PRIORITY["pmlr-official"],
            "candidate_discovery_sources": ["pmlr-official"],
            "license": "pmlr-public-paper-pdf",
            "eligibility": "holdout",
            "verification_status": "not-downloaded",
            "collection_status": "candidate",
        })
        if len(rows) >= target_per_venue:
            break
    return rows


def parse_icml_virtual_papers(payload: str | bytes | dict[str, Any], year: int = 2026, target_per_venue: int = 30) -> list[dict[str, Any]]:
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")
    data = json.loads(payload) if isinstance(payload, str) else payload
    rows: list[dict[str, Any]] = []
    for item in data.get("results", []):
        if not isinstance(item, dict):
            continue
        title = str(item.get("name") or item.get("title") or "").strip()
        pdf = str(item.get("paper_pdf_url") or "").strip()
        event_type = str(item.get("eventtype") or item.get("presentation_type") or "Regular").strip()
        decision = str(item.get("decision") or "").lower()
        accepted = "accept" in decision or event_type.lower() in {"oral", "spotlight", "poster", "regular"}
        if not title or not accepted or event_type.lower() not in {"oral", "spotlight", "poster", "regular"}:
            continue
        item_id = str(item.get("id") or item.get("uid") or title_fingerprint(title))
        rows.append({
            "source_id": f"icml{year}-virtual-{item_id}",
            "venue": "icml",
            "conference": VENUE_CONFERENCES["icml"],
            "year": year,
            "track": event_type,
            "title": title,
            "title_fingerprint": title_fingerprint(title),
            "public_url": urllib.parse.urljoin(ICML_VIRTUAL_ROOT, pdf) if pdf else None,
            "source_page_url": ICML_VIRTUAL_PAPERS_URL,
            "source_kind": "icml-virtual-official",
            "source_priority": SOURCE_PRIORITY["icml-virtual-official"],
            "candidate_discovery_sources": ["icml-virtual-json"],
            "license": "icml-public-paper-pdf",
            "eligibility": "holdout",
            "verification_status": "not-downloaded",
            "collection_status": "candidate",
        })
        if len(rows) >= target_per_venue:
            break
    return rows


def discover_icml_virtual(year: int, target_per_venue: int, timeout: int) -> list[dict[str, Any]]:
    page = read_url(ICML_VIRTUAL_PAPERS_URL.replace("2026", str(year)), timeout=timeout).decode("utf-8", errors="replace")
    names = re.findall(r"(?:[\"']|\\b)(serve_[A-Za-z0-9_-]+\\.json)(?:[\"']|\\b)", page)
    names.extend(re.findall(r"start\(\s*[\"']([^\"']+\.json)[\"']", page))
    names.extend(["serve_orals_posters.json", "serve_papers.json"])
    seen: set[str] = set()
    for name in names:
        if name in seen:
            continue
        seen.add(name)
        url = urllib.parse.urljoin(ICML_VIRTUAL_PAPERS_URL.replace("papers.html", ""), name)
        try:
            rows = parse_icml_virtual_papers(read_url(url, timeout=timeout), year, target_per_venue)
        except (urllib.error.URLError, json.JSONDecodeError):
            continue
        if rows:
            return rows
    return []


def discover_icml_pmlr(year: int, target_per_venue: int, timeout: int) -> list[dict[str, Any]]:
    """Find a published ICML volume only when PMLR itself labels it as the target year."""
    home = read_url("https://proceedings.mlr.press/", timeout=timeout).decode("utf-8", errors="replace")
    matches = re.findall(r'href=["\']([^"\']+)["\'][^>]*>\s*([^<]*ICML[^<]*2026[^<]*)<', home, flags=re.IGNORECASE)
    for href, _label in matches:
        url = urllib.parse.urljoin("https://proceedings.mlr.press/", html.unescape(href))
        rows = parse_pmlr_volume_html(read_url(url, timeout=timeout), year, target_per_venue)
        if rows:
            return rows
    return []


def corpus_index_candidates(venue: str, year: int = 2026, target_per_venue: int = 30, index_path: Path | None = None) -> list[dict[str, Any]]:
    index_path = index_path or ROOT / "evidence" / "derived" / "corpus-index.yaml"
    if not index_path.is_file():
        return []
    document = yaml.safe_load(index_path.read_text(encoding="utf-8")) or {}
    conference = VENUE_CONFERENCES[venue]
    rows: list[dict[str, Any]] = []
    for source in document.get("paper_sources", []):
        if source.get("conference") != conference or source.get("eligibility") != "primary-writing-evidence":
            continue
        tracks = source.get("tracks", [])
        if venue == "www" and "Research" not in tracks:
            continue
        title = source.get("title") or source.get("source_id")
        rows.append({
            "source_id": source.get("source_id") or f"{venue}{year}-{title_fingerprint(title)}",
            "venue": venue,
            "conference": conference,
            "year": year,
            "track": tracks[0] if tracks else "Main",
            "title": title,
            "title_fingerprint": title_fingerprint(title),
            "public_url": source.get("public_fulltext_url"),
            "source_page_url": source.get("accepted_title_url"),
            "relative_path": source.get("relative_path"),
            "expected_sha256": source.get("sha256"),
            "source_kind": "corpus-index-public-version",
            "source_priority": SOURCE_PRIORITY["corpus-index-public-version"],
            "candidate_discovery_sources": ["accepted-title-corpus-index"],
            "license": "accepted-title-verified-public-version",
            "eligibility": "holdout",
            "verification_status": "not-verified-by-visual-collector",
            "collection_status": "indexed-candidate",
        })
        if len(rows) >= target_per_venue:
            break
    return rows


def arxiv_query_url(title: str) -> str:
    query = urllib.parse.quote(f'ti:"{title}"')
    return f"https://export.arxiv.org/api/query?search_query={query}&start=0&max_results=5"


def empty_resolver_cache() -> dict[str, Any]:
    return {"schema_version": CACHE_SCHEMA_VERSION, "resolver_version": RESOLVER_VERSION, "entries": {}}


def load_resolver_cache(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return empty_resolver_cache()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return empty_resolver_cache()
    if data.get("schema_version") != CACHE_SCHEMA_VERSION or data.get("resolver_version") != RESOLVER_VERSION:
        return empty_resolver_cache()
    return data if isinstance(data.get("entries"), dict) else empty_resolver_cache()


def save_resolver_cache(path: Path | None, cache: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cache, indent=2, sort_keys=True), encoding="utf-8")


def cache_entry(cache: dict[str, Any] | None, fingerprint: str, now: datetime, force_refresh: bool) -> dict[str, Any] | None:
    if not cache or force_refresh:
        return None
    entry = cache.get("entries", {}).get(fingerprint)
    if not isinstance(entry, dict):
        return None
    ttl = CACHE_TTLS.get(str(entry.get("status")))
    if ttl is None:
        return entry if entry.get("status") == "success" else None
    try:
        checked_at = datetime.fromisoformat(str(entry["checked_at"]))
    except (KeyError, ValueError, TypeError):
        return None
    return entry if checked_at + ttl >= now else None


def cache_result(cache: dict[str, Any] | None, fingerprint: str, status: str, url: str | None, now: datetime) -> None:
    if cache is None:
        return
    cache.setdefault("entries", {})[fingerprint] = {
        "status": status,
        "url": url,
        "checked_at": now.isoformat(),
        "resolver_version": RESOLVER_VERSION,
    }


def resolve_arxiv_pdf(title: str, timeout: int = 60, cache: dict[str, Any] | None = None, force_refresh: bool = False, now: datetime | None = None) -> str | None:
    fingerprint = title_fingerprint(title)
    now = now or datetime.now(timezone.utc)
    cached = cache_entry(cache, fingerprint, now, force_refresh)
    if cached:
        return cached.get("url") if cached.get("status") == "success" else None
    try:
        payload = read_url(arxiv_query_url(title), timeout=timeout)
    except urllib.error.HTTPError as exc:
        cache_result(cache, fingerprint, "rate-limited" if exc.code == 429 else "network-error", None, now)
        return None
    except urllib.error.URLError:
        cache_result(cache, fingerprint, "network-error", None, now)
        return None
    root = ET.fromstring(payload)
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    target = normalize_title(title)
    for entry in root.findall("atom:entry", namespace):
        found_title = entry.findtext("atom:title", default="", namespaces=namespace)
        if normalize_title(found_title) != target:
            continue
        identifier = entry.findtext("atom:id", default="", namespaces=namespace)
        if not identifier:
            continue
        arxiv_id = identifier.rstrip("/").split("/")[-1]
        result = f"https://arxiv.org/pdf/{arxiv_id}"
        cache_result(cache, fingerprint, "success", result, now)
        return result
    cache_result(cache, fingerprint, "no-match", None, now)
    return None


def resolve_title_exact_public_fulltext(candidates: list[dict[str, Any]], target_per_venue: int, timeout: int, rate_limit: float, cache_path: Path | None = None, max_queries: int | None = None, force_refresh: bool = False) -> list[dict[str, Any]]:
    cache = load_resolver_cache(cache_path)
    resolved: list[dict[str, Any]] = []
    query_count = 0
    eligible_by_venue: dict[str, int] = defaultdict(int)
    for candidate in candidates:
        pdf_url = candidate.get("public_url")
        used_arxiv = False
        queried_network = False
        if not pdf_url:
            fingerprint = title_fingerprint(candidate["title"])
            cached = cache_entry(cache, fingerprint, datetime.now(timezone.utc), force_refresh)
            if cached:
                pdf_url = cached.get("url") if cached.get("status") == "success" else None
            elif max_queries is None or query_count < max_queries:
                pdf_url = resolve_arxiv_pdf(candidate["title"], timeout=timeout, cache=cache, force_refresh=False)
                query_count += 1
                queried_network = True
            used_arxiv = bool(pdf_url)
        if used_arxiv and pdf_url:
            candidate = dict(candidate)
            candidate["public_url"] = pdf_url
            candidate["source_kind"] = "arxiv-title-exact"
            candidate["license"] = "arxiv-public-paper-pdf"
            candidate["document_version"] = "public-preprint-or-author-version"
            candidate["accepted_title_verified"] = True
            candidate["source_priority"] = SOURCE_PRIORITY["arxiv-title-exact"]
            candidate["candidate_discovery_sources"] = list(candidate.get("candidate_discovery_sources", [])) + ["arxiv-title-exact"]
            eligible_by_venue[candidate["venue"]] += 1
        entry = cache.get("entries", {}).get(title_fingerprint(candidate["title"]), {})
        if entry:
            candidate = dict(candidate)
            candidate["resolver_cache_status"] = entry.get("status")
        resolved.append(candidate)
        if all(eligible_by_venue.get(venue, 0) >= target_per_venue for venue in {row["venue"] for row in candidates}):
            break
        if queried_network:
            time.sleep(rate_limit)
    save_resolver_cache(cache_path, cache)
    return resolved


def resolve_www_public_fulltext(candidates: list[dict[str, Any]], target_per_venue: int, timeout: int, rate_limit: float) -> list[dict[str, Any]]:
    """Backward-compatible WWW-only wrapper for the generic resolver."""
    return resolve_title_exact_public_fulltext(candidates, target_per_venue, timeout, rate_limit)


def relative_pdf_path(candidate: dict[str, Any]) -> str:
    conference = VENUE_CONFERENCES[candidate["venue"]]
    track = safe_name(str(candidate.get("track") or "main"), limit=32)
    title = safe_name(candidate["title"], limit=110)
    return f"papers/{conference}/verified_fulltext/{track} - {title}.pdf"


def extract_first_pages_text(path: Path, pages: int = 2) -> str:
    if fitz is None:
        raw = path.read_bytes()[:300_000]
        return raw.decode("latin-1", errors="ignore")
    document = fitz.open(path)
    texts = []
    for index in range(min(len(document), pages)):
        texts.append(document[index].get_text("text"))
    document.close()
    return "\n".join(texts)


def verify_pdf_for_candidate(path: Path, candidate: dict[str, Any]) -> tuple[str, str, list[str]]:
    notes: list[str] = []
    if not path.is_file():
        return "holdout", "missing-file", ["PDF file is missing"]
    if path.read_bytes()[:5] != b"%PDF-":
        return "holdout", "not-a-valid-pdf", ["Downloaded file is not a PDF"]
    try:
        text = extract_first_pages_text(path)
    except Exception as exc:
        return "holdout", "pdf-read-error", [str(exc)]
    normalized_text = normalize_title(text)
    title_ok = normalize_title(candidate["title"]) in normalized_text
    venue = candidate["venue"]
    marker = {
        "iclr": f"iclr {candidate['year']}",
        "icml": "international conference on machine learning",
        "www": "web conference",
    }[venue]
    marker_ok = marker in normalized_text
    if venue == "www":
        acm_restricted = "dl.acm.org" in str(candidate.get("public_url") or "")
        public_url = str(candidate.get("public_url") or "")
        public_source = candidate.get("source_kind") in PUBLIC_FULLTEXT_SOURCE_KINDS and public_url.startswith("https://")
        if candidate.get("track") == "Research" and title_ok and public_source and not acm_restricted:
            return "style-evidence", "title-exact-public-fulltext", notes
        return "holdout", "www-public-fulltext-not-title-exact", notes
    if title_ok or marker_ok:
        return "style-evidence", "title-or-venue-verified", notes
    return "holdout", "title-and-venue-not-verified", notes


def collect_pdf(candidate: dict[str, Any], corpus_root: Path, timeout: int, refresh: bool, user_agent: str) -> dict[str, Any]:
    row = dict(candidate)
    row["relative_path"] = relative_pdf_path(candidate)
    target = corpus_root / row["relative_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and not refresh:
        row["collection_status"] = "existing"
    else:
        partial = target.with_suffix(target.suffix + ".part")
        try:
            request = urllib.request.Request(str(candidate["public_url"]), headers={"User-Agent": user_agent})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                with partial.open("wb") as handle:
                    while True:
                        chunk = response.read(1024 * 1024)
                        if not chunk:
                            break
                        handle.write(chunk)
            partial.replace(target)
            row["collection_status"] = "collected"
        except urllib.error.URLError as exc:
            row["collection_status"] = "download-error"
            row["download_error"] = str(exc)
            row["relative_path"] = None
            row["sha256"] = None
            row["eligibility"] = "holdout"
            row["verification_status"] = "download-error"
            return row
    row["sha256"] = sha256(target)
    row["bytes"] = target.stat().st_size
    row["eligibility"], row["verification_status"], notes = verify_pdf_for_candidate(target, candidate)
    if notes:
        row["notes"] = notes
    return row


def dry_run_row(candidate: dict[str, Any]) -> dict[str, Any]:
    row = dict(candidate)
    if candidate.get("public_url"):
        row["relative_path"] = candidate.get("relative_path") or relative_pdf_path(candidate)
        row["collection_status"] = "would-download"
        row["verification_status"] = "not-downloaded-dry-run"
    elif candidate.get("relative_path"):
        row["collection_status"] = "would-use-existing-relative-path"
        row["verification_status"] = "not-checked-dry-run"
    else:
        row["relative_path"] = None
        row["collection_status"] = "holdout-no-public-fulltext"
        row["verification_status"] = "public-fulltext-not-resolved"
    row["sha256"] = None
    row["eligibility"] = "holdout"
    return row


def dedupe_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, str] = {}
    for row in rows:
        digest = row.get("sha256")
        if not digest or row.get("eligibility") != "style-evidence":
            continue
        if digest in seen:
            row["duplicate_of"] = seen[digest]
            row["eligibility"] = "holdout"
            row["verification_status"] = f"duplicate-of:{seen[digest]}"
        else:
            seen[digest] = row["source_id"]
    return rows


def merge_candidates(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge official title-index candidates without losing provenance."""
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for candidate in candidates:
        key = (str(candidate.get("venue")), normalize_title(str(candidate.get("title") or "")))
        if not key[1]:
            continue
        candidate = dict(candidate)
        candidate.setdefault("source_priority", SOURCE_PRIORITY.get(str(candidate.get("source_kind")), 100))
        candidate.setdefault("candidate_discovery_sources", [candidate.get("source_kind", "unknown")])
        current = merged.get(key)
        if current is None:
            merged[key] = candidate
            continue
        sources = list(dict.fromkeys(list(current.get("candidate_discovery_sources", [])) + list(candidate.get("candidate_discovery_sources", []))))
        preferred = min(
            (current, candidate),
            key=lambda row: (
                not bool(row.get("public_url")),
                not bool(row.get("relative_path")),
                int(row.get("source_priority", 100)),
            ),
        )
        preferred = dict(preferred)
        preferred["candidate_discovery_sources"] = sources
        preferred["source_priority"] = int(preferred.get("source_priority", 100))
        merged[key] = preferred
    return sorted(merged.values(), key=lambda row: (row["venue"], int(row.get("source_priority", 100)), row["title"]))


def limit_candidates_per_venue(candidates: list[dict[str, Any]], corpus_root: Path, target_per_venue: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for venue in sorted({str(row.get("venue")) for row in candidates}):
        rows = [row for row in candidates if row.get("venue") == venue]
        rows.sort(
            key=lambda row: (
                not bool(row.get("public_url")),
                not bool(row.get("relative_path") and (corpus_root / str(row["relative_path"])).is_file()),
                int(row.get("source_priority", 100)),
                row["title"],
            )
        )
        selected.extend(rows[:target_per_venue])
    return selected


def load_candidate_seed(path: Path | None, venues: list[str], year: int) -> list[dict[str, Any]]:
    """Load accepted-title seeds captured from an official public venue page."""
    if path is None:
        return []
    document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if document.get("schema_version") != 1 or not document.get("official_source_page"):
        raise ValueError("candidate seed requires schema_version 1 and official_source_page")
    rows = []
    for item in document.get("candidates", []):
        venue = str(item.get("venue") or "").lower()
        title = str(item.get("title") or "").strip()
        item_year = int(item.get("year", year))
        if venue not in venues or item_year != year or not title:
            continue
        track = str(item.get("track") or "Poster")
        if track not in OPENREVIEW_ACCEPTED_TRACKS.get(venue, ()):
            raise ValueError(f"candidate seed has unsupported accepted track: {track}")
        rows.append({
            "source_id": f"{venue}{year}-public-page-{title_fingerprint(title)}",
            "venue": venue,
            "conference": VENUE_CONFERENCES[venue],
            "year": year,
            "track": track,
            "title": title,
            "title_fingerprint": title_fingerprint(title),
            "public_url": None,
            "source_page_url": item.get("source_page_url") or document["official_source_page"],
            "source_kind": "openreview-submissions-public-page",
            "source_priority": SOURCE_PRIORITY["openreview-submissions-public-page"],
            "candidate_discovery_sources": ["openreview-public-submissions-page"],
            "license": "accepted-title-index-only",
            "eligibility": "holdout",
            "verification_status": "not-downloaded",
            "collection_status": "candidate",
            "accepted_title_verified": True,
        })
    return rows


def discover_candidates(venues: list[str], year: int, target_per_venue: int, timeout: int, rate_limit: float, resolve_preprints: bool, resolver_cache: Path | None = None, max_search_queries: int | None = None, force_refresh_cache: bool = False, discovery_gaps: list[dict[str, str]] | None = None, seed_candidates: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = list(seed_candidates or [])
    for venue in venues:
        if venue == "iclr":
            try:
                rows = discover_openreview(venue, year, target_per_venue, timeout)
            except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
                try:
                    rows = discover_openreview_legacy(venue, year, target_per_venue, timeout)
                except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
                    rows = []
            candidates.extend(rows)
            candidates.extend(corpus_index_candidates(venue, year, target_per_venue))
        elif venue == "icml":
            try:
                candidates.extend(discover_icml_virtual(year, target_per_venue, timeout))
            except urllib.error.URLError:
                pass
            try:
                candidates.extend(discover_openreview(venue, year, target_per_venue, timeout))
            except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
                try:
                    candidates.extend(discover_openreview_legacy(venue, year, target_per_venue, timeout))
                except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
                    pass
            try:
                candidates.extend(discover_icml_pmlr(year, target_per_venue, timeout))
            except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
                pass
            candidates.extend(corpus_index_candidates(venue, year, target_per_venue))
        elif venue == "www":
            try:
                payload = read_url(WWW_ACCEPTED_URL, timeout=timeout)
                rows = parse_www_research_html(payload, year, max(target_per_venue * 4, target_per_venue))
                candidates.extend(rows)
            except (urllib.error.URLError, urllib.error.HTTPError) as exc:
                if discovery_gaps is not None:
                    discovery_gaps.append({"venue": "www", "source": "official-accepted-research-index", "failure": type(exc).__name__})
            candidates.extend(corpus_index_candidates(venue, year, target_per_venue))
    candidates = merge_candidates(candidates)
    if resolve_preprints:
        candidates = resolve_title_exact_public_fulltext(candidates, target_per_venue, timeout, rate_limit, cache_path=resolver_cache, max_queries=max_search_queries, force_refresh=force_refresh_cache)
    return candidates


def summarize(rows: list[dict[str, Any]], venues: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for venue in venues:
        selected = [row for row in rows if row.get("venue") == venue]
        summary[venue] = {
            "sources": len(selected),
            "eligible": sum(row.get("eligibility") == "style-evidence" for row in selected),
            "holdout": sum(row.get("eligibility") == "holdout" for row in selected),
            "download_errors": sum(row.get("collection_status") == "download-error" for row in selected),
        }
    return summary


def preserved_manifest_rows(output: Path, venues: list[str], year: int) -> list[dict[str, Any]]:
    """Do not erase other venue provenance during a targeted collection run."""
    if not output.is_file():
        return []
    try:
        existing = yaml.safe_load(output.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    return [
        row for row in existing.get("sources", [])
        if row.get("venue") not in venues and int(row.get("year", year)) == year
    ]


def reusable_manifest_rows(output: Path, venues: list[str], year: int) -> list[dict[str, Any]]:
    """Reuse verified target-venue candidates when shrinking or refreshing a window."""
    if not output.is_file():
        return []
    try:
        existing = yaml.safe_load(output.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return []
    return [
        row for row in existing.get("sources", [])
        if row.get("venue") in venues
        and int(row.get("year", year)) == year
        and row.get("eligibility") == "style-evidence"
        and row.get("public_url")
        and row.get("relative_path")
    ]


def collect(
    corpus_root: Path,
    output: Path,
    venues: list[str],
    year: int = 2026,
    target_per_venue: int = 30,
    dry_run: bool = False,
    refresh: bool = False,
    timeout: int = 60,
    rate_limit: float = 2.0,
    resolve_preprints: bool = True,
    resolver_cache: Path | None = None,
    max_search_queries: int | None = None,
    force_refresh_cache: bool = False,
    candidates: list[dict[str, Any]] | None = None,
    candidate_seed: Path | None = None,
) -> dict[str, Any]:
    discovery_gaps: list[dict[str, str]] = []
    seed_candidates = load_candidate_seed(candidate_seed, venues, year)
    candidates = candidates if candidates is not None else discover_candidates(venues, year, target_per_venue, timeout, rate_limit, resolve_preprints and not dry_run, resolver_cache=resolver_cache, max_search_queries=max_search_queries, force_refresh_cache=force_refresh_cache, discovery_gaps=discovery_gaps, seed_candidates=seed_candidates)
    if not dry_run:
        candidates = merge_candidates(candidates + reusable_manifest_rows(output, venues, year))
    candidates = limit_candidates_per_venue(candidates, corpus_root, target_per_venue)
    rows: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate["venue"] not in venues:
            continue
        if dry_run:
            rows.append(dry_run_row(candidate))
            continue
        if not candidate.get("public_url"):
            relative = candidate.get("relative_path")
            if relative and (corpus_root / str(relative)).is_file():
                row = dict(candidate)
                target = corpus_root / str(relative)
                row["collection_status"] = "existing"
                row["sha256"] = sha256(target)
                row["bytes"] = target.stat().st_size
                row["eligibility"], row["verification_status"], notes = verify_pdf_for_candidate(target, candidate)
                if notes:
                    row["notes"] = notes
                rows.append(row)
            else:
                rows.append(dry_run_row(candidate))
                rows[-1]["collection_status"] = "holdout-no-public-fulltext"
            continue
        rows.append(collect_pdf(candidate, corpus_root, timeout, refresh, USER_AGENT))
        time.sleep(rate_limit)
    rows = dedupe_rows(rows)
    if not dry_run:
        rows.extend(preserved_manifest_rows(output, venues, year))
    manifest = {
        "schema_version": 2,
        "generated": date.today().isoformat(),
        "target": {"year": year, "venues": venues, "target_per_venue": target_per_venue},
        "source_policy": {
            "public_only": True,
            "raw_pdfs_outside_skill_repository": True,
            "raw_text_retained": False,
            "raw_images_retained": False,
            "www_acm_restricted_pdf_excluded": True,
            "accepted_title_index_is_the_only_candidate_source": True,
            "public_preprints_are_style_evidence_not_format_policy": True,
            "official_source_priority": ["openreview", "icml-virtual", "pmlr", "arxiv-title-exact"],
            "resolver_cache_is_external_and_ttl_bound": True,
        },
        "summary": summarize(rows, sorted(set(venues) | {str(row.get("venue")) for row in rows if row.get("venue")})),
        "discovery_gaps": discovery_gaps,
        "sources": rows,
    }
    if not dry_run:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", required=True, type=Path)
    parser.add_argument("--output", type=Path, default=ROOT / "evidence" / "derived" / "visual-style-source-manifest.yaml")
    parser.add_argument("--year", type=int, default=2026)
    parser.add_argument("--target-per-venue", type=int, default=30)
    parser.add_argument("--venues", default="www,iclr,icml")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--rate-limit-seconds", type=float, default=2.0)
    parser.add_argument("--no-resolve-preprints", action="store_true", help="Do not query arXiv for exact-title public PDFs across venues")
    parser.add_argument("--no-resolve-www", action="store_true", help="Deprecated alias for --no-resolve-preprints")
    parser.add_argument("--resolver-cache", type=Path, help="External cache for arXiv exact-title resolution")
    parser.add_argument("--max-search-queries", type=int, help="Limit arXiv title queries for a collection run")
    parser.add_argument("--refresh-resolver-cache", action="store_true", help="Ignore non-expired arXiv resolver cache entries")
    parser.add_argument("--candidate-seed", type=Path, help="External accepted-title seed captured from an official public venue page")
    args = parser.parse_args()
    venues = [item.strip().lower() for item in args.venues.split(",") if item.strip()]
    invalid = sorted(set(venues) - set(VENUE_CONFERENCES))
    if invalid:
        parser.error(f"unsupported venues: {', '.join(invalid)}")
    manifest = collect(
        corpus_root=args.corpus_root.resolve(),
        output=args.output.resolve(),
        venues=venues,
        year=args.year,
        target_per_venue=args.target_per_venue,
        dry_run=args.dry_run,
        refresh=args.refresh,
        timeout=args.timeout,
        rate_limit=args.rate_limit_seconds,
        resolve_preprints=not (args.no_resolve_preprints or args.no_resolve_www),
        resolver_cache=args.resolver_cache.resolve() if args.resolver_cache else args.corpus_root.resolve() / "sources" / "visual-style-resolver-cache.json",
        max_search_queries=args.max_search_queries,
        force_refresh_cache=args.refresh_resolver_cache or args.refresh,
        candidate_seed=args.candidate_seed.resolve() if args.candidate_seed else None,
    )
    print(json.dumps({"dry_run": args.dry_run, "output": str(args.output), "summary": manifest["summary"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
