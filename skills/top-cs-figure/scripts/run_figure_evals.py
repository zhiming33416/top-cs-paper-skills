#!/usr/bin/env python3
"""Execute the declarative synthetic top-cs-figure evaluation matrix."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import yaml
from PIL import Image, ImageChops

from audit_figure_spec import bundle_diff
from cs_figure_style import resolve_palette_profile
from render_from_figure_spec import apply_scales, render, render_paired, render_polar, validate_statistics
from top_cs_figure_core import apply_transforms, bootstrap_interval
from top_cs_figure_core.spec import validate_v3_spec


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "tests" / "fixtures" / "figure-specs"
SKILL = ROOT / "skills" / "top-cs-figure"
ASSET_MANIFEST = SKILL / "assets" / "generated-manifest.yaml"


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def _read_rows(path: str | Path) -> list[dict[str, str]]:
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _png_details(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgb = image.convert("RGB")
        bbox = ImageChops.difference(rgb, Image.new("RGB", rgb.size, "white")).getbbox()
        dpi = image.info.get("dpi")
        return {
            "size": image.size,
            "nonblank": bbox is not None,
            "dpi": min(float(value) for value in dpi) if dpi else None,
        }


def _svg_text_nodes(path: Path) -> list[str]:
    root = ET.fromstring(path.read_text(encoding="utf-8", errors="strict"))
    return ["".join(node.itertext()).strip() for node in root.iter() if node.tag.rsplit("}", 1)[-1] == "text"]


def _panel(context: dict[str, Any], panel_id: str) -> dict[str, Any]:
    return next(item for item in context["result"]["panels"] if item["panel_id"] == panel_id)


def _normalized_spec(context: dict[str, Any]) -> dict[str, Any]:
    return yaml.safe_load(Path(context["result"]["normalized_spec"]).read_text(encoding="utf-8"))


def _render_context(fixture: str, output: Path, cache: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if fixture not in cache:
        path = FIXTURES / fixture
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        cache[fixture] = {"result": render(spec, path, output / Path(fixture).stem), "spec": spec, "spec_path": path}
    return cache[fixture]


def _contract_context(case: dict[str, Any]) -> dict[str, Any]:
    structural = set(case["structural_assertions"])
    if str(case.get("fixture", "")).startswith("palette:"):
        _, venue, family = case["fixture"].split(":", 2)
        return {"palette": resolve_palette_profile(venue, family, 7 if family in {"sequential", "diverging"} else 4, background="#20242A" if family == "dark-overlay" else "#FFFFFF")}
    if "allow-list" in structural:
        rows, report = apply_transforms([{"x": "a"}, {"x": "b"}], [{"kind": "filter", "column": "x", "equals": "a"}])
        return {"rows": rows, "transform_report": report}
    if "grouped-output" in structural:
        rows, report = apply_transforms([{"g": "a", "v": 1}, {"g": "a", "v": 3}], [{"kind": "aggregate", "group_by": ["g"], "metrics": {"mean_v": {"column": "v", "op": "mean"}}}])
        return {"rows": rows, "transform_report": report}
    if "minmax" in structural:
        rows, report = apply_transforms([{"v": 2}, {"v": 4}], [{"kind": "normalize", "column": "v", "output": "n"}])
        return {"rows": rows, "transform_report": report}
    if "local-rng" in structural:
        left = bootstrap_interval([1, 2, 3, 4], "mean", 0.95, 200, 7)
        right = bootstrap_interval([1, 2, 3, 4], "mean", 0.95, 200, 7)
        return {"bootstrap_left": left, "bootstrap_right": right}
    raise AssertionError(f"no contract fixture registered for assertions: {sorted(structural)}")


def _expect_rejection(case: dict[str, Any]) -> dict[str, Any]:
    failure = case["failure_mode"]

    def unknown_field() -> None:
        spec = {"figure_id": "F", "claim_ids": ["C"], "venue": "generic", "data_sources": [], "panels": [], "output_base": "f", "export_formats": ["svg"], "evidence_status": "available", "unknown": 1}
        validate_v3_spec(spec)

    def missing_statistics() -> None:
        validate_statistics({"encodings": {"x": "x", "y": "y"}, "statistics": {"uncertainty": {"kind": "ci"}}}, [{"x": "a", "y": "1"}])

    def nonpositive_log() -> None:
        fig, ax = plt.subplots()
        try:
            apply_scales(ax, {"panel_id": "a", "visual_family": "trend-scaling", "encodings": {"x": "x"}, "scales": {"x": {"type": "log"}}}, [{"x": "0"}])
        finally:
            plt.close(fig)

    def significance_source() -> None:
        spec = {"figure_id": "F", "claim_ids": ["C"], "venue": "generic", "data_sources": [{"id": "s", "path": "x.csv", "format": "csv", "expected_sha256": None, "columns": ["x"]}], "panels": [{"panel_id": "a", "visual_family": "comparison", "variant": "dot", "source_id": "s", "encodings": {}, "metric_direction": "higher-is-better", "statistics": {"significance": {}}, "scales": {}, "caption_obligations": []}], "output_base": "f", "export_formats": ["svg"], "evidence_status": "available"}
        validate_v3_spec(spec)

    def incomplete_pairs() -> None:
        fig, ax = plt.subplots()
        try:
            render_paired(ax, [{"pair": "1", "condition": "a", "value": "1"}], {"encodings": {"pair": "pair", "condition": "condition", "value": "value"}}, "generic")
        finally:
            plt.close(fig)

    def polar_out_of_range() -> None:
        fig, ax = plt.subplots(subplot_kw={"projection": "polar"})
        try:
            rows = [{"axis": key, "value": value} for key, value in (("a", "1.2"), ("b", "0.5"), ("c", "0.6"))]
            render_polar(ax, rows, {"encodings": {"axis": "axis", "value": "value"}}, "generic")
        finally:
            plt.close(fig)

    def evidence_missing() -> None:
        path = FIXTURES / case["fixture"]
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
        spec["evidence_status"] = "missing"
        render(spec, path)

    operations: dict[str, Callable[[], None]] = {
        "unknown-field": unknown_field,
        "missing-statistics": missing_statistics,
        "nonpositive-log": nonpositive_log,
        "significance-source": significance_source,
        "incomplete-pairs": incomplete_pairs,
        "polar-out-of-range": polar_out_of_range,
        "evidence-missing": evidence_missing,
    }
    _check(failure in operations, f"unknown failure mode: {failure}")
    try:
        operations[failure]()
    except (ValueError, KeyError) as exc:
        return {"rejected": True, "error": str(exc), "failure_mode": failure}
    raise AssertionError(f"expected rejection: {failure}")


def _deep_context(case: dict[str, Any], output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    fixture = case["fixture"]
    if fixture == "synthetic:image-plate":
        images = []
        for index, color in enumerate(((50, 100, 160), (190, 120, 50)), 1):
            path = output / f"qual-{index}.png"
            Image.new("RGB", (80, 40), color).save(path)
            images.append(path)
        csv_path = output / "qual.csv"
        csv_path.write_text("image,image_id,crop_provenance,aspect_ratio,label\n" + "\n".join(f"{path.name},img-{index},uncropped,2.0,Case {index}" for index, path in enumerate(images, 1)), encoding="utf-8")
        spec_path = output / "qual.yaml"
        spec = {"spec_version": 3, "figure_id": "FQ", "claim_ids": ["CQ"], "venue": "generic", "data_sources": [{"id": "images", "path": csv_path.name, "format": "csv", "expected_sha256": None, "columns": ["image", "image_id", "crop_provenance", "aspect_ratio", "label"]}], "panels": [{"panel_id": "a", "visual_family": "qualitative-image-plate", "variant": "default", "source_id": "images", "encodings": {"image": "image", "image_id": "image_id", "crop_provenance": "crop_provenance", "aspect_ratio": "aspect_ratio", "label": "label"}, "statistics": {}, "scales": {}, "annotations": [], "semantic_roles": {}, "legend": "none", "metric_direction": "not-applicable", "caption_obligations": ["image IDs", "crop provenance"]}], "output_base": "qualitative", "export_formats": ["svg", "pdf", "png"], "evidence_status": "available"}
        spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
        return {"result": render(spec, spec_path, output / "qual-out"), "spec": spec, "image_count": len(images)}
    path = FIXTURES / fixture
    template = yaml.safe_load(path.read_text(encoding="utf-8"))
    if "tiff" in case["expected_files"]:
        spec = copy.deepcopy(template)
        spec["export_formats"] = ["svg", "pdf", "png", "tiff"]
        return {"result": render(spec, path, output / "camera"), "spec": spec}
    source = FIXTURES / "comparison.csv"
    before_csv, after_csv = output / "before.csv", output / "after.csv"
    original = source.read_text(encoding="utf-8")
    before_csv.write_text(original, encoding="utf-8")
    after_csv.write_text(original.replace("79.3", "80.3"), encoding="utf-8")
    before_spec, after_spec = copy.deepcopy(template), copy.deepcopy(template)
    before_spec["data_sources"], before_spec["output_base"] = [str(before_csv)], "revision"
    after_spec["data_sources"], after_spec["output_base"] = [str(after_csv)], "revision"
    before_path, after_path = output / "before.yaml", output / "after.yaml"
    before_path.write_text(yaml.safe_dump(before_spec), encoding="utf-8")
    after_path.write_text(yaml.safe_dump(after_spec), encoding="utf-8")
    before = render(before_spec, before_path, output / "before")
    after = render(after_spec, after_path, output / "after")
    return {"result": after, "before": before, "after": after, "diff": bundle_diff(Path(before["base"]), Path(after["base"]))}


def _asset_context(case: dict[str, Any]) -> dict[str, Any]:
    path = SKILL / case["fixture"]
    manifest = yaml.safe_load(ASSET_MANIFEST.read_text(encoding="utf-8"))
    record = next((item for item in manifest["records"] if Path(item["asset"]).name == path.name), None)
    return {"asset": path, "asset_manifest": manifest, "asset_record": record}


def _expected_file(context: dict[str, Any], name: str) -> Path | None:
    if "asset" in context:
        return context["asset"] if name == "png" else None
    result = context.get("result")
    if not result:
        return None
    base = Path(result["base"])
    mappings = {
        "svg": base.with_suffix(".svg"), "pdf": base.with_suffix(".pdf"), "png": base.with_suffix(".png"),
        "tiff": base.with_suffix(".tiff"), "render.json": Path(result["render_manifest"]),
        "normalized-spec.yaml": Path(result["normalized_spec"]),
    }
    if name == "plotted-data.csv":
        plotted = [Path(panel["plotted_data"]) for panel in result["panels"] if panel.get("plotted_data")]
        return plotted[0] if plotted else None
    return mappings.get(name)


def _assert_expected_files(case: dict[str, Any], context: dict[str, Any]) -> list[str]:
    executed = []
    for name in case["expected_files"]:
        path = _expected_file(context, name)
        _check(path is not None and path.is_file(), f"missing expected file {name}: {path}")
        executed.append(f"file:{name}")
    return executed


def _structural_assertion(name: str, context: dict[str, Any]) -> None:
    result = context.get("result")
    if name == "nonblank":
        _check(_png_details(Path(result["base"]).with_suffix(".png"))["nonblank"], "PNG is blank")
    elif name == "editable-svg-text":
        _check(bool(_svg_text_nodes(Path(result["base"]).with_suffix(".svg"))), "SVG lacks editable text nodes")
    elif name == "render-manifest":
        _check(Path(result["render_manifest"]).is_file() and result["spec_version"] == 3, "render manifest missing or stale")
    elif name == "source-hash":
        data_panels = [panel for panel in result["panels"] if panel["visual_family"] != "method-schematic"]
        _check(all(panel.get("data_hash") for panel in data_panels), "data-backed panel lacks source hash")
    elif name == "panel-a":
        _check(any(panel["panel_id"] == "a" for panel in result["panels"]), "panel a missing")
    elif name == "interval":
        panel = _panel(context, "a")
        rows = _read_rows(panel["plotted_data"])
        _check(all(key in rows[0] for key in ("estimate", "lower", "upper")), "forest interval columns missing")
    elif name == "null-line":
        panel = next(item for item in _normalized_spec(context)["panels"] if item["panel_id"] == "a")
        _check("null" in panel["encodings"], "forest null reference is undeclared")
    elif name in {"closed-schema", "explicit-aggregation", "log-domain", "explicit-test-source", "complete-pairs", "normalized-only", "evidence-boundary"}:
        _check(context.get("rejected") is True, f"{name} rejection was not enforced")
    elif name == "allow-list":
        _check(len(context["rows"]) == 1 and context["transform_report"][0]["kind"] == "filter", "filter allow-list failed")
    elif name == "grouped-output":
        _check(len(context["rows"]) == 1 and context["transform_report"][0]["kind"] == "aggregate", "aggregate output invalid")
    elif name == "minmax":
        _check([row["n"] for row in context["rows"]] == [0, 1], "min-max normalization failed")
    elif name == "local-rng":
        _check(context["bootstrap_left"] == context["bootstrap_right"], "bootstrap leaked global RNG state")
    elif name == "palette-profile":
        _check(context["palette"].get("family") and context["palette"].get("colors"), "palette profile was not resolved")
    elif name == "palette-provenance":
        palette = context["palette"]
        _check("observed_anchors" in palette and "constructed_tokens" in palette and "fallback_reason" in palette, "palette provenance is incomplete")
    elif name == "generic-fallback":
        _check(context["palette"].get("fallback_reason") is not None and not context["palette"].get("observed_anchors"), "generic fallback boundary was not recorded")
    elif name == "provenance":
        _check(context["asset_record"] is not None and context["asset_record"].get("synthetic_yaml_sha256") and context["asset_record"].get("synthetic_csv_sha256"), "asset provenance missing")
    elif name == "production-renderer":
        _check(context["asset_record"].get("production_renderer") is True, "asset bypassed production renderer")
    elif name in {"image-id", "crop-provenance", "aspect-ratio"}:
        rows = _read_rows(_panel(context, "a")["plotted_data"])
        column = {"image-id": "image_id", "crop-provenance": "crop_provenance", "aspect-ratio": "aspect_ratio"}[name]
        _check(all(row.get(column) for row in rows), f"qualitative image {column} missing")
    elif name == "camera-ready-bundle":
        _check(all(Path(result["base"]).with_suffix(f".{ext}").is_file() for ext in ("svg", "pdf", "png", "tiff")), "camera-ready bundle incomplete")
    elif name in {"normalized-spec-diff", "plotted-data-diff", "svg-diff", "png-diff"}:
        diff = context["diff"]
        checks = {
            "normalized-spec-diff": diff["render_manifest"]["normalized_spec_hash_changed"],
            "plotted-data-diff": bool(diff["render_manifest"]["panels"]),
            "svg-diff": bool(diff["svg"]["added_text"] or diff["svg"]["removed_text"] or diff["render_manifest"]["panels"]),
            "png-diff": diff["png"].get("changed_pixel_fraction", 0) > 0,
        }
        _check(bool(checks[name]), f"{name} not detected")
    else:
        raise AssertionError(f"unregistered structural assertion: {name}")


def _numeric_assertion(name: str, context: dict[str, Any]) -> None:
    result = context.get("result")
    if name in {"mean", "bootstrap-ci", "n", "deterministic-seed"} and result:
        panel = result["panels"][0]
        rows = _read_rows(panel["plotted_data"])
        if name == "mean":
            values = [float(row.get("estimate", row.get("mean_v", "nan"))) for row in rows]
            _check(all(value == value for value in values), "computed mean missing")
        elif name == "bootstrap-ci":
            _check(all(float(row["__lower"]) <= float(row["estimate"]) <= float(row["__upper"]) for row in rows), "bootstrap interval does not contain estimate")
        elif name == "n":
            _check(all(int(row["__n"]) > 1 for row in rows), "sample count missing")
        else:
            _check(panel["statistics"].get("seed") == 19, "deterministic seed not recorded")
    elif name == "composition-sums-to-one":
        rows = _read_rows(_panel(context, "b")["plotted_data"])
        totals: dict[str, float] = {}
        for row in rows:
            totals[row["x"]] = totals.get(row["x"], 0.0) + float(row["value"])
        _check(all(abs(sum(value / total for value in [float(row["value"]) for row in rows if row["x"] == key]) - 1) < 1e-9 for key, total in totals.items()), "composition normalization invalid")
    elif name == "three-complete-pairs":
        rows = _read_rows(_panel(context, "c")["plotted_data"])
        pairs: dict[str, set[str]] = {}
        for row in rows:
            pairs.setdefault(row["pair"], set()).add(row["condition"])
        _check(len(pairs) == 3 and all(len(values) == 2 for values in pairs.values()), "paired fixture is incomplete")
    elif name == "range-zero-one":
        rows = context.get("rows") or _read_rows(_panel(context, "d")["plotted_data"])
        key = "n" if rows and "n" in rows[0] else "value"
        _check(all(0 <= float(row[key]) <= 1 for row in rows), "values fall outside [0, 1]")
    elif name == "row-count":
        _check(len(context["rows"]) == 1, "unexpected row count")
    elif name == "mean":
        _check(float(context["rows"][0]["mean_v"]) == 2, "aggregate mean is incorrect")
    elif name == "same-seed-same-result":
        _check(context["bootstrap_left"] == context["bootstrap_right"], "same bootstrap seed changed result")
    elif name == "under-350kb":
        _check(context["asset"].stat().st_size <= 350 * 1024, "asset exceeds 350 KB")
    elif name == "two-images":
        _check(context.get("image_count") == 2, "qualitative plate image count changed")
    elif name == "minimum-300-dpi":
        details = _png_details(Path(result["base"]).with_suffix(".png"))
        _check(details["dpi"] is not None and details["dpi"] >= 299, f"camera-ready PNG DPI too low: {details['dpi']}")
    elif name == "changed-pixel-fraction":
        fraction = context["diff"]["png"].get("changed_pixel_fraction", 0)
        _check(0 < fraction <= 1, f"invalid changed-pixel fraction: {fraction}")
    elif name == "profile-colors":
        _check(2 <= len(context["palette"]["colors"]) <= 9, "palette profile color count is invalid")
    elif name == "profile-accessibility":
        _check(not context["palette"]["accessibility"]["violations"]["large_fill"], "palette has low-contrast fill colors")
    elif name == "monotonic-ramp":
        colors = context["palette"]["colors"]
        from top_cs_figure_core.color import relative_luminance
        values = [relative_luminance(color) for color in colors]
        direction = 1 if values[-1] > values[0] else -1
        _check(all(direction * (right - left) > 0 for left, right in zip(values, values[1:])), "palette ramp is not monotonic")
    elif name == "neutral-center":
        colors = context["palette"]["colors"]
        from top_cs_figure_core.color import hex_to_rgb, rgb_to_oklab
        _, a, b = rgb_to_oklab(hex_to_rgb(colors[len(colors) // 2]))
        _check((a * a + b * b) ** 0.5 < 0.035, "diverging center is not neutral")
    else:
        raise AssertionError(f"unregistered numeric assertion: {name}")


def _assert_qa(case: dict[str, Any], context: dict[str, Any]) -> list[str]:
    executed = []
    for name, threshold in case["qa_thresholds"].items():
        if name == "minimum_png_dpi":
            path = context.get("asset") or Path(context["result"]["base"]).with_suffix(".png")
            details = _png_details(path)
            dpi = details["dpi"]
            _check(dpi is not None and dpi + 1 >= float(threshold), f"PNG DPI {dpi} below {threshold}")
        elif name == "minimum_pixel_width":
            path = context.get("asset") or Path(context["result"]["base"]).with_suffix(".png")
            width = _png_details(path)["size"][0]
            _check(width >= int(threshold), f"PNG width {width} below {threshold} pixels")
        elif name in {"minimum_text_pt", "minimum_line_width_pt"}:
            geometry = context["result"]["geometry"]["panels"].values()
            if name == "minimum_text_pt":
                values = [text["font_pt"] for panel in geometry for text in panel["texts"]]
            else:
                values = [value for panel in geometry for value in panel["line_widths_pt"] if value > 0]
            if values:
                _check(min(values) + 1e-6 >= float(threshold), f"{name} {min(values):.3f} below {threshold}")
        else:
            raise AssertionError(f"unregistered QA threshold: {name}")
        executed.append(f"qa:{name}")
    return executed


def run(matrix: Path) -> dict[str, object]:
    document = yaml.safe_load(matrix.read_text(encoding="utf-8"))
    cases, results = document["cases"], []
    with tempfile.TemporaryDirectory() as temporary:
        output, cache = Path(temporary), {}
        for case in cases:
            mode = case["mode"]
            if mode == "render":
                context = _render_context(case["fixture"], output, cache)
                _check(len(context["result"]["panels"]) == int(case["expect_panels"]), "panel count mismatch")
            elif mode == "contract":
                context = _contract_context(case)
            elif mode == "reject":
                context = _expect_rejection(case)
            elif mode == "asset":
                context = _asset_context(case)
            elif mode == "deep":
                context = _deep_context(case, output / case["id"])
            else:
                raise AssertionError(f"unsupported eval mode: {mode}")
            executed = _assert_expected_files(case, context)
            for assertion in case["structural_assertions"]:
                _structural_assertion(assertion, context)
                executed.append(f"structure:{assertion}")
            for assertion in case["numeric_assertions"]:
                _numeric_assertion(assertion, context)
                executed.append(f"numeric:{assertion}")
            executed.extend(_assert_qa(case, context))
            results.append({"id": case["id"], "passed": True, "assertions_executed": executed})
    return {"schema_version": document["schema_version"], "passed": len(results), "failed": 0, "cases": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--matrix", type=Path, default=ROOT / "tests" / "figure-evals.yaml")
    args = parser.parse_args()
    print(json.dumps(run(args.matrix.resolve()), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
