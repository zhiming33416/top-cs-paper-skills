#!/usr/bin/env python3
"""Derive aggregate visual-style evidence from public paper PDFs.

The script stores only hashes, counts, color clusters, and layout labels. It never
writes figure crops, page images, caption text, paper text, or source data.
"""

from __future__ import annotations

import argparse
import colorsys
import hashlib
import json
import math
import random
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import median
from typing import Any, Iterable

import yaml

try:
    import fitz  # type: ignore
except ImportError as exc:  # pragma: no cover - import guard
    raise SystemExit("PyMuPDF is required: pip install pymupdf") from exc


ROOT = Path(__file__).resolve().parents[1]
CONFERENCES = {"www": "WWW2026", "iclr": "ICLR2026", "icml": "ICML2026"}
PROMOTION_MIN_SOURCES = 10
PRELIMINARY_MIN_SOURCES = 3


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def quantize_channel(value: float) -> int:
    return max(0, min(255, int(round(value * 255 / 16) * 16)))


def rgb_to_hex(rgb: tuple[float, float, float]) -> str:
    return "#" + "".join(f"{quantize_channel(channel):02X}" for channel in rgb)


def color_tuple(value: Any) -> tuple[float, float, float] | None:
    if not isinstance(value, (list, tuple)) or len(value) < 3:
        return None
    rgb = tuple(max(0.0, min(1.0, float(channel))) for channel in value[:3])
    if max(rgb) > 0.965 and min(rgb) > 0.965:
        return None
    return rgb  # type: ignore[return-value]


def is_neutral(hex_color: str) -> bool:
    channels = [int(hex_color[i : i + 2], 16) for i in (1, 3, 5)]
    return max(channels) - min(channels) <= 18


def page_raster_colors(page, clip=None, max_side: int = 180, sample_stride: int = 23) -> Counter[str]:
    rect = clip or page.rect
    scale = max_side / max(rect.width, rect.height)
    matrix = fitz.Matrix(scale, scale)
    pix = page.get_pixmap(matrix=matrix, clip=rect, alpha=False)
    data = pix.samples
    counter: Counter[str] = Counter()
    step = max(3, pix.n * sample_stride)
    for index in range(0, len(data) - 2, step):
        r, g, b = data[index], data[index + 1], data[index + 2]
        if r > 246 and g > 246 and b > 246:
            continue
        if r < 18 and g < 18 and b < 18:
            continue
        counter[rgb_to_hex((r / 255, g / 255, b / 255))] += 1
    return counter


def region_raster_summary(page, clip, max_side: int = 180, sample_stride: int = 17) -> tuple[Counter[str], dict[str, Any]]:
    scale = max_side / max(clip.width, clip.height)
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), clip=clip, alpha=False)
    colors: Counter[str] = Counter()
    luminance_bins: Counter[str] = Counter()
    sampled = 0
    colored = 0
    step = max(3, pix.n * sample_stride)
    for index in range(0, len(pix.samples) - 2, step):
        r, g, b = pix.samples[index:index + 3]
        sampled += 1
        luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
        luminance_bins["dark" if luminance < 0.35 else "light" if luminance > 0.72 else "mid"] += 1
        if max(r, g, b) - min(r, g, b) > 18 and not (r > 246 and g > 246 and b > 246):
            colors[rgb_to_hex((r / 255, g / 255, b / 255))] += 1
            colored += 1
    background = max(luminance_bins, key=luminance_bins.get) if luminance_bins else "unknown"
    return colors, {
        "background": background,
        "colored_sample_share": round(colored / max(1, sampled), 3),
        "sample_count": sampled,
    }


def figure_regions(page) -> list[Any]:
    """Infer bounded regions immediately above Figure captions without retaining text."""
    captions: list[tuple[float, float]] = []
    for block in page.get_text("blocks"):
        if len(block) < 5 or not isinstance(block[4], str):
            continue
        if re.search(r"(?i)^\s*(fig(?:ure)?\.?)\s*\d+", block[4]):
            captions.append((float(block[1]), float(block[3])))
    captions.sort()
    regions: list[Any] = []
    previous_bottom = 0.0
    for caption_top, caption_bottom in captions:
        top = max(previous_bottom, caption_top - page.rect.height * 0.58)
        if caption_top - top >= page.rect.height * 0.08:
            regions.append(fitz.Rect(page.rect.x0, top, page.rect.x1, caption_top))
        # Synthetic fixtures and a minority of camera-ready layouts place the
        # caption above the visual; keep a similarly bounded region below it.
        if caption_top < page.rect.height * 0.35:
            bottom = min(page.rect.y1, caption_bottom + page.rect.height * 0.58)
            if bottom - caption_bottom >= page.rect.height * 0.08:
                regions.append(fitz.Rect(page.rect.x0, caption_bottom, page.rect.x1, bottom))
        previous_bottom = caption_bottom
    return regions


