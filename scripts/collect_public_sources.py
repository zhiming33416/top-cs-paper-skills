#!/usr/bin/env python3
"""Collect configured public sources into an external cache with provenance.

The collector never writes into a skill directory unless that directory is
explicitly passed as --cache-root. OpenReview bulk queries remain index entries
until a concrete public query URL is supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Any

import yaml


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_config(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("sources"), list):
        raise ValueError("unsupported collection config")
    ids = [item.get("source_id") for item in data["sources"]]
    targets = [item.get("relative_path") for item in data["sources"]]
    if len(ids) != len(set(ids)) or len(targets) != len(set(targets)):
        raise ValueError("source_id and relative_path must be unique")
    for item in data["sources"]:
        if not str(item.get("url", "")).startswith("https://"):
            raise ValueError(f"only HTTPS public sources are allowed: {item.get('source_id')}")
        target = Path(str(item.get("relative_path", "")))
        if target.is_absolute() or ".." in target.parts:
            raise ValueError(f"unsafe relative_path: {target}")
    return data


def existing_record(item: dict[str, Any], target: Path) -> dict[str, Any]:
    return {
        "source_id": item["source_id"],
        "status": "existing",
        "relative_path": item["relative_path"],
        "url": item["url"],
        "sha256": digest(target),
        "bytes": target.stat().st_size,
        "accessed": date.today().isoformat(),
        "license": item.get("license", "unspecified"),
        "version_status": item.get("version_status", "unspecified"),
        "public": True,
    }


def collect_one(item: dict[str, Any], cache_root: Path, user_agent: str, timeout: int, refresh: bool) -> dict[str, Any]:
    target = cache_root / item["relative_path"]
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and not refresh:
        return existing_record(item, target)
    partial = target.with_suffix(target.suffix + ".part")
    headers = {"User-Agent": user_agent}
    mode = "wb"
    if partial.is_file() and partial.stat().st_size:
        headers["Range"] = f"bytes={partial.stat().st_size}-"
        mode = "ab"
    request = urllib.request.Request(item["url"], headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if mode == "ab" and response.status != 206:
                mode = "wb"
            with partial.open(mode) as handle:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    handle.write(chunk)
        partial.replace(target)
    except urllib.error.HTTPError as exc:
        return {"source_id": item["source_id"], "status": "http-error", "detail": str(exc)}
    return {
        "source_id": item["source_id"],
        "status": "collected",
        "relative_path": item["relative_path"],
        "url": item["url"],
        "sha256": digest(target),
        "bytes": target.stat().st_size,
        "accessed": date.today().isoformat(),
        "license": item.get("license", "unspecified"),
        "version_status": item.get("version_status", "unspecified"),
        "public": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--cache-root", required=True, type=Path)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rate-limit-seconds", type=float)
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--refresh", action="store_true", help="Re-download existing files to detect policy changes")
    args = parser.parse_args()
    config = load_config(args.config)
    policy = config.get("collection_policy", {})
    rate = args.rate_limit_seconds
    if rate is None:
        rate = float(policy.get("default_rate_limit_seconds", 2.0))
    if rate < 0:
        parser.error("rate limit must be non-negative")
    cache_root = args.cache_root.expanduser().resolve()
    rows = []
    for item in config["sources"]:
        if item.get("collect") is False:
            rows.append({
                "source_id": item["source_id"],
                "status": "manual-query-required",
                "url": item["url"],
                "target": item["relative_path"],
                "note": item.get("note"),
            })
            continue
        if args.dry_run:
            rows.append({
                "source_id": item["source_id"],
                "status": "would-collect",
                "url": item["url"],
                "target": item["relative_path"],
            })
            continue
        rows.append(collect_one(item, cache_root, policy.get("user_agent", "top-cs-paper-skills/1.0"), args.timeout, args.refresh))
        time.sleep(rate)
    by_hash: dict[str, str] = {}
    for row in rows:
        value = row.get("sha256")
        if not value:
            continue
        if value in by_hash:
            row["duplicate_of"] = by_hash[value]
        else:
            by_hash[value] = row["source_id"]
    result = {"schema_version": 1, "dry_run": args.dry_run, "cache_root": str(cache_root), "sources": rows}
    if not args.dry_run:
        (cache_root / "collection-manifest.yaml").write_text(
            yaml.safe_dump(result, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if any(row["status"].endswith("error") for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
