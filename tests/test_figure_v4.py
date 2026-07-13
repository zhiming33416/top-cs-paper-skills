from __future__ import annotations

import hashlib
import importlib.util
import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "top-cs-figure" / "scripts"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


core_data = load_module("figure_v4_data", SCRIPTS / "top_cs_figure_core" / "data.py")
core_stats = load_module("figure_v4_stats", SCRIPTS / "top_cs_figure_core" / "statistics.py")
core_spec = load_module("figure_v4_spec", SCRIPTS / "top_cs_figure_core" / "spec.py")
style = load_module("figure_v4_style", SCRIPTS / "cs_figure_style.py")
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
renderer = load_module("figure_v4_renderer", SCRIPTS / "render_from_figure_spec.py")
regressions = load_module("figure_v4_regressions", SCRIPTS / "run_private_figure_regressions.py")


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


class FigureV4Tests(unittest.TestCase):
    def test_manifest_schema_and_routes_are_v4(self):
        manifest = yaml.safe_load((ROOT / "skills" / "top-cs-figure" / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(manifest["version"], "4.1.0")
        self.assertTrue({"forest-interval", "composition-stacked", "paired-change", "polar-summary"}.issubset(manifest["axes"]["visual_family"]["values"]))
        self.assertTrue({"rendering-api", "data-statistics", "qa-contract", "tutorials"}.issubset(manifest["reference_routes"]))

    def test_v3_schema_is_closed_and_declares_strict_objects(self):
        schema = yaml.safe_load((ROOT / "skills" / "_shared" / "contracts" / "figure-render-spec.schema.yaml").read_text(encoding="utf-8"))
        self.assertFalse(schema["additionalProperties"])
        self.assertIn(3, schema["properties"]["spec_version"]["enum"])
        self.assertFalse(schema["$defs"]["source"]["additionalProperties"])
        self.assertFalse(schema["$defs"]["panel"]["additionalProperties"])

    def test_unknown_nested_fields_and_variants_are_rejected(self):
        fixture = yaml.safe_load((ROOT / "tests" / "fixtures" / "figure-specs" / "raw-bootstrap-v3.yaml").read_text(encoding="utf-8"))
        bad = yaml.safe_load(yaml.safe_dump(fixture)); bad["panels"][0]["statistics"]["secret"] = 1
        with self.assertRaisesRegex(ValueError, "unknown statistics"):
            core_spec.validate_v3_spec(bad)
        bad = yaml.safe_load(yaml.safe_dump(fixture)); bad["panels"][0]["variant"] = "decorative"
        with self.assertRaisesRegex(ValueError, "unsupported variant"):
            core_spec.validate_v3_spec(bad)

    def test_all_safe_transforms_are_deterministic(self):
        rows = [{"g":"a", "v":1, "b":1}, {"g":"a", "v":3, "b":1}, {"g":"b", "v":2, "b":1}]
        filtered, _ = core_data.apply_transforms(rows, [{"kind":"filter", "column":"g", "in":["a"]}])
        self.assertEqual(len(filtered), 2)
        aggregated, _ = core_data.apply_transforms(rows, [{"kind":"aggregate", "group_by":["g"], "metrics":{"score":{"column":"v", "op":"mean"}}}])
        self.assertEqual([item["score"] for item in aggregated], [2, 2])
        normalized, _ = core_data.apply_transforms(rows, [{"kind":"normalize", "column":"v", "output":"n"}])
        self.assertEqual([item["n"] for item in normalized], [0.0, 1.0, 0.5])
        delta, _ = core_data.apply_transforms(rows, [{"kind":"baseline-delta", "column":"v", "baseline_column":"b"}])
        self.assertEqual([item["v_delta"] for item in delta], [0, 2, 1])
        ranked, _ = core_data.apply_transforms(rows, [{"kind":"rank", "column":"v", "direction":"higher-is-better"}])
        self.assertEqual([item["v_rank"] for item in ranked], [3, 1, 2])

    def test_bootstrap_and_raw_run_summary_are_repeatable(self):
        values = [1, 2, 3, 5, 8]
        left = core_stats.bootstrap_interval(values, "mean", 0.95, 500, 11)
        right = core_stats.bootstrap_interval(values, "mean", 0.95, 500, 11)
        self.assertEqual(left, right)
        panel = {"encodings":{"x":"task", "series":"method", "raw_y":"score", "y":"mean"}, "statistics":{"estimator":"mean", "uncertainty":{"kind":"bootstrap-ci", "confidence":0.95, "bootstrap_samples":200, "seed":4}, "missing":"reject"}}
        output, report = core_stats.summarize_panel_rows([{"task":"A", "method":"M", "score":"1"}, {"task":"A", "method":"M", "score":"3"}], panel)
        self.assertEqual(output[0]["mean"], 2)
        self.assertEqual(output[0]["__n"], 2)
        self.assertEqual(report["seed"], 4)

    def test_semantic_identity_is_stable_across_order(self):
        first = style.semantic_style_registry("generic", ["Model X", "Model Y"])
        second = style.semantic_style_registry("generic", ["Model Y", "Model X"])
        self.assertEqual(first["Model X"], second["Model X"])
        self.assertEqual(first["Model Y"], second["Model Y"])

    def test_palette_profiles_use_all_anchors_and_record_provenance(self):
        for venue in ("www", "iclr", "icml"):
            categorical = style.resolve_palette_profile(venue, "categorical", 6)
            anchors = [item["hex"] for item in categorical["observed_anchors"]]
            self.assertEqual(anchors, style.venue_style_status(venue)["palette_candidates"])
            self.assertGreaterEqual(len(categorical["colors"]), 6)
            semantic = style.resolve_palette_profile(venue, "semantic", 5)
            self.assertEqual(semantic["semantic_roles"]["secondary"], anchors[3])
            self.assertIn("accessibility", categorical)
            for family in ("semantic", "ordered", "sequential", "diverging", "dark-overlay"):
                profile = style.resolve_palette_profile(venue, family, 7 if family in {"sequential", "diverging"} else 4, background="#20242A" if family == "dark-overlay" else "#FFFFFF")
                self.assertGreaterEqual(len(profile["colors"]), 2)
                self.assertIn("fallback_reason", profile)

    def test_custom_palette_rejects_indistinguishable_colors(self):
        with self.assertRaisesRegex(ValueError, "distinguishable"):
            style.resolve_palette_profile("generic", "categorical", 2, mode="custom", custom_colors=["#335577", "#345678"])

    def test_v3_palette_profile_is_closed(self):
        fixture = yaml.safe_load((ROOT / "tests" / "fixtures" / "figure-specs" / "raw-bootstrap-v3.yaml").read_text(encoding="utf-8"))
        fixture.setdefault("style", {})["palette_profile"] = {"mode": "generic", "family": "semantic", "series_count": 3}
        core_spec.validate_v3_spec(fixture)
        fixture["style"]["palette_profile"]["secret"] = True
        with self.assertRaisesRegex(ValueError, "unknown palette profile"):
            core_spec.validate_v3_spec(fixture)

    def test_quantitative_chart_variants_execute(self):
        import matplotlib.pyplot as plt

        comparison_rows = [{"x": x, "series": series, "y": str(value), "lower": str(value - 1), "upper": str(value + 1)} for x, base in (("A", 4), ("B", 6)) for series, value in (("Base", base), ("Ours", base + 2))]
        for variant in ("grouped-bar", "stacked-bar", "normalized-bar", "dot"):
            fig, ax = plt.subplots()
            try: renderer.render_comparison(ax, comparison_rows, {"variant":variant, "encodings":{"x":"x", "y":"y", "series":"series", "lower":"lower", "upper":"upper"}}, "generic")
            finally: plt.close(fig)
        fig, ax = plt.subplots()
        try: renderer.render_comparison(ax, [{"x":"A","y":"2"},{"x":"B","y":"-1"}], {"variant":"waterfall", "encodings":{"x":"x","y":"y"}}, "generic")
        finally: plt.close(fig)

        trend_rows = [{"x":str(x), "series":series, "y":str(x + offset), "run":"r1"} for series, offset in (("Base",0),("Ours",2)) for x in (1,2,3)]
        for variant in ("line", "line-band", "step", "area", "individual-runs", "learning-curve"):
            fig, ax = plt.subplots(); panel={"variant":variant,"encodings":{"x":"x","y":"y","series":"series","run":"run","raw_y":"y"},"_raw_rows":trend_rows}
            try: renderer.render_trend(ax, trend_rows, panel, "generic")
            finally: plt.close(fig)

        distribution_rows = [{"group":group,"value":str(value)} for group in ("A","B") for value in (1,2,3,4,5)]
        for variant in ("box", "violin", "strip", "histogram", "ecdf"):
            fig, ax = plt.subplots()
            try: renderer.render_distribution(ax, distribution_rows, {"variant":variant,"encodings":{"group":"group","value":"value"}}, "generic")
            finally: plt.close(fig)

        heatmap_rows = [{"row":row,"column":column,"value":str(value)} for row in ("A","B") for column,value in (("X",-1),("Y",1))]
        for variant in ("sequential", "diverging", "annotated", "confusion", "diverging-annotated"):
            fig, ax = plt.subplots()
            try: renderer.render_heatmap(ax, heatmap_rows, {"variant":variant,"encodings":{"row":"row","column":"column","value":"value"}}, "generic")
            finally: plt.close(fig)

        scatter_rows = [{"x":str(index),"y":str(index % 3),"label":f"P{index}","size":str(12 + index)} for index in range(8)]
        for variant in ("scatter", "bubble", "labeled"):
            fig, ax = plt.subplots()
            try: renderer.render_scatter(ax, scatter_rows, {"variant":variant,"encodings":{"x":"x","y":"y","label":"label","size":"size"}}, "generic")
            finally: plt.close(fig)
        fig, ax = plt.subplots()
        try: renderer.render_scatter(ax, scatter_rows, {"variant":"hexbin","encodings":{"x":"x","y":"y"}}, "generic")
        finally: plt.close(fig)

    def test_atlas_and_gallery_are_small_and_provenanced(self):
        root = ROOT / "skills" / "top-cs-figure" / "assets"
        manifest = yaml.safe_load((root / "generated-manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(len(manifest["records"]), 27)
        self.assertEqual(manifest["atlas_count"], 13)
        self.assertEqual(manifest["gallery_count"], 14)
        self.assertEqual(manifest["visual_example_count"], 222)
        self.assertLess(manifest["total_bytes"], 3 * 1024 * 1024)
        self.assertEqual(manifest["generator_sha256"], source_sha256(SCRIPTS / "build_figure_atlas.py"))
        self.assertEqual(manifest["renderer_sha256"], source_sha256(SCRIPTS / "render_from_figure_spec.py"))
        self.assertEqual(manifest["style_dependency_sha256"], source_sha256(SCRIPTS / "cs_figure_style.py"))
        for record in manifest["records"]:
            self.assertNotIn("\\", record["asset"])
            path = root / record["asset"]
            self.assertTrue(path.is_file())
            self.assertLessEqual(path.stat().st_size, 350 * 1024)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), record["sha256"])
            self.assertTrue(record["synthetic_csv_sha256"])
            self.assertTrue(record["synthetic_yaml_sha256"])
            self.assertTrue(record["production_renderer"])
            self.assertGreaterEqual(record["panel_count"], 6)

    def test_eval_matrix_is_executable_and_complete(self):
        matrix = yaml.safe_load((ROOT / "tests" / "figure-evals.yaml").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(matrix["cases"]), 30)
        required = {"fixture", "cli", "expected_files", "structural_assertions", "numeric_assertions", "qa_thresholds", "failure_mode"}
        self.assertTrue(all(required.issubset(case) for case in matrix["cases"]))

    def test_private_regression_interface_is_aggregate_only(self):
        report = regressions.run(ROOT / "tests" / "fixtures" / "private-regression-suite.yaml")
        self.assertEqual(report["passed"], 1)
        self.assertEqual(report["failed"], 0)
        self.assertTrue(report["aggregate_only"])
        import json
        serialized = json.dumps(report)
        self.assertNotIn("comparison.csv", serialized)
        self.assertNotIn(str(ROOT), serialized)


if __name__ == "__main__":
    unittest.main()
