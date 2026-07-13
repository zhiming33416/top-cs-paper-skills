#!/usr/bin/env python3
"""Create a reproducibility audit and optional visual diff for a figure bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from check_figure_bundle import inspect_bundle


PROJECT_ROOT = SCRIPT_DIR.parents[2]
EVIDENCE_DIR = PROJECT_ROOT / "evidence" / "derived"


def sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def style_evidence_summary(venue: str | None) -> dict[str, Any]:
    path = EVIDENCE_DIR / "visual-style-rules.yaml"
    rules = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {}
    rule = (rules or {}).get("rules", {}).get((venue or "generic").lower(), {})
    status = rule.get("style_status", rule.get("status", "insufficient"))
    palette_status = rule.get("palette_status", "insufficient")
    return {
        "rules_sha256": sha256(path),
        "stats_sha256": sha256(EVIDENCE_DIR / "visual-style-stats.json"),
        "style_status": status,
        "eligible_sources": int(rule.get("eligible_sources", 0)),
        "palette_status": palette_status,
        "anchor_status": rule.get("anchor_status", palette_status),
        "profile_status": rule.get("profile_status", palette_status),
        "palette_fallback_reason": rule.get("palette_fallback_reason"),
        "palette_candidates": list(rule.get("palette_candidates", [])),
        "palette_candidate_support": list(rule.get("palette_candidate_support", [])),
        "palette_profiles": dict(rule.get("palette_profiles", {})),
        "generic_fallback": status != "promoted" or palette_status != "usable",
    }


def resolve_data_sources(spec: dict[str, Any], spec_path: Path) -> list[Path]:
    sources = list(spec.get("data_sources") or [])
    for panel in spec.get("panels") or []:
        if panel.get("data_source"):
            sources.append(panel["data_source"])
    unique: list[Path] = []
    for source in sources:
        if isinstance(source, dict):
            source = source.get("path")
        if not source:
            continue
        path = Path(str(source))
        path = path if path.is_absolute() else (spec_path.parent / path).resolve()
        if path not in unique:
            unique.append(path)
    return unique


def expected_panels(spec: dict[str, Any]) -> list[str]:
    if spec.get("panels"):
        return [str(panel["panel_id"]) for panel in spec["panels"]]
    panel_map = spec.get("panel_map") or [{}]
    return [str(panel_map[0].get("panel_id", "a"))]


def svg_features(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        return {"text": [], "colors": [], "panel_labels": []}
    content = path.read_text(encoding="utf-8", errors="ignore")
    text = re.findall(r"<text[^>]*>(.*?)</text>", content, flags=re.DOTALL)
    text = [re.sub(r"<[^>]+>", "", item).strip() for item in text if item.strip()]
    colors = sorted(set(re.findall(r"#[0-9a-fA-F]{6}\b", content)))
    panels = [item for item in text if re.fullmatch(r"[a-z]", item)]
    return {"text": sorted(set(text)), "colors": colors, "panel_labels": sorted(set(panels))}


def png_difference(previous: Path, current: Path) -> dict[str, Any]:
    if not previous.is_file() or not current.is_file():
        return {"available": False}
    try:
        from PIL import Image, ImageChops, ImageStat
    except ImportError:
        return {"available": False, "reason": "Pillow unavailable"}
    with Image.open(previous).convert("RGB") as before, Image.open(current).convert("RGB") as after:
        if before.size != after.size:
            return {"available": True, "same_size": False, "before_size": before.size, "after_size": after.size}
        difference = ImageChops.difference(before, after)
        stat = ImageStat.Stat(difference)
        mean_delta = round(sum(stat.mean) / len(stat.mean), 3)
        pixels = difference.get_flattened_data() if hasattr(difference, "get_flattened_data") else difference.getdata()
        changed = sum(1 for pixel in pixels if max(pixel) > 8)
        return {
            "available": True,
            "same_size": True,
            "size": before.size,
            "mean_channel_delta": mean_delta,
            "changed_pixel_fraction": round(changed / (before.size[0] * before.size[1]), 5),
        }


def bundle_diff(previous_base: Path, current_base: Path) -> dict[str, Any]:
    previous_base = previous_base.with_suffix("") if previous_base.suffix else previous_base
    current_base = current_base.with_suffix("") if current_base.suffix else current_base
    before = svg_features(previous_base.with_suffix(".svg"))
    after = svg_features(current_base.with_suffix(".svg"))
    def load_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}

    before_render = load_json(previous_base.with_name(previous_base.name + ".render.json"))
    after_render = load_json(current_base.with_name(current_base.name + ".render.json"))
    before_panels = {item.get("panel_id"): item for item in before_render.get("panels", [])}
    after_panels = {item.get("panel_id"): item for item in after_render.get("panels", [])}
    panel_diff = {}
    for panel_id in sorted(set(before_panels) | set(after_panels)):
        left, right = before_panels.get(panel_id, {}), after_panels.get(panel_id, {})
        changed = {}
        for key in ("variant", "transforms", "statistics", "data_hash", "plotted_data_hash", "caption_obligations"):
            if left.get(key) != right.get(key):
                changed[key] = {"before": left.get(key), "after": right.get(key)}
        if changed:
            panel_diff[str(panel_id)] = changed
    before_spec_path = Path(str(before_render.get("normalized_spec", "")))
    after_spec_path = Path(str(after_render.get("normalized_spec", "")))
    before_spec = yaml.safe_load(before_spec_path.read_text(encoding="utf-8")) if before_spec_path.is_file() else {}
    after_spec = yaml.safe_load(after_spec_path.read_text(encoding="utf-8")) if after_spec_path.is_file() else {}
    spec_sections = {}
    for key in ("layout", "shared_guides", "accessibility", "reproducibility"):
        if (before_spec or {}).get(key) != (after_spec or {}).get(key):
            spec_sections[key] = {"before": (before_spec or {}).get(key), "after": (after_spec or {}).get(key)}
    return {
        "scientific_claims_compared": False,
        "svg": {
            "added_text": sorted(set(after["text"]) - set(before["text"])),
            "removed_text": sorted(set(before["text"]) - set(after["text"])),
            "added_colors": sorted(set(after["colors"]) - set(before["colors"])),
            "removed_colors": sorted(set(before["colors"]) - set(after["colors"])),
            "added_panel_labels": sorted(set(after["panel_labels"]) - set(before["panel_labels"])),
            "removed_panel_labels": sorted(set(before["panel_labels"]) - set(after["panel_labels"])),
        },
        "png": png_difference(previous_base.with_suffix(".png"), current_base.with_suffix(".png")),
        "render_manifest": {
            "available": bool(before_render and after_render),
            "normalized_spec_hash_changed": before_render.get("normalized_spec_hash") != after_render.get("normalized_spec_hash"),
            "panels": panel_diff,
            "spec_sections": spec_sections,
        },
    }


def audit(spec_path: Path, base: Path, output: Path | None = None, compare_to: Path | None = None) -> dict[str, Any]:
    spec_path = spec_path.resolve()
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
    base = base.with_suffix("") if base.suffix else base
    formats = tuple(spec.get("export_formats") or ("svg", "pdf", "png"))
    bundle = inspect_bundle(
        base,
        formats=formats,
        expected_panels=expected_panels(spec),
        caption=spec.get("caption"),
        callout=spec.get("manuscript_callout"),
    )
    data_sources = resolve_data_sources(spec, spec_path)
    missing_sources = [str(path) for path in data_sources if not path.is_file()]
    unresolved = list((spec.get("data_provenance") or {}).get("unresolved_inputs") or [])
    if spec.get("evidence_status") != "available":
        unresolved.append(f"evidence_status={spec.get('evidence_status')}")
    result = {
        "schema_version": 2,
        "figure_id": spec.get("figure_id"),
        "spec_version": int(spec.get("spec_version", 1)),
        "evidence_status": spec.get("evidence_status"),
        "spec_sha256": sha256(spec_path),
        "data_sources": [{"path": str(path), "sha256": sha256(path), "exists": path.is_file()} for path in data_sources],
        "style_evidence": style_evidence_summary(spec.get("venue")),
        "render_manifest": None,
        "bundle": bundle,
        "unresolved_inputs": sorted(set(unresolved + missing_sources)),
        "passed": bundle["passed"] and not missing_sources,
    }
    render_path = base.with_name(base.name + ".render.json")
    if render_path.is_file():
        render_manifest = json.loads(render_path.read_text(encoding="utf-8"))
        result["render_manifest"] = {
            "path": str(render_path),
            "sha256": sha256(render_path),
            "migration": render_manifest.get("migration"),
            "normalized_spec_sha256": render_manifest.get("normalized_spec_hash"),
            "panels": render_manifest.get("panels"),
            "environment": render_manifest.get("environment"),
            "geometry": render_manifest.get("geometry"),
            "palette_resolution": render_manifest.get("palette_resolution"),
        }
    if compare_to is not None:
        result["revision_diff"] = bundle_diff(compare_to, base)
    output = output or base.with_name(base.name + ".figure-audit.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    result["output"] = str(output)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--base", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--compare-to", type=Path, help="Previous figure base path for structural/raster diff")
    args = parser.parse_args()
    result = audit(args.spec, args.base, args.output, args.compare_to)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