def drawing_in_regions(drawing: dict[str, Any], regions: list[Any]) -> bool:
    rect = drawing.get("rect")
    return bool(rect and any(rect.intersects(region) for region in regions))


def palette_chroma(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return colorsys.rgb_to_hsv(*channels)[1]


def palette_hue(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    return colorsys.rgb_to_hsv(*channels)[0]


def palette_family(hex_color: str, bins: int = 12) -> int:
    """Map nearby hues to a circular family so minor export shifts do not split evidence."""
    return int((palette_hue(hex_color) + 0.5 / bins) * bins) % bins


def contrast_on_white(hex_color: str) -> float:
    channels = [int(hex_color[i : i + 2], 16) / 255 for i in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    luminance = 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
    return 1.05 / (luminance + 0.05)


def classify_layout(drawings: int, images: int, captions: int, pages: int, color_count: int) -> list[str]:
    density = drawings / max(1, pages)
    result: list[str] = []
    if images / max(1, pages) >= 2.0:
        result.append("image-heavy")
    if density >= 80 or captions >= 3:
        result.append("quantitative-grid")
    if 12 <= density < 80 and color_count >= 4:
        result.append("mixed")
    if density < 12 and images == 0:
        result.append("sparse-theoretical")
    if color_count >= 6 and captions <= 2 and drawings >= 30:
        result.append("schematic-led-composite")
    return result or ["mixed"]


def classify_figure_context(drawings: int, images: int, color_count: int) -> str:
    if images >= 2:
        return "image-heavy"
    if drawings >= 80 and color_count <= 4:
        return "matrix-or-dense-quantitative"
    if drawings >= 24 and color_count >= 5:
        return "schematic-or-mixed"
    return "quantitative"


def palette_signature(vector: Counter[str], raster: Counter[str], summary: dict[str, Any], drawings: int, images: int) -> dict[str, Any]:
    combined = vector + raster
    non_neutral = Counter({color: count for color, count in combined.items() if not is_neutral(color) and palette_chroma(color) >= 0.2})
    total = sum(non_neutral.values())
    dominant = [
        {"hex": color, "color_family": palette_family(color), "sample_share": round(count / max(1, total), 3)}
        for color, count in non_neutral.most_common(6)
    ]
    return {
        "color_families": sorted({item["color_family"] for item in dominant}),
        "dominant_colors": dominant,
        "background": summary["background"],
        "colored_sample_share": summary["colored_sample_share"],
        "visual_context": classify_figure_context(drawings, images, len(dominant)),
        "drawing_count": drawings,
        "image_count": images,
    }


def text_size_summary(sizes: Iterable[float]) -> dict[str, float | None]:
    values = sorted(value for value in sizes if value > 0)
    if not values:
        return {"min": None, "median": None, "max": None}
    return {"min": round(values[0], 2), "median": round(median(values), 2), "max": round(values[-1], 2)}


def extract_pdf_visual_record(path: Path, source: dict[str, Any] | None = None, max_pages: int = 12, raster_sample_pages: int = 4) -> dict[str, Any]:
    source = source or {}
    document = fitz.open(path)
    page_count_sampled = min(len(document), max_pages)
    vector_colors: Counter[str] = Counter()
    raster_colors: Counter[str] = Counter()
    text_sizes: list[float] = []
    page_geometries: Counter[str] = Counter()
    drawings = 0
    images = 0
    figure_captions = 0
    tables = 0
    pages_with_color = 0
    figure_region_count = 0
    palette_signatures: list[dict[str, Any]] = []
    for page_number in range(page_count_sampled):
        page = document[page_number]
        page_geometries[f"{round(page.rect.width)}x{round(page.rect.height)}"] += 1
        page_colors = 0
        text = page.get_text("text")
        figure_captions += len(re.findall(r"(?im)\bfig(?:ure)?\.?\s*\d+", text))
        tables += len(re.findall(r"(?im)\btable\s*\d+", text))
        regions = figure_regions(page)
        figure_region_count += len(regions)
        page_drawings = page.get_drawings()
        page_images = page.get_images(full=True)
        for drawing in page_drawings:
            drawings += 1
            if not drawing_in_regions(drawing, regions):
                continue
            for raw in (drawing.get("color"), drawing.get("fill")):
                rgb = color_tuple(raw)
                if rgb is None:
                    continue
                vector_colors[rgb_to_hex(rgb)] += 1
                page_colors += 1
        images += len(page_images)
        if page_number < raster_sample_pages:
            for region in regions:
                page_raster, raster_summary = region_raster_summary(page, region)
                raster_colors.update(page_raster)
                page_colors += sum(page_raster.values())
                region_vector: Counter[str] = Counter()
                region_drawings = 0
                for drawing in page_drawings:
                    if not drawing_in_regions(drawing, [region]):
                        continue
                    region_drawings += 1
                    for raw in (drawing.get("color"), drawing.get("fill")):
                        rgb = color_tuple(raw)
                        if rgb is not None:
                            region_vector[rgb_to_hex(rgb)] += 1
                region_images = sum(1 for image in page_images if image)
                signature = palette_signature(region_vector, page_raster, raster_summary, region_drawings, region_images)
                if signature["dominant_colors"]:
                    palette_signatures.append(signature)
        if page_colors:
            pages_with_color += 1
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    size = span.get("size")
                    if isinstance(size, (int, float)):
                        text_sizes.append(float(size))
    non_neutral = [color for color in vector_colors if not is_neutral(color)]
    layout = classify_layout(drawings, images, figure_captions, page_count_sampled, len(non_neutral))
    color_clusters = [
        {"hex": color, "count": count, "source": "figure-vector"}
        for color, count in vector_colors.most_common(12)
    ] + [
        {"hex": color, "count": count, "source": "figure-raster"}
        for color, count in raster_colors.most_common(8)
    ]
    venue = source.get("venue") or "unknown"
    eligibility = source.get("eligibility") or source.get("use") or "comparison-only"
    confidence = "medium" if eligibility == "style-evidence" and page_count_sampled >= 8 else "low" if eligibility == "style-evidence" else "insufficient"
    return {
        "source_id": source.get("source_id") or source.get("file") or path.name,
        "source_hash": sha256(path),
        "venue": venue if venue in {"www", "iclr", "icml"} else "unknown",
        "eligibility": eligibility if eligibility in {"style-evidence", "comparison-only", "holdout", "excluded"} else "comparison-only",
        "page_count_sampled": page_count_sampled,
        "page_geometry_modes": [{"geometry": key, "count": count} for key, count in page_geometries.most_common(3)],
        "feature_counts": {
            "drawings": drawings,
            "images": images,
            "figure_captions": figure_captions,
            "figure_regions": figure_region_count,
            "tables": tables,
            "pages_with_color": pages_with_color,
        },
        "color_clusters": color_clusters,
        "palette_signatures": palette_signatures,
        "text_size_summary": text_size_summary(text_sizes),
        "layout_archetypes": layout,
        "confidence": confidence,
        "notes": ["aggregate-only; no figure crops, page text, or source data retained"],
    }


def load_local_sources(config_path: Path, corpus_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    document = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    result: list[tuple[Path, dict[str, Any]]] = []
    for source in document.get("sources", []):
        file_name = source.get("file")
        if not file_name:
            continue
        path = corpus_root / file_name
        if path.is_file():
            result.append((path, source))
    return result


def load_source_manifest(manifest_path: Path, corpus_root: Path) -> tuple[list[tuple[Path, dict[str, Any]]], list[dict[str, Any]]]:
    document = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    rows = list(document.get("sources", []))
    sources: list[tuple[Path, dict[str, Any]]] = []
    for row in rows:
        relative = row.get("relative_path")
        if not relative:
            continue
        path = corpus_root / str(relative)
        if not path.is_file():
            continue
        meta = {
            "source_id": row.get("source_id"),
            "file": path.name,
            "venue": row.get("venue"),
            "eligibility": row.get("eligibility", "holdout"),
            "track": row.get("track"),
            "collection_status": row.get("collection_status"),
            "verification_status": row.get("verification_status"),
        }
        sources.append((path, meta))
    return sources, rows


def discover_external_sources(corpus_root: Path) -> list[tuple[Path, dict[str, Any]]]:
    result: list[tuple[Path, dict[str, Any]]] = []
    for venue, conference in CONFERENCES.items():
        for path in sorted((corpus_root / "papers" / conference).rglob("*.pdf")) if (corpus_root / "papers" / conference).is_dir() else []:
            result.append((path, {"file": path.name, "venue": venue, "status": "verified-main", "use": "style-evidence"}))
    return result


def stability(counter: Counter[str]) -> dict[str, float | int | None]:
    total = sum(counter.values())
    if not total:
        return {"top_share": None, "unique": 0}
    return {"top_share": round(max(counter.values()) / total, 3), "unique": len(counter)}


def distinct_palette_support(items: list[dict[str, Any]], limit: int = 6) -> list[dict[str, Any]]:
    """Keep chromatically distinct candidates; near-duplicates do not fill semantic slots."""
    selected: list[dict[str, Any]] = []
    for item in items:
        hue = palette_hue(item["hex"])
        if any(min(abs(hue - palette_hue(existing["hex"])), 1 - abs(hue - palette_hue(existing["hex"]))) < 0.1 for existing in selected):
            continue
        selected.append(item)
        if len(selected) >= limit:
            break
    return selected


def profile_stability(rows: list[dict[str, Any]], minimum_support: int, samples: int = 200, seed: int = 17) -> dict[str, Any]:
    source_families = {
        str(record["source_id"]): set().union(*(set(signature.get("color_families") or []) for signature in record.get("palette_signatures") or []))
        for record in rows
    }
    source_families = {source: families for source, families in source_families.items() if families}
    if not source_families:
        return {"source_count": 0, "cooccurrence_pairs": [], "bootstrap_retention": 0.0, "leave_one_out_jaccard": 0.0}
    pair_sources: dict[tuple[int, int], set[str]] = defaultdict(set)
    for source, families in source_families.items():
        ordered = sorted(families)
        for index, left in enumerate(ordered):
            for right in ordered[index + 1:]:
                pair_sources[(left, right)].add(source)
    stable_pairs = [
        {"families": list(pair), "source_count": len(sources), "source_share": round(len(sources) / len(source_families), 3)}
        for pair, sources in pair_sources.items() if len(sources) >= minimum_support
    ]
    stable_pairs.sort(key=lambda item: (-item["source_count"], item["families"]))
    baseline = {tuple(item["families"]) for item in stable_pairs[:6]}
    rng = random.Random(seed)
    sources = sorted(source_families)
    retained = 0
    for _ in range(samples):
        draw = [rng.choice(sources) for _ in sources]
        counts: Counter[tuple[int, int]] = Counter()
        for source in draw:
            families = sorted(source_families[source])
            counts.update((left, right) for index, left in enumerate(families) for right in families[index + 1:])
        sample_top = {pair for pair, _ in counts.most_common(6)}
        retained += len(baseline & sample_top) / max(1, len(baseline))
    loo_scores = []
    for omitted in sources:
        counts: Counter[tuple[int, int]] = Counter()
        for source, families_set in source_families.items():
            if source == omitted:
                continue
            families = sorted(families_set)
            counts.update((left, right) for index, left in enumerate(families) for right in families[index + 1:])
        candidate = {pair for pair, _ in counts.most_common(6)}
        loo_scores.append(len(baseline & candidate) / max(1, len(baseline | candidate)))
    return {
        "source_count": len(source_families), "cooccurrence_pairs": stable_pairs[:8],
        "bootstrap_retention": round(retained / samples, 3),
        "leave_one_out_jaccard": round(sum(loo_scores) / max(1, len(loo_scores)), 3),
    }


def promote_rules(records: list[dict[str, Any]], source_rows: list[dict[str, Any]] | None = None, target_per_venue: int = 30) -> tuple[dict[str, Any], dict[str, Any]]:
    by_venue: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record["eligibility"] == "style-evidence":
            by_venue[record["venue"]].append(record)
    source_rows = source_rows or []
    stats: dict[str, Any] = {"schema_version": 3, "generated": date.today().isoformat(), "venues": {}}
    rules: dict[str, Any] = {
        "schema_version": 3,
        "generated": date.today().isoformat(),
        "promotion_thresholds": {"promoted": PROMOTION_MIN_SOURCES, "preliminary": PRELIMINARY_MIN_SOURCES, "target_per_venue": target_per_venue},
        "rules": {},
        "boundary": "Visual-style evidence is aggregate-only and must not be presented as official venue policy or acceptance advice.",
    }
    for venue in ("www", "iclr", "icml"):
        rows = by_venue.get(venue, [])
        venue_source_rows = [row for row in source_rows if row.get("venue") == venue]
        extracted_rows = [record for record in records if record.get("venue") == venue]
        color_counter: Counter[str] = Counter()
        color_sources: dict[str, set[str]] = defaultdict(set)
        family_counter: Counter[int] = Counter()
        family_sources: dict[int, set[str]] = defaultdict(set)
        family_color_counter: dict[int, Counter[str]] = defaultdict(Counter)
        family_color_sources: dict[int, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
        layout_counter: Counter[str] = Counter()
        track_counter: Counter[str] = Counter()
        status_counter: Counter[str] = Counter()
        if venue_source_rows:
            track_counter.update(str(row.get("track") or "unknown") for row in venue_source_rows)
            status_counter.update(str(row.get("collection_status") or "unknown") for row in venue_source_rows)
        for record in rows:
            for color in record["color_clusters"]:
                if color["source"] in {"figure-vector", "figure-raster", "vector"} and not is_neutral(color["hex"]) and palette_chroma(color["hex"]) >= 0.2:
                    color_counter[color["hex"]] += int(color["count"])
                    color_sources[color["hex"]].add(record["source_id"])
                    family = palette_family(color["hex"])
                    family_counter[family] += int(color["count"])
                    family_sources[family].add(record["source_id"])
                    family_color_counter[family][color["hex"]] += int(color["count"])
                    family_color_sources[family][color["hex"]].add(record["source_id"])
            layout_counter.update(record["layout_archetypes"])
        minimum_color_support = max(3, math.ceil(len(rows) * 0.25))
        palette_support = []
        for family, source_ids in family_sources.items():
            if len(source_ids) < minimum_color_support:
                continue
            visible = [color for color in family_color_counter[family] if contrast_on_white(color) >= 1.8]
            if not visible:
                continue
            representative = max(
                visible,
                key=lambda color: (
                    len(family_color_sources[family][color]),
                    family_color_counter[family][color],
                    contrast_on_white(color),
                ),
            )
            palette_support.append({
                "hex": representative,
                "color_family": family,
                "source_count": len(source_ids),
                "representative_source_count": len(family_color_sources[family][representative]),
                "source_share": round(len(source_ids) / max(1, len(rows)), 3),
                "figure_color_count": family_counter[family],
                "hue": round(palette_hue(representative), 3),
                "chroma": round(palette_chroma(representative), 3),
                "contrast_on_white": round(contrast_on_white(representative), 3),
            })
        palette_support.sort(key=lambda item: (-item["source_count"], -item["figure_color_count"], item["hex"]))
        palette_support = distinct_palette_support(palette_support)
        status = (
            "promoted" if len(rows) >= PROMOTION_MIN_SOURCES
            else "preliminary" if len(rows) >= PRELIMINARY_MIN_SOURCES
            else "external-corpus-required"
        )
        anchor_status = "usable" if status == "promoted" and len(palette_support) >= 3 else "insufficient"
        stability_report = profile_stability(rows, minimum_color_support)
        profile_status = "usable" if anchor_status == "usable" and stability_report["source_count"] >= PROMOTION_MIN_SOURCES and stability_report["bootstrap_retention"] >= 0.6 else "insufficient"
        # palette_status remains the v2 anchor-availability compatibility field.
        # Runtime venue injection is gated by the stricter profile_status.
        palette_status = anchor_status
        palette_reason = None if profile_status == "usable" else (
            "anchors-usable-profile-unstable" if anchor_status == "usable" else
            "promoted-no-usable-palette" if status == "promoted" else "style-evidence-below-promotion-threshold"
        )
        profile_support = {
            family: {
                "status": profile_status,
                "provenance": "constructed-from-observed-anchors",
                "source_count": stability_report["source_count"],
                "bootstrap_retention": stability_report["bootstrap_retention"],
                "leave_one_out_jaccard": stability_report["leave_one_out_jaccard"],
            }
            for family in ("semantic", "categorical", "ordered", "sequential", "diverging", "dark-overlay")
        }
        stats["venues"][venue] = {
            "eligible_sources": len(rows),
            "coverage": {
                "target_sources": target_per_venue,
                "manifest_sources": len(venue_source_rows),
                "extracted_records": len(extracted_rows),
                "eligible_count": len(rows),
                "holdout_count": sum(row.get("eligibility") == "holdout" for row in venue_source_rows),
                "download_failures": sum(row.get("collection_status") == "download-error" for row in venue_source_rows),
                "track_mix": dict(track_counter),
                "collection_status": dict(status_counter),
                "palette_stability": stability(color_counter),
                "palette_source_prevalence": palette_support[:8],
                "minimum_palette_source_support": minimum_color_support,
                "palette_status": palette_status,
                "anchor_status": anchor_status,
                "profile_status": profile_status,
                "profile_stability": stability_report,
                "palette_fallback_reason": palette_reason,
                "layout_archetype_stability": stability(layout_counter),
            },
            "top_vector_colors": [{"hex": color, "count": count} for color, count in color_counter.most_common(8)],
            "layout_archetypes": dict(layout_counter),
        }
        rules["rules"][venue] = {
            "status": status,
            "style_status": status,
            "eligible_sources": len(rows),
            "palette_status": palette_status,
            "anchor_status": anchor_status,
            "profile_status": profile_status,
            "palette_fallback_reason": palette_reason,
            "palette_candidates": [item["hex"] for item in palette_support[:6]] if anchor_status == "usable" else [],
            "palette_candidate_support": palette_support[:6],
            "palette_profiles": profile_support,
            "layout_archetypes": [name for name, _ in layout_counter.most_common(4)],
            "guidance": (
                "Use as corpus-calibrated defaults only after promotion threshold is met."
                if status == "promoted"
                else "Treat as preliminary; prefer conservative generic styling and state the evidence gap when venue-specific style matters."
            ),
        }
    stats["records_total"] = len(records)
    stats["eligible_total"] = sum(1 for record in records if record["eligibility"] == "style-evidence")
    return stats, rules


def derive(corpus_root: Path, output_dir: Path, local_only: bool = False, max_pages: int = 12, source_manifest: Path | None = None, target_per_venue: int = 30) -> dict[str, Any]:
    config = ROOT / "corpus-sources.yaml"
    source_rows: list[dict[str, Any]] = []
    if source_manifest is not None:
        if not source_manifest.is_file():
            raise FileNotFoundError(f"source manifest does not exist: {source_manifest}")
        sources, source_rows = load_source_manifest(source_manifest, corpus_root)
    else:
        sources = load_local_sources(config, corpus_root)
    if not local_only:
        # A supplied manifest is the provenance boundary. Do not silently
        # promote PDFs merely because they happen to exist under corpus_root.
        if source_manifest is None:
            known = {path.resolve() for path, _ in sources}
            sources.extend((path, meta) for path, meta in discover_external_sources(corpus_root) if path.resolve() not in known)
    records = [extract_pdf_visual_record(path, meta, max_pages=max_pages) for path, meta in sources]
    stats, rules = promote_rules(records, source_rows=source_rows, target_per_venue=target_per_venue)
    index = {
        "schema_version": 1,
        "generated": date.today().isoformat(),
        "source_policy": {
            "aggregate_only": True,
            "raw_pages_or_figures_retained": False,
            "raw_text_retained": False,
            "local_only": local_only,
            "source_manifest": source_manifest.name if source_manifest else None,
        },
        "records": records,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "visual-style-index.yaml").write_text(yaml.safe_dump(index, sort_keys=False, allow_unicode=True), encoding="utf-8")
    (output_dir / "visual-style-stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_dir / "visual-style-rules.yaml").write_text(yaml.safe_dump(rules, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return {"records": len(records), "eligible": stats["eligible_total"], "output_dir": str(output_dir)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus-root", type=Path, default=ROOT.parent, help="Root containing local PDFs and optional papers/<conference> external corpus")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "evidence" / "derived")
    parser.add_argument("--source-manifest", type=Path, help="Verified visual-style source manifest produced by collect_visual_style_corpus.py")
    parser.add_argument("--local-only", action="store_true", help="Only use corpus-sources.yaml local PDFs")
    parser.add_argument("--max-pages", type=int, default=12)
    parser.add_argument("--target-per-venue", type=int, default=30)
    args = parser.parse_args()
    result = derive(
        args.corpus_root.resolve(),
        args.output_dir.resolve(),
        local_only=args.local_only,
        max_pages=args.max_pages,
        source_manifest=args.source_manifest.resolve() if args.source_manifest else None,
        target_per_venue=args.target_per_venue,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
