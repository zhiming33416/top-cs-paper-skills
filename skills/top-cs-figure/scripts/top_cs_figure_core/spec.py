from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any


TOP_LEVEL_FIELDS = {
    "figure_id", "claim_ids", "venue", "spec_version", "visual_family", "data_sources",
    "panel_map", "encodings", "metric_direction", "output_base", "export_formats",
    "evidence_status", "caption", "manuscript_callout", "style", "layout", "panels",
    "data_provenance", "shared_guides", "accessibility", "reproducibility", "output",
}
PANEL_FIELDS = {
    "panel_id", "visual_family", "variant", "source_id", "data_source", "encodings",
    "transforms", "statistics", "scales", "annotations", "semantic_roles", "legend",
    "palette_profile",
    "colorbar_group", "title", "metric_direction", "caption_obligations", "accessibility",
    "nodes", "edges", "groups", "lanes", "columns",
}
SOURCE_FIELDS = {"id", "path", "format", "expected_sha256", "columns"}
TRANSFORMS = {"filter", "sort", "group", "aggregate", "normalize", "baseline-delta", "rank"}
TRANSFORM_FIELDS = {
    "filter": {"kind", "column", "equals", "in"}, "sort": {"kind", "by", "descending"},
    "group": {"kind", "by"}, "aggregate": {"kind", "group_by", "metrics"},
    "normalize": {"kind", "column", "output", "method"},
    "baseline-delta": {"kind", "column", "baseline_column", "output"},
    "rank": {"kind", "column", "output", "direction"},
}
VARIANTS = {
    "comparison": {"grouped-bar", "stacked-bar", "normalized-bar", "dot", "waterfall"},
    "trend-scaling": {"line", "line-band", "step", "area", "individual-runs", "learning-curve"},
    "matrix-heatmap": {"sequential", "diverging", "annotated", "confusion", "diverging-annotated"},
    "embedding-scatter": {"scatter", "bubble", "hexbin", "labeled"},
    "distribution-uncertainty": {"box", "violin", "strip", "histogram", "ecdf"},
    "composition-stacked": {"stacked", "normalized"}, "forest-interval": {"interval"},
    "paired-change": {"slope"}, "polar-summary": {"normalized"},
}


def _reject_unknown(value: dict[str, Any], allowed: set[str], where: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"unknown {where} fields: {', '.join(unknown)}")


