#!/usr/bin/env python3
"""Check a top-cs-figure export bundle for expected files and basic SVG/PNG/PDF traits."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from top_cs_figure_core.color import oklab_distance, relative_luminance, rgb_to_oklab, simulate_cvd


DEFAULT_FORMATS = ("svg", "pdf", "png")


def _signature(path: Path) -> str:
    try:
        return path.read_bytes()[:16].hex()
    except OSError:
        return ""


def _luminance(hex_color: str) -> float:
    return relative_luminance(hex_color)


def _rgb(hex_color: str) -> tuple[float, float, float]:
    value = hex_color.lstrip("#")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (0, 2, 4))  # type: ignore[return-value]


def _cvd_distance(left: str, right: str, kind: str) -> float:
    return oklab_distance(simulate_cvd(left, kind), simulate_cvd(right, kind))


def _palette_profile_findings(resolution: dict) -> list[str]:
    colors = [str(color) for color in resolution.get("colors") or []]
    family = resolution.get("family")
    findings: list[str] = []
    accessibility = resolution.get("accessibility") or {}
    violations = accessibility.get("violations") or {}
    if violations.get("large_fill"):
        findings.append(f"{family} palette has low-contrast fill colors: {', '.join(violations['large_fill'])}")
    if family in {"semantic", "categorical"}:
        for pair in accessibility.get("pairs") or []:
            if pair.get("oklab_distance", 1) < 0.08 or min((pair.get("cvd_distance") or {"none": 1}).values()) < 0.05:
                findings.append(f"{family} palette has indistinguishable pair: {pair.get('left')}/{pair.get('right')}")
    if family in {"ordered", "sequential"} and len(colors) > 2:
        luminance = [_luminance(color) for color in colors]
        direction = 1 if luminance[-1] > luminance[0] else -1
        if any(direction * (right - left) <= 0.005 for left, right in zip(luminance, luminance[1:])):
            findings.append(f"{family} palette is not luminance-monotonic")
    if family == "diverging" and len(colors) >= 3:
        lightness, a, b = rgb_to_oklab(_rgb(colors[len(colors) // 2]))
        if math.sqrt(a * a + b * b) > 0.035 or not 0.72 <= lightness <= 0.98:
            findings.append("diverging palette center is not a light neutral")
    return findings


def _analyze_svg(path: Path, expected_panels: Iterable[str] = (), expected_colors: Iterable[str] = (), expected_text: Iterable[str] = (), metric_direction: str | None = None, require_editable_text: bool = True) -> dict:
    text = path.read_text(encoding="utf-8", errors="ignore")
    try:
        root = ET.fromstring(text)
        parse_error = None
    except ET.ParseError as exc:
        root, parse_error = None, str(exc)
    elements = list(root.iter()) if root is not None else []
    text_nodes = [element for element in elements if element.tag.rsplit("}", 1)[-1] == "text"]
    svg_text = ["".join(element.itertext()).strip() for element in text_nodes]
    has_text = bool(text_nodes)
    warnings = [] if has_text or not require_editable_text else ["svg has no <text> nodes; text may be outlined or absent"]
    lower = text.lower()
    panels_missing = [label for label in expected_panels if label not in svg_text]
    colors_missing = [color for color in expected_colors if color.lower() not in lower]
    text_missing = [value for value in expected_text if value not in text]
    normalized = re.sub(r"[^a-z]", "", text.lower())
    direction_missing = bool(metric_direction) and re.sub(r"[^a-z]", "", metric_direction.lower()) not in normalized
    color_values = [color.lower() for color in expected_colors if re.fullmatch(r"#[0-9a-fA-F]{6}", color)]
    grayscale_collisions = [f"{left}/{right}" for index, left in enumerate(color_values) for right in color_values[index + 1 :] if abs(_luminance(left) - _luminance(right)) < 0.045]
    warnings.extend(f"panel label not found in svg text: {label}" for label in panels_missing)
    warnings.extend(f"expected color not found in svg: {color}" for color in colors_missing)
    warnings.extend(f"expected SVG text not found: {value}" for value in text_missing)
    if direction_missing:
        warnings.append(f"metric direction not found in SVG text: {metric_direction}")
    warnings.extend(f"low grayscale separation between expected colors: {pair}" for pair in grayscale_collisions)
    ids = [element.attrib["id"] for element in elements if element.attrib.get("id")]
    duplicate_ids = sorted(value for value, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        warnings.append(f"duplicate SVG ids: {', '.join(duplicate_ids[:8])}")
    viewbox = root.attrib.get("viewBox") if root is not None else None
    if not viewbox:
        warnings.append("SVG viewBox is missing")
    font_sizes = [float(value) for value in re.findall(r"font-size:\s*([0-9.]+)px", text)]
    if font_sizes and min(font_sizes) < 6:
        warnings.append(f"SVG contains text below 6 pt: {min(font_sizes):.2f} pt")
    cvd_collisions = []
    for index, left in enumerate(color_values):
        for right in color_values[index + 1:]:
            failed = [kind for kind in ("protan", "deutan", "tritan") if _cvd_distance(left, right, kind) < 0.12]
            if failed:
                cvd_collisions.append(f"{left}/{right}:{','.join(failed)}")
    warnings.extend(f"low color-vision separation: {pair}" for pair in cvd_collisions)
    return {
        "has_text_nodes": has_text,
        "has_svg_root": "<svg" in text[:500].lower(),
        "has_font_declaration": "font-family" in lower or "font:" in lower,
        "panel_labels_missing": panels_missing,
        "expected_colors_missing": colors_missing,
        "expected_text_missing": text_missing,
        "metric_direction_missing": direction_missing,
        "grayscale_collisions": grayscale_collisions,
        "cvd_collisions": cvd_collisions,
        "viewbox": viewbox,
        "duplicate_ids": duplicate_ids,
        "text_node_count": len(text_nodes),
        "minimum_text_pt": round(min(font_sizes), 3) if font_sizes else None,
        "parse_error": parse_error,
        "warnings": warnings,
    }


def _analyze_binary(path: Path, fmt: str) -> dict:
    sig = _signature(path)
    warnings: list[str] = []
    if fmt == "pdf" and not sig.startswith("25504446"):
        warnings.append("pdf signature not detected")
    if fmt == "png" and not sig.startswith("89504e470d0a1a0a"):
        warnings.append("png signature not detected")
    if fmt in {"tif", "tiff"} and not (sig.startswith("49492a00") or sig.startswith("4d4d002a")):
        warnings.append("tiff signature not detected")
    details = {"signature": sig, "warnings": warnings}
    if fmt == "png":
        try:
            from PIL import Image, ImageChops

            with Image.open(path) as image:
                rgb = image.convert("RGB")
                background = Image.new("RGB", rgb.size, "white")
                bbox = ImageChops.difference(rgb, background).getbbox()
                dpi = image.info.get("dpi")
                details.update({
                    "pixel_size": list(image.size),
                    "dpi": [round(float(value), 2) for value in dpi] if dpi else None,
                    "nonblank": bbox is not None,
                    "content_bbox": list(bbox) if bbox else None,
                    "content_touches_edge": bool(bbox and (bbox[0] == 0 or bbox[1] == 0 or bbox[2] == image.size[0] or bbox[3] == image.size[1])),
                })
                if bbox is None:
                    warnings.append("png appears blank")
                if dpi and min(dpi) < 250:
                    warnings.append("png DPI is below 250")
        except Exception:
            details["pixel_inspection"] = "unavailable"
    if fmt == "pdf":
        try:
            import fitz

            document = fitz.open(path)
            if document:
                rect = document[0].rect
                details["page_count"] = len(document)
                details["page_size_points"] = [round(rect.width, 2), round(rect.height, 2)]
                details["page_size_mm"] = [round(rect.width * 25.4 / 72, 2), round(rect.height * 25.4 / 72, 2)]
                fonts = document[0].get_fonts(full=True)
                details["embedded_font_count"] = len(fonts)
                if not fonts:
                    warnings.append("PDF has no detectable embedded fonts")
            document.close()
        except Exception:
            details["page_inspection"] = "unavailable"
    return details


def inspect_bundle(
    base: Path,
    formats: Iterable[str] = DEFAULT_FORMATS,
    script: Path | None = None,
    source_data: Path | None = None,
    expected_panels: Iterable[str] = (),
    expected_colors: Iterable[str] = (),
    expected_text: Iterable[str] = (),
    metric_direction: str | None = None,
    caption: str | None = None,
    callout: str | None = None,
    require_editable_text: bool = True,
) -> dict:
    base = base.with_suffix("") if base.suffix else base
    files = []
    missing = []
    warnings = []
    for fmt in formats:
        fmt = fmt.lower().lstrip(".")
        path = base.with_suffix("." + fmt)
        entry = {"format": fmt, "path": str(path), "exists": path.is_file(), "bytes": path.stat().st_size if path.is_file() else 0}
        if not path.is_file():
            missing.append(str(path))
        elif path.stat().st_size == 0:
            warnings.append(f"{path} is empty")
        elif fmt == "svg":
            details = _analyze_svg(path, expected_panels=expected_panels, expected_colors=expected_colors, expected_text=expected_text, metric_direction=metric_direction, require_editable_text=require_editable_text)
            entry.update(details)
            warnings.extend(f"{path}: {item}" for item in details["warnings"])
        elif fmt in {"pdf", "png", "tif", "tiff"}:
            details = _analyze_binary(path, fmt)
            entry.update(details)
            warnings.extend(f"{path}: {item}" for item in details["warnings"])
        files.append(entry)
    extras = {}
    if script is not None:
        extras["script_exists"] = script.is_file()
        if not script.is_file():
            warnings.append(f"plotting script missing: {script}")
    if source_data is not None:
        extras["source_data_exists"] = source_data.is_file()
        if not source_data.is_file():
            warnings.append(f"source data missing: {source_data}")
    expected_panels = list(expected_panels)
    expected_colors = list(expected_colors)
    render_path = base.with_name(base.name + ".render.json")
    if render_path.is_file():
        render_manifest = json.loads(render_path.read_text(encoding="utf-8"))
        extras["render_manifest"] = str(render_path)
        geometry = render_manifest.get("geometry") or {}
        extras["geometry"] = geometry
        for panel_id, panel_geometry in (geometry.get("panels") or {}).items():
            if not panel_geometry.get("inside_canvas", True):
                warnings.append(f"panel {panel_id} extends outside the canvas")
            font_sizes = [item.get("font_pt", 99) for item in panel_geometry.get("texts", [])]
            if font_sizes and min(font_sizes) < 6:
                warnings.append(f"panel {panel_id} contains text below 6 pt")
            thin = [value for value in panel_geometry.get("line_widths_pt", []) if 0 < value < 0.6]
            if thin:
                warnings.append(f"panel {panel_id} contains line widths below 0.6 pt")
            if panel_geometry.get("text_overlaps"):
                warnings.append(f"panel {panel_id} has overlapping text labels")
            if panel_geometry.get("legend_text_overlaps"):
                warnings.append(f"panel {panel_id} legend overlaps labels")
            if panel_geometry.get("panel_label_title_overlap"):
                warnings.append(f"panel {panel_id} panel label overlaps title")
            if panel_geometry.get("uncertainty_clipped"):
                warnings.append(f"panel {panel_id} clips an uncertainty interval")
        obligations = [item for panel in render_manifest.get("panels", []) for item in panel.get("caption_obligations", [])]
        extras["caption_obligations"] = obligations
        used_styles = [style for panel in render_manifest.get("panels", []) for style in (panel.get("semantic_styles") or {}).values()]
        used_colors = sorted({str(style.get("color", "")).lower() for style in used_styles if re.fullmatch(r"#[0-9a-fA-F]{6}", str(style.get("color", "")))})
        extras["used_semantic_colors"] = used_colors
        palette_resolution = render_manifest.get("palette_resolution") or {}
        extras["palette_resolution"] = palette_resolution
        palette_findings = []
        for panel_id, resolution in (palette_resolution.get("panels") or {}).items():
            inspected = dict(resolution)
            if inspected.get("family") in {"semantic", "categorical"} and used_colors:
                inspected["colors"] = used_colors
                inspected["accessibility"] = {
                    **(inspected.get("accessibility") or {}),
                    "pairs": [pair for pair in (inspected.get("accessibility") or {}).get("pairs", []) if pair.get("left", "").lower() in used_colors and pair.get("right", "").lower() in used_colors],
                    "violations": {key: [color for color in values if color.lower() in used_colors] for key, values in ((inspected.get("accessibility") or {}).get("violations") or {}).items()},
                }
            palette_findings.extend(f"panel {panel_id}: {finding}" for finding in _palette_profile_findings(inspected))
        extras["palette_findings"] = palette_findings
        warnings.extend(palette_findings)
        svg_path = base.with_suffix(".svg")
        if svg_path.is_file():
            svg_content = svg_path.read_text(encoding="utf-8", errors="ignore").lower()
            for color in used_colors:
                if color not in svg_content:
                    warnings.append(f"render-manifest semantic color absent from SVG: {color}")
        noncolor_signatures = {(str(style.get("marker")), str(style.get("linestyle")), str(style.get("hatch"))) for style in used_styles}
        collisions = []
        for index, left in enumerate(used_colors):
            for right in used_colors[index + 1:]:
                if abs(_luminance(left) - _luminance(right)) < 0.045 or any(_cvd_distance(left, right, mode) < 0.12 for mode in ("protan", "deutan", "tritan")):
                    collisions.append(f"{left}/{right}")
        extras["semantic_color_collisions"] = collisions
        if collisions and len(noncolor_signatures) < len(used_colors):
            warnings.append("semantic colors collide under grayscale/CVD without complete non-color redundancy")
        expected_width, expected_height = geometry.get("width_mm"), geometry.get("height_mm")
        for entry in files:
            if entry["format"] == "pdf" and entry.get("page_size_mm") and expected_width and expected_height:
                if max(abs(entry["page_size_mm"][0] - expected_width), abs(entry["page_size_mm"][1] - expected_height)) > 0.5:
                    warnings.append("PDF dimensions differ from render-manifest dimensions")
            if entry["format"] == "png" and entry.get("pixel_size") and entry.get("dpi") and expected_width and expected_height:
                actual_mm = [entry["pixel_size"][0] / entry["dpi"][0] * 25.4, entry["pixel_size"][1] / entry["dpi"][1] * 25.4]
                if max(abs(actual_mm[0] - expected_width), abs(actual_mm[1] - expected_height)) > 0.75:
                    warnings.append("PNG dimensions differ from render-manifest dimensions")
        if obligations and caption is None:
            warnings.append("caption text was not supplied for caption-obligation QA")
        if caption is not None:
            for obligation in obligations:
                token = obligation.get("token") if isinstance(obligation, dict) else str(obligation)
                if token and token.lower() not in caption.lower():
                    warnings.append(f"caption obligation not covered: {token}")
    if caption is not None:
        extras["caption_present"] = bool(caption.strip())
        if not caption.strip():
            warnings.append("caption is empty")
        for label in expected_panels:
            if label and label not in caption:
                warnings.append(f"caption does not mention panel label: {label}")
    if callout is not None:
        extras["callout_present"] = bool(callout.strip())
        if not callout.strip():
            warnings.append("manuscript callout is empty")
    return {
        "base": str(base),
        "passed": not missing and not warnings,
        "missing": missing,
        "warnings": warnings,
        "files": files,
        **extras,
    }


def text_report(result: dict) -> str:
    lines = [f"base: {result['base']}", f"passed: {result['passed']}"]
    if result["missing"]:
        lines.append("missing:")
        lines.extend(f"- {item}" for item in result["missing"])
    if result["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {item}" for item in result["warnings"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, type=Path, help="Figure base path without extension")
    parser.add_argument("--format", choices=("json", "text"), default="text")
    parser.add_argument("--require-format", action="append", default=[], help="Additional required format such as tiff")
    parser.add_argument("--script", type=Path, help="Optional plotting script to verify")
    parser.add_argument("--source-data", type=Path, help="Optional source data file to verify")
    parser.add_argument("--expect-panel", action="append", default=[], help="Panel label expected in editable SVG text and caption")
    parser.add_argument("--expect-color", action="append", default=[], help="Hex color expected in the SVG")
    parser.add_argument("--expect-text", action="append", default=[], help="Expected editable SVG text such as an axis or legend label")
    parser.add_argument("--metric-direction", help="Expected direction text such as higher-is-better")
    parser.add_argument("--caption", help="Caption text to check for panel mapping")
    parser.add_argument("--callout", help="Manuscript callout text to check for presence")
    parser.add_argument("--no-require-editable-text", action="store_true", help="Do not fail when SVG text is outlined")
    args = parser.parse_args()
    formats = list(DEFAULT_FORMATS)
    for fmt in args.require_format:
        if fmt not in formats:
            formats.append(fmt)
    result = inspect_bundle(
        args.base,
        formats=formats,
        script=args.script,
        source_data=args.source_data,
        expected_panels=args.expect_panel,
        expected_colors=args.expect_color,
        expected_text=args.expect_text,
        metric_direction=args.metric_direction,
        caption=args.caption,
        callout=args.callout,
        require_editable_text=not args.no_require_editable_text,
    )
    print(json.dumps(result, indent=2) if args.format == "json" else text_report(result))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
