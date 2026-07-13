#!/usr/bin/env python3
"""Run external figure regressions and emit aggregate-only, anonymized results."""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
from pathlib import Path
from typing import Any

import yaml
from PIL import Image

from render_from_figure_spec import render


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def dhash(path: Path) -> str:
    with Image.open(path) as image:
        grayscale = image.convert("L").resize((9, 8), Image.Resampling.LANCZOS)
        pixels = list(grayscale.get_flattened_data() if hasattr(grayscale, "get_flattened_data") else grayscale.getdata())
    bits = 0
    for row in range(8):
        for column in range(8):
            bits = (bits << 1) | int(pixels[row * 9 + column] > pixels[row * 9 + column + 1])
    return f"{bits:016x}"


def hamming(left: str, right: str) -> int:
    return (int(left, 16) ^ int(right, 16)).bit_count()


def validate_suite(document: dict[str, Any]) -> None:
    allowed = {"schema_version", "suite_id", "privacy", "cases"}
    if set(document) - allowed or document.get("schema_version") != 1:
        raise ValueError("unsupported or unknown regression suite fields")
    privacy = document.get("privacy") or {}
    if privacy != {"anonymized": True, "retain_rendered_artifacts": False, "include_source_paths_in_report": False}:
        raise ValueError("private regressions require strict aggregate-only privacy settings")
    ids: set[str] = set()
    for case in document.get("cases") or []:
        unknown = set(case) - {"id", "spec", "expected_panels", "expected_formats", "baseline", "thresholds"}
        if unknown:
            raise ValueError(f"unknown case fields: {', '.join(sorted(unknown))}")
        if not case.get("id") or case["id"] in ids:
            raise ValueError("regression case ids must be present and unique")
        ids.add(case["id"])


def geometry_metrics(result: dict[str, Any]) -> dict[str, Any]:
    panels = result["geometry"]["panels"]
    text = [item["font_pt"] for panel in panels.values() for item in panel["texts"]]
    lines = [value for panel in panels.values() for value in panel["line_widths_pt"] if value > 0]
    return {
        "width_mm": float(result["geometry"]["width_mm"]),
        "height_mm": float(result["geometry"]["height_mm"]),
        "minimum_text_pt": float(min(text)) if text else None,
        "minimum_line_width_pt": float(min(lines)) if lines else None,
        "overlap_count": sum(len(panel["text_overlaps"]) for panel in panels.values()),
        "all_panels_inside_canvas": all(panel["inside_canvas"] for panel in panels.values()),
        "uncertainty_clipped": any(panel["uncertainty_clipped"] for panel in panels.values()),
    }


def run(suite_path: Path) -> dict[str, Any]:
    suite_path = suite_path.resolve()
    document = yaml.safe_load(suite_path.read_text(encoding="utf-8"))
    validate_suite(document)
    reports = []
    with tempfile.TemporaryDirectory(prefix="top-cs-figure-private-") as temporary:
        output_root = Path(temporary)
        for case in document["cases"]:
            spec_path = (suite_path.parent / case["spec"]).resolve()
            spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
            result = render(spec, spec_path, output_root / case["id"])
            base = Path(result["base"])
            current_hash = dhash(base.with_suffix(".png"))
            baseline = case.get("baseline") or {}
            distance = hamming(current_hash, baseline["png_dhash"]) if baseline.get("png_dhash") else None
            metrics = geometry_metrics(result)
            thresholds = case["thresholds"]
            findings = []
            if len(result["panels"]) != int(case["expected_panels"]):
                findings.append("panel-count")
            for fmt in case["expected_formats"]:
                if not base.with_suffix(f".{fmt}").is_file():
                    findings.append(f"missing-{fmt}")
            if distance is not None and distance > int(thresholds["max_dhash_distance"]):
                findings.append("visual-distance")
            if metrics["minimum_text_pt"] is not None and metrics["minimum_text_pt"] < float(thresholds["minimum_text_pt"]):
                findings.append("minimum-text")
            if metrics["minimum_line_width_pt"] is not None and metrics["minimum_line_width_pt"] < float(thresholds["minimum_line_width_pt"]):
                findings.append("minimum-line-width")
            if not metrics["all_panels_inside_canvas"]:
                findings.append("canvas-overflow")
            if metrics["uncertainty_clipped"]:
                findings.append("uncertainty-clipped")
            panel_ids = [panel["panel_id"] for panel in result["panels"]]
            if baseline.get("panel_ids") is not None and panel_ids != baseline["panel_ids"]:
                findings.append("panel-id-change")
            if baseline.get("normalized_spec_sha256") and result["normalized_spec_hash"] != baseline["normalized_spec_sha256"]:
                findings.append("normalized-spec-change")
            reports.append({
                "id": case["id"],
                "passed": not findings,
                "findings": sorted(set(findings)),
                "spec_sha256": sha256(spec_path),
                "data_sha256": sorted(panel["data_hash"] for panel in result["panels"] if panel.get("data_hash")),
                "normalized_spec_sha256": result["normalized_spec_hash"],
                "png_dhash": current_hash,
                "dhash_distance": distance,
                "panel_ids": panel_ids,
                "geometry": metrics,
            })
    return {
        "schema_version": 1,
        "suite_id": document["suite_id"],
        "aggregate_only": True,
        "passed": sum(case["passed"] for case in reports),
        "failed": sum(not case["passed"] for case in reports),
        "cases": reports,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run(args.suite)
    payload = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