def validate_v3_spec(spec: dict[str, Any]) -> None:
    _reject_unknown(spec, TOP_LEVEL_FIELDS, "spec")
    required = {"figure_id", "claim_ids", "venue", "data_sources", "panels", "output_base", "export_formats", "evidence_status"}
    missing = sorted(required - set(spec))
    if missing:
        raise ValueError(f"v3 spec missing fields: {', '.join(missing)}")
    style = spec.get("style") or {}
    _reject_unknown(style, {"palette", "palette_profile", "width_mm", "height_mm", "size"}, "style")
    profile = style.get("palette_profile") or {}
    _reject_unknown(profile, {"mode", "family", "series_count", "background", "emphasis_role", "colors"}, "palette profile")
    if profile.get("mode") == "custom" and len(profile.get("colors") or []) < 2:
        raise ValueError("custom palette profile requires at least two colors")
    sources = spec.get("data_sources")
    if not isinstance(sources, list) or not sources:
        raise ValueError("v3 data_sources must be a non-empty source registry")
    source_ids: set[str] = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("v3 data_sources entries must be objects")
        _reject_unknown(source, SOURCE_FIELDS, "data source")
        missing_source = sorted({"id", "path", "format", "expected_sha256", "columns"} - set(source))
        if missing_source:
            raise ValueError(f"v3 data source missing fields: {', '.join(missing_source)}")
        if source.get("format") != "csv":
            raise ValueError("v3 data source format must be csv")
        if source["id"] in source_ids:
            raise ValueError(f"duplicate data source id: {source['id']}")
        source_ids.add(str(source["id"]))
    panels = spec.get("panels")
    if not isinstance(panels, list) or not panels:
        raise ValueError("v3 panels must be non-empty")
    panel_ids: set[str] = set()
    panel_required = {"panel_id", "visual_family", "variant", "encodings", "metric_direction", "statistics", "scales", "caption_obligations"}
    for panel in panels:
        if not isinstance(panel, dict):
            raise ValueError("v3 panel entries must be objects")
        _reject_unknown(panel, PANEL_FIELDS, "panel")
        missing_panel = sorted(panel_required - set(panel))
        if missing_panel:
            raise ValueError(f"v3 panel {panel.get('panel_id', '?')} missing fields: {', '.join(missing_panel)}")
        panel_id = str(panel["panel_id"])
        if panel_id in panel_ids:
            raise ValueError(f"duplicate panel id: {panel_id}")
        panel_ids.add(panel_id)
        panel_profile = panel.get("palette_profile") or {}
        _reject_unknown(panel_profile, {"mode", "family", "series_count", "background", "emphasis_role", "colors"}, "panel palette profile")
        if panel_profile.get("mode") == "custom" and len(panel_profile.get("colors") or []) < 2:
            raise ValueError(f"panel {panel_id} custom palette requires at least two colors")
        source_id = panel.get("source_id")
        if panel["visual_family"] not in {"method-schematic"} and not source_id:
            raise ValueError(f"v3 panel {panel_id} requires source_id")
        if source_id and source_id not in source_ids:
            raise ValueError(f"panel {panel_id} references unknown source_id: {source_id}")
        variants = VARIANTS.get(str(panel["visual_family"]))
        if variants and panel.get("variant") not in variants:
            raise ValueError(f"panel {panel_id} has unsupported variant: {panel.get('variant')}")
        for transform in panel.get("transforms") or []:
            if not isinstance(transform, dict) or transform.get("kind") not in TRANSFORMS:
                raise ValueError(f"panel {panel_id} has unsupported transform")
            _reject_unknown(transform, TRANSFORM_FIELDS[str(transform["kind"])], "transform")
        statistics = panel.get("statistics") or {}
        _reject_unknown(statistics, {"estimator", "aggregation", "uncertainty", "missing", "paired_id", "bins", "critical_difference", "significance"}, "statistics")
        if statistics.get("uncertainty"):
            _reject_unknown(statistics["uncertainty"], {"kind", "confidence", "bootstrap_samples", "seed"}, "uncertainty")
        if "significance" in statistics:
            significance = statistics.get("significance") or {}
            _reject_unknown(significance, {"source_column", "test_name", "adjustment"}, "significance")
            missing_significance = sorted({"source_column", "test_name", "adjustment"} - set(significance))
            if missing_significance:
                raise ValueError(f"significance annotations missing fields: {', '.join(missing_significance)}")
        scales = panel.get("scales") or {}
        _reject_unknown(scales, {"x", "y"}, "scales")
        for axis, scale in scales.items():
            _reject_unknown(scale or {}, {"type", "limits", "label", "unit"}, f"{axis} scale")
        for annotation in panel.get("annotations") or []:
            _reject_unknown(annotation, {"kind", "value", "x", "y", "text", "color", "linestyle", "linewidth", "fontsize", "axes_fraction", "ha", "va"}, "annotation")
        for node in panel.get("nodes") or []:
            _reject_unknown(node, {"id", "label", "x", "y", "width", "height", "kind", "shape", "shape_label", "ports"}, "node")
        for edge in panel.get("edges") or []:
            _reject_unknown(edge, {"from", "to", "label", "routing", "from_port", "to_port"}, "edge")
        for group in panel.get("groups") or []:
            _reject_unknown(group, {"id", "label", "x", "y", "width", "height", "color"}, "group")
        for lane in panel.get("lanes") or []:
            _reject_unknown(lane, {"id", "label", "y", "height", "color"}, "lane")
        if panel["visual_family"] == "qualitative-image-plate":
            required_image_encodings = {"image", "image_id", "crop_provenance", "aspect_ratio"}
            missing_image = sorted(required_image_encodings - set(panel.get("encodings") or {}))
            if missing_image:
                raise ValueError(f"v3 qualitative panel {panel_id} missing encodings: {', '.join(missing_image)}")


def normalize_spec(spec: dict[str, Any], spec_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return renderer-compatible data and an explicit migration record."""
    normalized = deepcopy(spec)
    version = int(normalized.get("spec_version", 1))
    migration = {"input_spec_version": version, "normalized_spec_version": 3, "actions": []}
    if version == 3:
        validate_v3_spec(normalized)
        registry = {str(item["id"]): item for item in normalized["data_sources"]}
        normalized["source_registry"] = registry
        for panel in normalized["panels"]:
            panel["_spec_version"] = 3
            if panel.get("source_id"):
                panel["data_source"] = str(registry[str(panel["source_id"])]["path"])
        migration["actions"].append("resolved v3 source registry")
        return normalized, migration
    if version not in {1, 2}:
        raise ValueError(f"unsupported spec_version: {version}")
    normalized.setdefault("panels", [])
    normalized.setdefault("shared_guides", {})
    normalized.setdefault("accessibility", {})
    normalized.setdefault("reproducibility", {"seed": 0})
    migration["actions"].append(f"migrated legacy v{version} defaults")
    return normalized, migration
