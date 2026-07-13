#!/usr/bin/env python3
"""Render reproducible single- or multi-panel CS paper figure bundles from YAML/CSV specs."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
from pathlib import Path
from typing import Any, Iterable

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from cs_figure_style import active_palette_resolution, add_panel_label, apply_venue_style, figure_size, save_figure_bundle, set_palette_context
from top_cs_figure_core import apply_transforms, normalize_spec, summarize_panel_rows
from top_cs_figure_core.geometry import geometry_report
from top_cs_figure_core.layout import apply_annotations, apply_scales, create_axes, manage_tick_density
from top_cs_figure_core.provenance import clean_internal, hash_file, schematic_records, write_plotted_data
from top_cs_figure_core.renderers import (
    render_calibration,
    render_comparison,
    render_composition,
    render_distribution,
    render_forest,
    render_heatmap,
    render_image_plate,
    render_network,
    render_paired,
    render_polar,
    render_ranking,
    render_scatter,
    render_schematic,
    render_tradeoff,
    render_trend,
    styles_for,
)


BLOCKING_STATUSES = {"planned", "missing", "unverified"}
VISUAL_FAMILIES = {
    "comparison",
    "trend-scaling",
    "matrix-heatmap",
    "embedding-scatter",
    "network",
    "method-schematic",
    "distribution-uncertainty",
    "tradeoff-frontier",
    "calibration-reliability",
    "ranking-critical-difference",
    "qualitative-image-plate",
    "forest-interval",
    "composition-stacked",
    "paired-change",
    "polar-summary",
}


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"data source is empty: {path}")
    return rows


def require_columns(rows: list[dict[str, str]], columns: Iterable[str]) -> None:
    available = set(rows[0]) if rows else set()
    missing = [column for column in columns if column and column not in available]
    if missing:
        raise ValueError(f"missing required columns: {', '.join(missing)}")


def required_columns(encodings: dict[str, str], visual_family: str) -> list[str]:
    keys = {
        "comparison": ["x", "y"],
        "trend-scaling": ["x", "y"],
        "matrix-heatmap": ["row", "column", "value"],
        "embedding-scatter": ["x", "y"],
        "network": ["source", "target"],
        "distribution-uncertainty": ["group", "value"],
        "tradeoff-frontier": ["x", "y"],
        "calibration-reliability": ["confidence", "accuracy"],
        "ranking-critical-difference": ["method", "rank"],
        "qualitative-image-plate": ["image"],
        "forest-interval": ["label", "estimate", "lower", "upper"],
        "composition-stacked": ["x", "segment", "value"],
        "paired-change": ["pair", "condition", "value"],
        "polar-summary": ["axis", "value"],
    }.get(visual_family, [])
    columns = [encodings[key] for key in keys if key in encodings]
    for key in ("lower", "upper", "error", "series", "group", "label", "size"):
        if encodings.get(key):
            columns.append(encodings[key])
    return columns


def panel_source(panel: dict[str, Any], spec: dict[str, Any], spec_path: Path) -> Path | None:
    source = panel.get("data_source") or panel.get("source")
    if source is None:
        sources = spec.get("data_sources") or []
        source = sources[0] if sources else None
        if isinstance(source, dict):
            source = source.get("path")
    if source is None:
        return None
    path = Path(str(source))
    return path if path.is_absolute() else (spec_path.parent / path).resolve()


def normalized_panels(spec: dict[str, Any]) -> list[dict[str, Any]]:
    if spec.get("panels"):
        panels = [dict(panel) for panel in spec["panels"]]
    else:
        legacy = dict(spec)
        panel_map = legacy.get("panel_map") or [{}]
        legacy["panel_id"] = str(panel_map[0].get("panel_id", "a"))
        panels = [legacy]
    ids = [str(panel.get("panel_id", "")) for panel in panels]
    if not all(ids) or len(ids) != len(set(ids)):
        raise ValueError("each panel requires a unique panel_id")
    for panel in panels:
        family = panel.get("visual_family") or spec.get("visual_family")
        if family not in VISUAL_FAMILIES:
            raise ValueError(f"unsupported visual_family: {family}")
        panel["visual_family"] = family
        panel.setdefault("variant", {
            "comparison": "grouped-bar", "trend-scaling": "line", "distribution-uncertainty": "box",
            "matrix-heatmap": "sequential", "embedding-scatter": "scatter",
        }.get(family, "default"))
        panel["encodings"] = dict(panel.get("encodings") or spec.get("encodings") or {})
    return panels


def validate_statistics(panel: dict[str, Any], rows: list[dict[str, str]]) -> None:
    statistics = panel.get("statistics") or {}
    encodings = panel["encodings"]
    uncertainty = statistics.get("uncertainty") or {}
    if not uncertainty:
        return
    kind = uncertainty.get("kind")
    if kind not in {"ci", "sd", "se", "interval", "bootstrap-ci", "none"}:
        raise ValueError("unsupported statistics.uncertainty.kind")
    if encodings.get("raw_y"):
        return
    if not statistics.get("aggregation"):
        raise ValueError("statistics with uncertainty require an explicit aggregation")
    if encodings.get("error"):
        require_columns(rows, [encodings["error"]])
    elif encodings.get("lower") and encodings.get("upper"):
        require_columns(rows, [encodings["lower"], encodings["upper"]])
    else:
        raise ValueError("statistics with uncertainty require error or lower/upper encodings")


def render_panel(ax, rows: list[dict[str, str]], panel: dict[str, Any], venue: str, spec_path: Path):
    family = panel["visual_family"]
    if family == "comparison":
        return render_comparison(ax, rows, panel, venue)
    if family == "trend-scaling":
        return render_trend(ax, rows, panel, venue)
    if family == "matrix-heatmap":
        return render_heatmap(ax, rows, panel, venue)
    if family == "embedding-scatter":
        return render_scatter(ax, rows, panel, venue)
    if family == "network":
        return render_network(ax, rows, panel, venue)
    if family == "distribution-uncertainty":
        return render_distribution(ax, rows, panel, venue)
    if family == "tradeoff-frontier":
        return render_tradeoff(ax, rows, panel, venue)
    if family == "calibration-reliability":
        return render_calibration(ax, rows, panel, venue)
    if family == "ranking-critical-difference":
        return render_ranking(ax, rows, panel, venue)
    if family == "qualitative-image-plate":
        return render_image_plate(ax, rows, panel, spec_path)
    if family == "forest-interval":
        return render_forest(ax, rows, panel, venue)
    if family == "composition-stacked":
        return render_composition(ax, rows, panel, venue)
    if family == "paired-change":
        return render_paired(ax, rows, panel, venue)
    if family == "polar-summary":
        return render_polar(ax, rows, panel, venue)
    if family == "method-schematic":
        return render_schematic(ax, panel, venue)
    raise ValueError(f"unsupported visual_family for spec rendering: {family}")


def render(spec: dict[str, Any], spec_path: Path, outdir: Path | None = None) -> dict[str, Any]:
    spec, migration = normalize_spec(spec, spec_path)
    if spec.get("evidence_status") in BLOCKING_STATUSES:
        raise ValueError(f"refusing to render result-like figure with evidence_status={spec.get('evidence_status')}")
    panels = normalized_panels(spec)
    venue = str(spec.get("venue", "generic"))
    style = spec.get("style") or {}
    figsize = figure_size(style.get("size", "double" if len(panels) > 1 else "single"))
    if style.get("width_mm") and style.get("height_mm"):
        figsize = (float(style["width_mm"]) / 25.4, float(style["height_mm"]) / 25.4)
    palette_profile = dict(style.get("palette_profile") or {})
    applied_palette = apply_venue_style(venue, panels[0]["visual_family"], palette_profile=palette_profile, variant=panels[0].get("variant"))
    fig = plt.figure(figsize=figsize)
    axes = create_axes(fig, panels, spec.get("layout"))
    shared_handles: dict[str, Any] = {}
    shared_colorbars: dict[str, tuple[Any, list[Any]]] = {}
    panel_results = []
    panel_rows: dict[str, list[dict[str, Any]]] = {}
    panel_specs = {str(panel["panel_id"]): panel for panel in panels}
    base = Path(spec["output_base"])
    if outdir is not None:
        base = outdir / base.name
    elif not base.is_absolute():
        base = spec_path.parent / base
    base.parent.mkdir(parents=True, exist_ok=True)
    for panel in panels:
        if panel.get("evidence_status") in BLOCKING_STATUSES:
            raise ValueError(f"refusing to render panel {panel['panel_id']} with evidence_status={panel.get('evidence_status')}")
        source = panel_source(panel, spec, spec_path)
        rows: list[dict[str, str]] = []
        if panel["visual_family"] != "method-schematic":
            if source is None:
                raise ValueError(f"panel {panel['panel_id']} requires a data_source")
            registry_item = (spec.get("source_registry") or {}).get(str(panel.get("source_id")), {})
            actual_hash = hash_file(source)
            if registry_item.get("expected_sha256") and registry_item["expected_sha256"] != actual_hash:
                raise ValueError(f"source hash mismatch for {panel['panel_id']}: {source}")
            raw_rows = load_rows(source)
            if registry_item.get("columns"):
                require_columns(raw_rows, registry_item["columns"])
            rows, transform_report = apply_transforms(raw_rows, panel.get("transforms"))
            panel["_raw_rows"] = rows
            if panel["encodings"].get("raw_y"):
                require_columns(rows, [panel["encodings"]["raw_y"]])
            if panel.get("_spec_version") == 3 and panel["visual_family"] == "qualitative-image-plate":
                require_columns(rows, [panel["encodings"][key] for key in ("image", "image_id", "crop_provenance", "aspect_ratio")])
            rows, statistics_report = summarize_panel_rows(rows, panel)
            require_columns(rows, required_columns(panel["encodings"], panel["visual_family"]))
            validate_statistics(panel, rows)
            significance = (panel.get("statistics") or {}).get("significance")
            if significance:
                require_columns(rows, [significance["source_column"]])
        else:
            rows = schematic_records(panel)
            transform_report, statistics_report, actual_hash = [], {"computed": False}, None
        profile_for_panel = dict(palette_profile)
        profile_for_panel.update(panel.get("palette_profile") or {})
        identity_key = panel["encodings"].get("series") or panel["encodings"].get("group") or panel["encodings"].get("segment")
        if "series_count" not in profile_for_panel and identity_key and rows:
            profile_for_panel["series_count"] = max(2, min(8, len({str(row.get(identity_key, "value")) for row in rows})))
        panel_palette_resolution = set_palette_context(venue, panel["visual_family"], panel.get("variant"), profile_for_panel)
        ax = axes[str(panel["panel_id"])]
        panel_background = str(panel_palette_resolution.get("background", "#FFFFFF"))
        if panel_background.upper() != "#FFFFFF":
            ax.set_facecolor(panel_background)
            ax.tick_params(colors="white")
            for spine in ax.spines.values():
                spine.set_color("#E6E8EB")
        result = render_panel(ax, rows, panel, venue, spec_path)
        panel_rows[str(panel["panel_id"])] = rows
        apply_scales(ax, panel, rows)
        if panel["visual_family"] not in {"method-schematic", "qualitative-image-plate", "polar-summary"}:
            manage_tick_density(ax, panel)
        apply_annotations(ax, panel.get("annotations") or [])
        add_panel_label(ax, str(panel["panel_id"]), x=-0.13, y=1.03, color="white" if panel_background.upper() != "#FFFFFF" else "black")
        if panel.get("title"):
            hero = str((spec.get("layout") or {}).get("hero_panel", "")) == str(panel["panel_id"])
            ax.set_title(str(panel["title"]), loc="left", fontsize=7.6 if hero else 6.8, fontweight="bold" if hero else "normal")
        if panel_background.upper() != "#FFFFFF":
            ax.title.set_color("white"); ax.xaxis.label.set_color("white"); ax.yaxis.label.set_color("white")
        legend_mode = panel.get("legend", "local")
        handles, labels = ax.get_legend_handles_labels()
        if legend_mode == "shared" and handles:
            for handle, label in zip(handles, labels):
                if label and not label.startswith("_"):
                    shared_handles.setdefault(label, handle)
            legend = ax.get_legend()
            if legend:
                legend.remove()
        elif legend_mode == "local" and handles:
            ax.legend(loc="best", fontsize=6)
        colorbar_group = panel.get("colorbar_group")
        if result is not None and panel["visual_family"] == "matrix-heatmap":
            if colorbar_group:
                item = shared_colorbars.setdefault(str(colorbar_group), (result, []))
                item[1].append(ax)
            else:
                fig.colorbar(result, ax=ax, fraction=0.046, pad=0.04)
        plotted_path = write_plotted_data(base, str(panel["panel_id"]), rows) if rows else None
        panel_results.append({
            "panel_id": str(panel["panel_id"]), "visual_family": panel["visual_family"], "variant": panel.get("variant"),
            "data_source": str(source) if source else None, "data_hash": actual_hash,
            "transforms": transform_report, "statistics": statistics_report,
            "plotted_data": str(plotted_path) if plotted_path else None,
            "plotted_data_hash": hash_file(plotted_path) if plotted_path else None,
            "caption_obligations": panel.get("caption_obligations") or [],
            "palette_resolution": panel_palette_resolution,
            "semantic_styles": styles_for(panel, venue, list(dict.fromkeys(str(row.get(panel["encodings"].get("series") or panel["encodings"].get("group") or panel["encodings"].get("segment"), "value")) for row in rows))) if rows and (panel["encodings"].get("series") or panel["encodings"].get("group") or panel["encodings"].get("segment")) else {},
        })
    for mappable, target_axes in shared_colorbars.values():
        fig.colorbar(mappable, ax=target_axes, fraction=0.025, pad=0.02)
    if shared_handles:
        fig.legend(list(shared_handles.values()), list(shared_handles), loc="lower center", ncol=min(6, max(1, len(shared_handles))), fontsize=6, frameon=False)
    directions = {str(panel.get("metric_direction") or spec.get("metric_direction")) for panel in panels if (panel.get("metric_direction") or spec.get("metric_direction")) not in {None, "not-applicable", "mixed"}}
    direction_note = (spec.get("shared_guides") or {}).get("metric_direction_note")
    if not direction_note and len(directions) == 1:
        direction_note = next(iter(directions)).replace("-", " ")
    if direction_note:
        fig.text(0.995, 0.995, str(direction_note), ha="right", va="top", fontsize=6, color="#59616C")
    fig.tight_layout(rect=(0.015, 0.075 if shared_handles else 0.02, 0.99, 0.965), pad=0.75)
    fig.canvas.draw()
    geometry = geometry_report(fig, axes, panel_rows, panel_specs)
    saved = save_figure_bundle(fig, base, formats=tuple(spec.get("export_formats", ["svg", "pdf", "png"])))
    normalized_path = base.parent / f"{base.name}.normalized-spec.yaml"
    normalized_path.write_text(yaml.safe_dump(clean_internal(spec), sort_keys=False, allow_unicode=False), encoding="utf-8")
    from cs_figure_style import venue_style_status
    manifest = {
        "figure_id": spec["figure_id"], "input_spec": str(spec_path), "input_spec_hash": hash_file(spec_path),
        "spec_version": 3, "migration": migration, "venue": venue, "venue_style": venue_style_status(venue),
        "semantic_palette": applied_palette,
        "palette_resolution": {"requested": palette_profile or {"mode": "venue-derived", "family": "auto"}, "panels": {item["panel_id"]: item["palette_resolution"] for item in panel_results}},
        "environment": {"python": platform.python_version(), "matplotlib": matplotlib.__version__, "seed": (spec.get("reproducibility") or {}).get("seed", 0)},
        "panels": panel_results, "geometry": geometry, "normalized_spec": str(normalized_path),
        "normalized_spec_hash": hash_file(normalized_path), "saved": saved,
    }
    render_path = base.parent / f"{base.name}.render.json"
    render_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    manifest["render_manifest"] = str(render_path)
    return {**manifest, "base": str(base)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path)
    parser.add_argument("--outdir", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()
    spec = yaml.safe_load(args.spec.read_text(encoding="utf-8"))
    result = render(spec, args.spec.resolve(), args.outdir.resolve() if args.outdir else None)
    print(json.dumps(result, indent=2) if args.format == "json" else "\n".join(result["saved"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
