#!/usr/bin/env python3
"""Build dense synthetic atlas/gallery PNGs exclusively through the v3 renderer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import tempfile
from pathlib import Path
from typing import Any

import yaml

from render_from_figure_spec import render


ATLAS: dict[str, list[tuple[str, str]]] = {
    "www-palette-atlas": [("comparison", "grouped-bar"), ("embedding-scatter", "scatter"), ("trend-scaling", "line"), ("matrix-heatmap", "sequential"), ("matrix-heatmap", "diverging"), ("comparison", "dot")],
    "iclr-palette-atlas": [("comparison", "grouped-bar"), ("embedding-scatter", "scatter"), ("trend-scaling", "line"), ("matrix-heatmap", "sequential"), ("matrix-heatmap", "diverging"), ("comparison", "dot")],
    "icml-palette-atlas": [("comparison", "grouped-bar"), ("embedding-scatter", "scatter"), ("trend-scaling", "line"), ("matrix-heatmap", "sequential"), ("matrix-heatmap", "diverging"), ("comparison", "dot")],
    "comparison-composition": [
        ("comparison", "grouped-bar"), ("comparison", "dot"), ("comparison", "stacked-bar"),
        ("comparison", "normalized-bar"), ("comparison", "waterfall"), ("composition-stacked", "stacked"),
        ("composition-stacked", "normalized"), ("forest-interval", "interval"),
        ("paired-change", "slope"), ("comparison", "dot"), ("comparison", "grouped-bar"),
        ("composition-stacked", "normalized"),
    ],
    "trend-uncertainty": [
        ("trend-scaling", "line"), ("trend-scaling", "line-band"), ("trend-scaling", "step"),
        ("trend-scaling", "area"), ("trend-scaling", "individual-runs"), ("trend-scaling", "learning-curve"),
        ("trend-scaling", "line-band"), ("trend-scaling", "step"), ("trend-scaling", "area"),
        ("calibration-reliability", "default"), ("tradeoff-frontier", "default"), ("paired-change", "slope"),
    ],
    "distribution-interval": [
        ("distribution-uncertainty", "box"), ("distribution-uncertainty", "violin"),
        ("distribution-uncertainty", "strip"), ("distribution-uncertainty", "histogram"),
        ("distribution-uncertainty", "ecdf"), ("forest-interval", "interval"),
        ("paired-change", "slope"), ("ranking-critical-difference", "default"),
        ("distribution-uncertainty", "box"), ("distribution-uncertainty", "ecdf"),
        ("forest-interval", "interval"), ("paired-change", "slope"),
    ],
    "matrix-heatmap": [
        ("matrix-heatmap", "sequential"), ("matrix-heatmap", "diverging"),
        ("matrix-heatmap", "annotated"), ("matrix-heatmap", "confusion"),
        ("matrix-heatmap", "diverging-annotated"), ("matrix-heatmap", "sequential"),
        ("matrix-heatmap", "diverging"), ("matrix-heatmap", "annotated"),
        ("matrix-heatmap", "confusion"), ("matrix-heatmap", "diverging-annotated"),
        ("matrix-heatmap", "sequential"), ("matrix-heatmap", "diverging"),
    ],
    "scatter-tradeoff": [
        ("embedding-scatter", "scatter"), ("embedding-scatter", "bubble"),
        ("embedding-scatter", "hexbin"), ("embedding-scatter", "labeled"),
        ("tradeoff-frontier", "default"), ("calibration-reliability", "default"),
        ("embedding-scatter", "scatter"), ("embedding-scatter", "bubble"),
        ("embedding-scatter", "hexbin"), ("embedding-scatter", "labeled"),
        ("tradeoff-frontier", "default"), ("calibration-reliability", "default"),
    ],
    "ranking-calibration": [
        ("ranking-critical-difference", "default"), ("calibration-reliability", "default"),
        ("forest-interval", "interval"), ("polar-summary", "normalized"),
        ("comparison", "dot"), ("distribution-uncertainty", "ecdf"),
        ("ranking-critical-difference", "default"), ("calibration-reliability", "default"),
        ("forest-interval", "interval"), ("polar-summary", "normalized"),
        ("comparison", "dot"), ("distribution-uncertainty", "box"),
    ],
    "network-matrix": [
        ("network", "default"), ("matrix-heatmap", "sequential"), ("embedding-scatter", "scatter"),
        ("network", "default"), ("matrix-heatmap", "diverging"), ("embedding-scatter", "bubble"),
        ("network", "default"), ("matrix-heatmap", "annotated"), ("embedding-scatter", "hexbin"),
        ("network", "default"), ("matrix-heatmap", "confusion"), ("embedding-scatter", "labeled"),
    ],
    "schematic-layout": [("method-schematic", "default")] * 12,
    "qualitative-image": [("qualitative-image-plate", "default")] * 12,
    "cs-systems": [
        ("comparison", "grouped-bar"), ("trend-scaling", "line-band"), ("tradeoff-frontier", "default"),
        ("composition-stacked", "normalized"), ("distribution-uncertainty", "ecdf"),
        ("matrix-heatmap", "annotated"), ("calibration-reliability", "default"),
        ("forest-interval", "interval"), ("paired-change", "slope"),
        ("embedding-scatter", "bubble"), ("ranking-critical-difference", "default"),
        ("polar-summary", "normalized"),
    ],
}

GALLERY: dict[str, list[tuple[str, str]]] = {
    "www-benchmark-venue": [("comparison", "grouped-bar"), ("comparison", "dot"), ("trend-scaling", "line-band"), ("distribution-uncertainty", "box"), ("forest-interval", "interval"), ("matrix-heatmap", "diverging-annotated")],
    "iclr-scaling-venue": [("trend-scaling", "learning-curve"), ("trend-scaling", "line-band"), ("tradeoff-frontier", "default"), ("comparison", "dot"), ("distribution-uncertainty", "ecdf"), ("calibration-reliability", "default")],
    "icml-heatmap-venue": [("matrix-heatmap", "sequential"), ("matrix-heatmap", "diverging"), ("matrix-heatmap", "annotated"), ("matrix-heatmap", "confusion"), ("embedding-scatter", "hexbin"), ("comparison", "dot")],
    "www-calibration-venue": [("calibration-reliability", "default"), ("distribution-uncertainty", "histogram"), ("forest-interval", "interval"), ("comparison", "dot"), ("matrix-heatmap", "confusion"), ("tradeoff-frontier", "default")],
    "iclr-network-venue": [("network", "default"), ("embedding-scatter", "scatter"), ("matrix-heatmap", "sequential"), ("comparison", "dot"), ("trend-scaling", "line"), ("forest-interval", "interval")],
    "icml-schematic-venue": [("method-schematic", "default"), ("comparison", "dot"), ("trend-scaling", "line-band"), ("matrix-heatmap", "diverging"), ("network", "default"), ("calibration-reliability", "default")],
    "benchmark-ablation": [("comparison", "grouped-bar"), ("comparison", "dot"), ("trend-scaling", "line-band"), ("matrix-heatmap", "diverging-annotated"), ("distribution-uncertainty", "box"), ("forest-interval", "interval")],
    "systems-scaling-tradeoff": [("trend-scaling", "line-band"), ("tradeoff-frontier", "default"), ("composition-stacked", "normalized"), ("distribution-uncertainty", "ecdf"), ("comparison", "dot"), ("matrix-heatmap", "annotated")],
    "calibration-qualitative": [("calibration-reliability", "default"), ("distribution-uncertainty", "histogram"), ("forest-interval", "interval"), ("qualitative-image-plate", "default"), ("qualitative-image-plate", "default"), ("matrix-heatmap", "confusion")],
    "graph-robustness": [("comparison", "grouped-bar"), ("network", "default"), ("embedding-scatter", "scatter"), ("trend-scaling", "line-band"), ("matrix-heatmap", "diverging"), ("distribution-uncertainty", "violin")],
    "llm-scaling-efficiency": [("trend-scaling", "learning-curve"), ("tradeoff-frontier", "default"), ("composition-stacked", "stacked"), ("forest-interval", "interval"), ("comparison", "dot"), ("polar-summary", "normalized")],
    "retrieval-online-offline": [("comparison", "grouped-bar"), ("paired-change", "slope"), ("trend-scaling", "step"), ("calibration-reliability", "default"), ("distribution-uncertainty", "ecdf"), ("matrix-heatmap", "annotated")],
    "agent-failure-analysis": [("comparison", "stacked-bar"), ("composition-stacked", "normalized"), ("trend-scaling", "line"), ("matrix-heatmap", "diverging-annotated"), ("network", "default"), ("forest-interval", "interval")],
    "multimodal-evidence": [("method-schematic", "default"), ("qualitative-image-plate", "default"), ("qualitative-image-plate", "default"), ("comparison", "dot"), ("embedding-scatter", "bubble"), ("calibration-reliability", "default")],
}

CSV_COLUMNS = [
    "panel", "category", "method", "value", "lower", "upper", "x", "y", "run", "group",
    "row", "column", "label", "size", "source", "target", "confidence", "accuracy", "rank",
    "segment", "pair", "condition", "axis", "estimate", "image", "image_id", "crop_provenance",
    "aspect_ratio",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def base_panel(panel_id: str, family: str, variant: str, title: str) -> dict[str, Any]:
    if title == "default":
        title = family.replace("-", " ")
    panel: dict[str, Any] = {
        "panel_id": panel_id, "visual_family": family, "variant": variant,
        "encodings": {}, "transforms": [], "statistics": {}, "scales": {}, "annotations": [],
        "semantic_roles": {"Ours": "ours", "Base": "baseline", "Strong": "strong_baseline"},
        "legend": "none", "metric_direction": "not-applicable", "caption_obligations": [], "title": title,
    }
    if family != "method-schematic":
        panel["source_id"] = "synthetic"
        panel["transforms"] = [{"kind": "filter", "column": "panel", "equals": panel_id}]
    return panel


def panel_and_rows(panel_id: str, family: str, variant: str, index: int, root: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    panel = base_panel(panel_id, family, variant, variant.replace("-", " "))
    rows: list[dict[str, Any]] = []
    add = lambda **values: rows.append({"panel": panel_id, **values})
    if family == "comparison":
        if variant == "waterfall":
            panel["encodings"] = {"x": "category", "y": "value", "ylabel": "delta"}
            for category, value in zip(("Load", "Cache", "Batch"), (4 + index % 2, -2, 3)): add(category=category, value=value)
        else:
            panel["encodings"] = {"x": "category", "y": "value", "series": "method", "ylabel": "score"}
            panel["metric_direction"] = "higher-is-better"; panel["scales"] = {"x": {"type": "categorical"}}
            for c, category in enumerate(("A", "B", "C")):
                for m, method in enumerate(("Base", "Ours")): add(category=category, method=method, value=68 + c * 3 + m * (5 + index % 3))
    elif family == "trend-scaling":
        panel["encodings"] = {"x": "x", "y": "value", "series": "method", "lower": "lower", "upper": "upper", "xlabel": "budget", "ylabel": "quality"}
        panel["metric_direction"] = "higher-is-better"
        if variant in {"individual-runs", "learning-curve"}:
            panel["encodings"].update({"run": "run", "raw_y": "value"})
            panel["encodings"].pop("lower"); panel["encodings"].pop("upper")
        for method, offset in (("Base", 0), ("Ours", 5)):
            for run in (("r1", "r2") if variant in {"individual-runs", "learning-curve"} else ("r1",)):
                for x in (1, 2, 4, 8, 16):
                    value = 45 + 8 * math.log2(x) + offset + (1 if run == "r2" else 0)
                    add(x=x, method=method, run=run, value=value, lower=value - 2, upper=value + 2)
    elif family == "distribution-uncertainty":
        panel["encodings"] = {"group": "group", "value": "value", "ylabel": "score"}
        for group, offset in (("Base", 0), ("Ours", 6)):
            for sample in range(14): add(group=group, value=68 + offset + math.sin(sample * 1.4 + index) * 4)
    elif family == "forest-interval":
        panel["encodings"] = {"label": "label", "estimate": "estimate", "lower": "lower", "upper": "upper", "null": 0, "x": "estimate"}
        panel["scales"] = {"y": {"type": "categorical"}}
        for j, label in enumerate(("Task A", "Task B", "Task C")):
            estimate = 0.08 + j * 0.09 + index * 0.002; add(label=label, estimate=estimate, lower=estimate - 0.07, upper=estimate + 0.08)
    elif family == "paired-change":
        panel["encodings"] = {"pair": "pair", "condition": "condition", "value": "value"}; panel["scales"] = {"x": {"type": "categorical"}}
        for pair in range(5):
            add(pair=f"r{pair}", condition="before", value=66 + pair * 2); add(pair=f"r{pair}", condition="after", value=72 + pair * 2 + index % 2)
    elif family == "matrix-heatmap":
        panel["encodings"] = {"row": "row", "column": "column", "value": "value", "annotate": variant in {"annotated", "confusion", "diverging-annotated"}}
        for r, row in enumerate(("A", "B", "C", "D")):
            for c, column in enumerate(("A", "B", "C", "D")):
                value = (r - c) * 0.35 if "diverging" in variant else (0.72 if r == c else 0.08 + ((r + c + index) % 4) * 0.04)
                add(row=row, column=column, value=value)
    elif family == "embedding-scatter":
        panel["encodings"] = {"x": "x", "y": "y", "series": "method"}
        if variant in {"bubble", "labeled"}: panel["encodings"].update({"label": "label", "size": "size"})
        methods = ("Ours", "Strong", "Base", "Ablation")
        for point in range(20):
            add(x=math.cos(point * 0.7) + point / 12, y=math.sin(point * 0.9), method=methods[point % len(methods)], label=f"P{point}", size=12 + point)
    elif family == "tradeoff-frontier":
        panel["encodings"] = {"x": "x", "y": "y", "series": "method", "xlabel": "latency", "ylabel": "quality", "x_direction": "lower", "y_direction": "higher"}
        for method, shift in (("Base", 0), ("Ours", 4)):
            for point in range(5): add(x=7 + point * 5 + shift / 2, y=63 + point * 4 + shift, method=method)
    elif family == "calibration-reliability":
        panel["encodings"] = {"confidence": "confidence", "accuracy": "accuracy", "series": "method"}
        for method, shift in (("Base", -0.08), ("Ours", -0.02)):
            for step in range(1, 10): add(confidence=step / 10, accuracy=max(0, min(1, step / 10 + shift)), method=method)
    elif family == "ranking-critical-difference":
        panel["encodings"] = {"method": "method", "rank": "rank"}; panel["statistics"] = {"critical_difference": 0.8}
        for method, rank in (("Ours", 1.3), ("Strong", 2.2), ("Base", 3.1)): add(method=method, rank=rank)
    elif family == "composition-stacked":
        panel["encodings"] = {"x": "category", "segment": "segment", "value": "value"}; panel["scales"] = {"x": {"type": "categorical"}}
        for category in ("Small", "Large"):
            for segment, value in (("Compute", 55), ("Memory", 30), ("IO", 15)): add(category=category, segment=segment, value=value + (5 if category == "Large" and segment == "Memory" else 0))
    elif family == "polar-summary":
        panel["encodings"] = {"axis": "axis", "value": "value"}
        for axis, value in (("Quality", .82), ("Speed", .68), ("Robust", .75), ("Calib", .62)): add(axis=axis, value=value)
    elif family == "network":
        panel["encodings"] = {"source": "source", "target": "target"}
        for source, target in (("Input", "Encoder"), ("Encoder", "Head"), ("Head", "Output"), ("Input", "Head")): add(source=source, target=target)
    elif family == "method-schematic":
        y = 0.65 if index % 2 else 0.5
        panel.update({
            "nodes": [
                {"id": "input", "label": "Input", "x": .15, "y": y, "kind": "input", "ports": ["right"]},
                {"id": "encoder", "label": "Encoder", "x": .5, "y": y, "kind": "process", "shape_label": "B x T x D", "ports": ["left", "right"]},
                {"id": "output", "label": "Output", "x": .85, "y": y, "kind": "output", "ports": ["left"]},
            ],
            "edges": [
                {"from": "input", "to": "encoder", "from_port": "right", "to_port": "left", "routing": "straight"},
                {"from": "encoder", "to": "output", "from_port": "right", "to_port": "left", "routing": "orthogonal" if index % 3 == 0 else "straight"},
            ],
            "lanes": [{"id": "main", "label": "Data path", "y": .25, "height": .55, "color": "#F5F6F8"}],
        })
    elif family == "qualitative-image-plate":
        panel["encodings"] = {"image": "image", "image_id": "image_id", "crop_provenance": "crop_provenance", "aspect_ratio": "aspect_ratio", "label": "label"}
        from PIL import Image, ImageDraw
        for image_index, label in enumerate(("Input", "Prediction")):
            image_path = root / f"{panel_id}-{image_index}.png"
            image = Image.new("RGB", (96, 60), (38 + index * 5, 78 + image_index * 38, 132 + index * 3))
            draw = ImageDraw.Draw(image); draw.rectangle((12, 10, 50 + image_index * 12, 44), outline="white", width=2); image.save(image_path)
            add(image=image_path.name, image_id=f"{panel_id}-{image_index}", crop_provenance="uncropped", aspect_ratio=1.6, label=label)
    else:
        raise ValueError(f"unsupported synthetic family: {family}")
    return panel, rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def build_spec(name: str, definitions: list[tuple[str, str]], root: Path, gallery: bool) -> tuple[Path, int]:
    panel_ids = [chr(ord("a") + index) for index in range(len(definitions))]
    panels, rows = [], []
    for index, (panel_id, definition) in enumerate(zip(panel_ids, definitions)):
        panel, panel_rows = panel_and_rows(panel_id, definition[0], definition[1], index, root)
        panels.append(panel); rows.extend(panel_rows)
    venue = next((candidate for candidate in ("www", "iclr", "icml") if name.startswith(candidate + "-") or f"-{candidate}-" in name), "generic")
    if "palette-atlas" in name:
        profiles = ["semantic", "categorical", "ordered", "sequential", "diverging", "dark-overlay"]
        for panel, family in zip(panels, profiles):
            panel["palette_profile"] = {"mode": "venue-derived", "family": family, "series_count": 7 if family in {"sequential", "diverging"} else 4, "background": "#20242A" if family == "dark-overlay" else "#FFFFFF"}
            panel["title"] = family
    csv_path = root / f"{name}.csv"; write_csv(csv_path, rows)
    if gallery:
        mosaic = ["aab", "ccd", "eef"]
        width_mm, height_mm = 183, 125
    elif len(definitions) == 6:
        mosaic = ["abc", "def"]
        width_mm, height_mm = 183, 95
    else:
        mosaic = ["abcd", "efgh", "ijkl"]
        width_mm, height_mm = 183, 145
    spec = {
        "spec_version": 3, "figure_id": name, "claim_ids": ["synthetic-atlas"], "venue": venue,
        "data_sources": [{"id": "synthetic", "path": csv_path.name, "format": "csv", "expected_sha256": sha256(csv_path), "columns": CSV_COLUMNS}],
        "panels": panels, "layout": {"kind": "mosaic", "mosaic": mosaic, "hero_panel": "a"},
        "style": {"width_mm": width_mm, "height_mm": height_mm},
        "shared_guides": {"legend": "none", "metric_direction_note": "synthetic visual grammar"},
        "reproducibility": {"seed": 40, "environment_capture": True, "write_plotted_data": True},
        "accessibility": {"minimum_text_pt": 6, "minimum_line_width_pt": .6, "redundant_encoding": True, "grayscale_required": True, "cvd_modes": ["protan", "deutan", "tritan"]},
        "output_base": name, "export_formats": ["png"], "evidence_status": "available",
        "caption": f"Synthetic {name} atlas; not experimental evidence.", "manuscript_callout": "Synthetic visual grammar only.",
    }
    spec_path = root / f"{name}.yaml"; spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return spec_path, len(panels)


def compress_png(source: Path, destination: Path) -> None:
    from PIL import Image
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        rgb = image.convert("RGB")
        rgb.thumbnail((1800, 1500))
        quantized = rgb.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        quantized.save(destination, optimize=True)
    if destination.stat().st_size > 350 * 1024:
        raise ValueError(f"asset exceeds 350 KB: {destination}")


def build(output_root: Path) -> dict[str, object]:
    records: list[dict[str, Any]] = []
    expected: set[Path] = set()
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        definitions = [(f"chart-atlas/{name}", items, False) for name, items in ATLAS.items()]
        definitions += [(f"gallery/{name}", items, True) for name, items in GALLERY.items()]
        for relative, items, gallery in definitions:
            slug = relative.replace("/", "-")
            spec_path, panel_count = build_spec(slug, items, root, gallery)
            spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
            result = render(spec, spec_path, root / "rendered" / slug)
            rendered_png = Path(next(path for path in result["saved"] if path.endswith(".png")))
            output = output_root / f"{relative}.png"; compress_png(rendered_png, output); expected.add(output.resolve())
            csv_path = root / f"{slug}.csv"
            records.append({
                "asset": str(output.relative_to(output_root)), "sha256": sha256(output), "bytes": output.stat().st_size,
                "synthetic_csv_sha256": sha256(csv_path), "synthetic_yaml_sha256": sha256(spec_path), "seed": 40,
                "panel_count": panel_count, "visual_families": sorted({family for family, _ in items}),
                "production_renderer": True, "render_manifest_sha256": sha256(Path(result["render_manifest"])),
                "venue": spec.get("venue", "generic"),
            })
    for directory in (output_root / "chart-atlas", output_root / "gallery"):
        if directory.is_dir():
            for path in directory.glob("*.png"):
                if path.resolve() not in expected:
                    path.unlink()
    script_dir = Path(__file__).resolve().parent
    manifest = {
        "schema_version": 2, "generator": Path(__file__).name, "generator_sha256": sha256(Path(__file__)),
        "renderer_sha256": sha256(script_dir / "render_from_figure_spec.py"),
        "style_dependency_sha256": sha256(script_dir / "cs_figure_style.py"), "external_assets_used": False,
        "atlas_count": len(ATLAS), "gallery_count": len(GALLERY),
        "visual_example_count": sum(record["panel_count"] for record in records),
        "records": records, "total_bytes": sum(record["bytes"] for record in records),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "generated-manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-root", type=Path, default=Path(__file__).resolve().parents[1] / "assets")
    args = parser.parse_args(); print(json.dumps(build(args.output_root.resolve()), indent=2)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
