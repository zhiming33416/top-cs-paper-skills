from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


collector = load_script("collect_public_sources")
visual_collector = load_script("collect_visual_style_corpus")
router = load_script("route_skill")
evaluator = load_script("evaluate_skill_output")
validator = load_script("validate_evidence")
derive = load_script("derive_corpus_evidence")
visual_derive = load_script("derive_visual_style_evidence")


def load_latex_checker():
    path = ROOT / "skills" / "top-cs-polishing" / "scripts" / "check_latex_project.py"
    spec = importlib.util.spec_from_file_location("check_latex_project", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


latex_checker = load_latex_checker()


def load_skill_script(skill: str, name: str):
    path = ROOT / "skills" / skill / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"{skill}_{name}", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


figure_checker = load_skill_script("top-cs-figure", "check_figure_bundle")
figure_style = load_skill_script("top-cs-figure", "cs_figure_style")
figure_renderer = load_skill_script("top-cs-figure", "render_from_figure_spec")
figure_audit = load_skill_script("top-cs-figure", "audit_figure_spec")


class CollectionConfigTests(unittest.TestCase):
    def test_public_collection_config_is_safe_and_unique(self):
        config = collector.load_config(ROOT / "public-sources.yaml")
        self.assertTrue(config["collection_policy"]["public_only"])
        self.assertTrue(all(item["url"].startswith("https://") for item in config["sources"]))
        self.assertEqual(len(config["sources"]), len({item["relative_path"] for item in config["sources"]}))

    def test_visual_style_openreview_and_www_discovery_fixtures(self):
        openreview_payload = (ROOT / "tests" / "fixtures" / "visual-style" / "openreview-notes.json").read_text(encoding="utf-8")
        openreview = visual_collector.parse_openreview_notes(openreview_payload, "iclr", 2026, target_per_venue=10)
        self.assertEqual([row["track"] for row in openreview], ["Poster", "Oral"])
        self.assertTrue(all(row["public_url"].startswith("https://openreview.net/pdf?id=") for row in openreview))

        www_payload = (ROOT / "tests" / "fixtures" / "visual-style" / "www-accepted.html").read_text(encoding="utf-8")
        www = visual_collector.parse_www_research_html(www_payload, 2026, target_per_venue=2)
        self.assertEqual([row["source_id"] for row in www], ["www2026-rfp0134", "www2026-rfp0524"])
        self.assertTrue(all(row["track"] == "Research" and row["eligibility"] == "holdout" for row in www))

    def test_visual_style_collector_dry_run_uses_external_paths_only(self):
        candidate = {
            "source_id": "iclr2026-fixture",
            "venue": "iclr",
            "conference": "ICLR2026",
            "year": 2026,
            "track": "Poster",
            "title": "Robust Agents for Long-Horizon Planning",
            "title_fingerprint": visual_collector.title_fingerprint("Robust Agents for Long-Horizon Planning"),
            "public_url": "https://openreview.net/pdf?id=fixture",
            "source_page_url": "https://openreview.net/forum?id=fixture",
            "source_kind": "openreview-accepted",
            "license": "openreview-public-paper-pdf",
            "eligibility": "holdout",
            "verification_status": "not-downloaded",
            "collection_status": "candidate",
        }
        with tempfile.TemporaryDirectory() as tmp:
            manifest = visual_collector.collect(Path(tmp), Path(tmp) / "manifest.yaml", ["iclr"], dry_run=True, target_per_venue=1, candidates=[candidate])
            row = manifest["sources"][0]
            self.assertEqual(row["collection_status"], "would-download")
            self.assertTrue(row["relative_path"].startswith("papers/ICLR2026/verified_fulltext/"))
            self.assertFalse((Path(tmp) / row["relative_path"]).exists())


class RoutingTests(unittest.TestCase):
    def test_writing_route_resolves_static_and_runtime_inputs(self):
        result = router.resolve("top-cs-writing", {
            "venue": "iclr", "paper_type": "theoretical", "section": ["introduction", "method"],
            "language": "en", "artifact_scope": "full-manuscript", "evidence_state": "partial",
            "submission_stage": "pre-submission",
        })
        self.assertFalse(result["missing_parameters"])
        self.assertEqual(result["route"]["venue"], "iclr")
        self.assertTrue(any(path.endswith("theoretical.md") for path in result["load_files"]))
        self.assertEqual(result["policy_freshness"]["status"], "current")

    def test_unsupported_year_uses_generic(self):
        result = router.resolve("top-cs-writing", {
            "venue": "iclr", "paper_type": "empirical", "section": ["abstract"], "language": "en",
        }, year=2027)
        self.assertEqual(result["route"]["venue"], "generic")
        self.assertIsNotNone(result["generic_fallback_reason"])
        self.assertTrue(result["missing_policy_categories"])
        self.assertIn("reviewer-guide", result["missing_policy_categories"])

    def test_supported_routes_report_only_real_policy_gaps(self):
        www = router.resolve("top-cs-writing", {
            "venue": "www", "paper_type": "empirical", "section": ["abstract"], "language": "en",
        })
        self.assertIn("reviewer-guide", www["missing_policy_categories"])
        self.assertIn("review-form", www["missing_policy_categories"])
        self.assertNotIn("anonymity", www["missing_policy_categories"])

    def test_response_remains_parameterized_without_axes(self):
        result = router.resolve("top-cs-response", {"venue": "icml"})
        self.assertEqual(result["route"], {})
        self.assertEqual(result["runtime_parameters"]["venue"], "icml")

    def test_full_section_route_selects_reference_deterministically(self):
        result = router.resolve("top-cs-writing", {
            "venue": "www", "paper_type": "empirical", "section": ["experiments", "discussion"], "language": "en",
        })
        self.assertIn("full-section-corpus", result["automatic_needs"])
        self.assertTrue(any(item["path"].endswith("full-section-corpus-patterns.md") for item in result["selected_references"]))
        self.assertTrue(any(path.endswith("full-section-corpus-patterns.md") for path in result["load_files"]))

    def test_explicit_reference_need_and_unknown_need(self):
        result = router.resolve("top-cs-polishing", {"venue": "generic", "paper_type": "empirical", "section": ["abstract"], "language": "en"}, needs=["claim-strength", "not-a-route"])
        self.assertIn("not-a-route", result["unknown_needs"])
        self.assertTrue(any(item["need"] == "claim-strength" for item in result["selected_references"]))

    def test_citation_figure_and_stress_capabilities_select_contracts(self):
        result = router.resolve("top-cs-response", {
            "venue": "iclr", "citation_verification": "metadata", "figure_handoff": "track", "stress_test": "up-to-3-rounds",
        })
        self.assertEqual(result["capability_status"]["citation_verification"], "metadata")
        self.assertIn("citation-verification", result["automatic_needs"])
        self.assertIn("figure-handoff", result["automatic_needs"])
        self.assertIn("response-stress-test", result["automatic_needs"])
        self.assertTrue(any(path.endswith("citation-record.schema.yaml") for path in result["selected_contracts"]))
        self.assertTrue(any(path.endswith("figure-brief.schema.yaml") for path in result["selected_contracts"]))
        self.assertTrue(any(path.endswith("response-issue.schema.yaml") for path in result["selected_contracts"]))

    def test_figure_route_resolves_visual_family_and_runtime_inputs(self):
        result = router.resolve("top-cs-figure", {
            "venue": "iclr",
            "paper_type": "empirical",
            "visual_family": "trend-scaling",
            "figure_task": "export-bundle",
            "data_state": "available",
            "output_target": "camera-ready",
            "figure_handoff": "consume",
        })
        self.assertFalse(result["missing_parameters"])
        self.assertEqual(result["route"]["visual_family"], "trend-scaling")
        self.assertEqual(result["runtime_parameters"]["figure_task"], "export-bundle")
        self.assertIn("figure-contract", result["automatic_needs"])
        self.assertIn("python-workflow", result["automatic_needs"])
        self.assertIn("visual-qa", result["automatic_needs"])
        self.assertIn("visual-style", result["automatic_needs"])
        self.assertIn("palette-policy", result["automatic_needs"])
        self.assertIn("statistics", result["automatic_needs"])
        self.assertIn("figure-handoff", result["automatic_needs"])
        self.assertTrue(any(path.endswith("figure-brief.schema.yaml") for path in result["selected_contracts"]))
        self.assertTrue(any(path.endswith("figure-render-spec.schema.yaml") for path in result["selected_contracts"]))
        self.assertTrue(any(path.endswith("cs_figure_style.py") for path in result["load_files"]))
        self.assertTrue(any(path.endswith("static/fragments/venue-style/iclr.md") for path in result["load_files"]))
        self.assertTrue(any(path.endswith("visual-style-rules.yaml") for path in result["load_files"]))


class EvaluationTests(unittest.TestCase):
    def test_output_contract_pass_and_failure(self):
        case = {"id": "x", "skill": "top-cs-response", "must_include": ["Issue matrix"], "must_not_include": ["experiment completed"]}
        self.assertTrue(evaluator.evaluate(case, "Issue matrix\nplanned experiment")["passed_automatic_checks"])
        self.assertFalse(evaluator.evaluate(case, "experiment completed")["passed_automatic_checks"])

    def test_multi_case_loader_requires_case_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cases.yaml"
            path.write_text(yaml.safe_dump({"cases": [{"id": "a"}]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                evaluator.load_case(path, None)

    def test_case_source_file_can_be_resolved_by_cli_contract(self):
        case_path = ROOT / "tests" / "deep-acceptance-cases.yaml"
        case = evaluator.load_case(case_path, "deep-writing-abstract-fidelity")
        source = (case_path.parent / case["source_file"]).resolve()
        self.assertTrue(source.is_file())
        self.assertIn("42.7%", source.read_text(encoding="utf-8"))

    def test_structured_semantic_contract_preserves_source_artifacts(self):
        case = {
            "id": "semantic", "skill": "top-cs-polishing",
            "semantic_contract": {
                "required_sections": ["Revised text"],
                "fact_invariants": ["Dataset-X"],
                "preserve_from_source": ["numbers", "citations", "labels"],
                "forbidden_claim_patterns": [r"experiment completed"],
                "required_claim_statuses": {"C1": "partial"},
                "required_table_columns": [["Claim", "Status"]],
            },
        }
        source = r"Dataset-X improves by 12.5% \cite{smith2024}. See \ref{tab:main}."
        output = "# Revised text\nDataset-X improves by 12.5% \\cite{smith2024}. See \\ref{tab:main}.\n| Claim | Status |\n| C1 | partial |"
        result = evaluator.evaluate(case, output, source)
        self.assertTrue(result["passed_automatic_checks"], result["failures"])

    def test_structured_semantic_contract_detects_number_drift(self):
        case = {"semantic_contract": {"preserve_from_source": ["numbers"]}}
        result = evaluator.evaluate(case, "Accuracy is 91%.", "Accuracy is 89%.")
        self.assertFalse(result["passed_automatic_checks"])
        self.assertTrue(any("89" in item for item in result["failures"]))

    def test_contract_fields_round_limit_and_citation_boundary(self):
        case = {"semantic_contract": {
            "required_record_fields": {"figure": ["figure_id", "claim_ids", "caption_draft"]},
            "forbidden_status_transitions": [["planned", "verified"]],
            "max_round": 3,
            "forbid_metadata_as_claim_support": True,
        }}
        good = "figure_id: F1\nclaim_ids: [C1]\ncaption_draft: Test\nRound 3\nmetadata-verified; claim entailment not checked"
        self.assertTrue(evaluator.evaluate(case, good)["passed_automatic_checks"])
        bad = "figure_id: F1\nplanned -> verified\nRound 4\nmetadata-verified therefore supports the claim"
        result = evaluator.evaluate(case, bad)
        self.assertFalse(result["passed_automatic_checks"])
        self.assertGreaterEqual(len(result["failures"]), 3)


class StructureExtractionTests(unittest.TestCase):
    def test_combined_and_numbered_headings_are_detected(self):
        text = "1. Introduction\n2. Problem Formulation\n3. Experiments and Results\n4. Limitations and Future Work\n5. Concluding Remarks\nReferences\n"
        sections = [name for name, _ in derive.heading_events(text)]
        self.assertEqual(sections, ["introduction", "method", "experiments", "limitations", "conclusion", "references"])

    def test_pdf_outline_supplements_missing_text_headings(self):
        features = derive.structural_features("Introduction\nText\nReferences", ["Introduction", "References"], ["Method", "Discussion and Implications"])
        self.assertIn("method", features["section_order"])
        self.assertEqual(features["section_detection"]["method"]["evidence"], "pdf-outline")


class LatexCheckerTests(unittest.TestCase):
    def test_root_detection_and_safe_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            (project / "main.tex").write_text(r"\documentclass{article}\begin{document}x\end{document}", encoding="utf-8")
            root = latex_checker.find_root(project)
            command = latex_checker.command_for("pdflatex", root, project / "out")
            self.assertEqual(root.name, "main.tex")
            self.assertIn("-no-shell-escape", command)

    def test_log_analysis(self):
        log = "LaTeX Warning: Citation `x' on page 1 undefined.\nLaTeX Warning: Reference `fig:a' undefined.\nOverfull \\hbox\n! Undefined control sequence."
        findings = latex_checker.analyze_log(log)
        self.assertEqual(findings["undefined_citations"], ["x"])
        self.assertEqual(findings["undefined_references"], ["fig:a"])
        self.assertEqual(findings["overfull_boxes"], 1)


class FigureToolTests(unittest.TestCase):
    def test_style_helpers_without_matplotlib_runtime(self):
        self.assertEqual(figure_style.size_mm(25.4, 50.8), (1.0, 2.0))
        self.assertEqual(figure_style.require_columns(["dataset", "method"], ["dataset", "score"]), ["score"])
        self.assertIn("ours", figure_style.PALETTE)
        self.assertIn("ours", figure_style.palette_for("icml"))
        self.assertGreater(figure_style.contrast_ratio("#000000", "#FFFFFF"), 10)

    def test_check_figure_bundle_pass_and_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "fig1"
            base.with_suffix(".svg").write_text('<svg viewBox="0 0 10 10"><text x="0" y="8" style="font-size: 7px; font-family: sans-serif">a</text><path fill="#2F5DAA"/></svg>', encoding="utf-8")
            base.with_suffix(".pdf").write_bytes(b"%PDF-1.7\n")
            base.with_suffix(".png").write_bytes(bytes.fromhex("89504e470d0a1a0a") + b"\n")
            result = figure_checker.inspect_bundle(base, expected_panels=["a"], expected_colors=["#2F5DAA"], caption="a main panel", callout="Figure 1 shows C1.")
            self.assertTrue(result["passed"], result)
            base.with_suffix(".png").unlink()
            result = figure_checker.inspect_bundle(base)
            self.assertFalse(result["passed"])
            self.assertTrue(any(item.endswith("fig1.png") for item in result["missing"]))

    def test_render_from_figure_spec_comparison_trend_and_heatmap(self):
        for name in ("comparison", "trend", "heatmap"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                outdir = Path(tmp)
                spec = ROOT / "tests" / "fixtures" / "figure-specs" / f"{name}.yaml"
                result = figure_renderer.render(yaml.safe_load(spec.read_text(encoding="utf-8")), spec, outdir)
                self.assertEqual(len(result["saved"]), 3)
                self.assertTrue((outdir / f"{name}.svg").is_file())
                check = figure_checker.inspect_bundle(outdir / name, expected_panels=["a"])
                self.assertTrue(check["passed"], check)

    def test_render_v2_mosaic_and_audit_provenance(self):
        spec_path = ROOT / "tests" / "fixtures" / "figure-specs" / "multipanel-ablation.yaml"
        spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            outdir = Path(tmp)
            result = figure_renderer.render(spec, spec_path, outdir)
            self.assertEqual(result["spec_version"], 3)
            self.assertEqual(result["migration"]["input_spec_version"], 2)
            self.assertEqual([panel["panel_id"] for panel in result["panels"]], ["a", "b", "c", "d"])
            check = figure_checker.inspect_bundle(outdir / "multipanel-ablation", expected_panels=["a", "b", "c", "d"], metric_direction="higher-is-better")
            self.assertTrue(check["passed"], check)
            self.assertTrue(check["files"][2]["nonblank"])
            audit = figure_audit.audit(spec_path, outdir / "multipanel-ablation")
            self.assertTrue(audit["passed"], audit)
            self.assertTrue(audit["style_evidence"]["rules_sha256"])
            self.assertEqual(figure_audit.bundle_diff(outdir / "multipanel-ablation", outdir / "multipanel-ablation")["png"]["changed_pixel_fraction"], 0.0)

    def test_render_new_families_and_rejects_incomplete_statistics(self):
        fixtures = ROOT / "tests" / "fixtures" / "figure-specs"
        for name in ("distribution", "ranking", "schematic"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                spec_path = fixtures / f"{name}.yaml"
                result = figure_renderer.render(yaml.safe_load(spec_path.read_text(encoding="utf-8")), spec_path, Path(tmp))
                self.assertEqual(len(result["saved"]), 3)
        bad = yaml.safe_load((fixtures / "multipanel-ablation.yaml").read_text(encoding="utf-8"))
        bad["panels"][0]["statistics"].pop("aggregation")
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "aggregation"):
                figure_renderer.render(bad, fixtures / "multipanel-ablation.yaml", Path(tmp))

    def test_render_qualitative_image_plate_requires_user_files(self):
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, color in (("one.png", "#336699"), ("two.png", "#CC8844")):
                Image.new("RGB", (80, 40), color).save(root / name)
            (root / "plate.csv").write_text("image,label\none.png,Input\ntwo.png,Output\n", encoding="utf-8")
            spec = {
                "spec_version": 2, "figure_id": "Figure Q1", "claim_ids": ["C-Q1"], "venue": "generic",
                "visual_family": "qualitative-image-plate", "data_sources": ["plate.csv"], "panel_map": [{"panel_id": "a", "job": "examples"}],
                "encodings": {"image": "image"}, "metric_direction": "not-applicable", "output_base": "plate", "export_formats": ["svg", "pdf", "png"], "evidence_status": "partial",
                "layout": {"kind": "grid", "rows": 1, "columns": 1},
                "panels": [{"panel_id": "a", "visual_family": "qualitative-image-plate", "data_source": "plate.csv", "encodings": {"image": "image", "label": "label"}}],
            }
            spec_path = root / "plate.yaml"
            spec_path.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
            result = figure_renderer.render(spec, spec_path, root)
            self.assertTrue((root / "plate.svg").is_file())
            self.assertEqual(result["panels"][0]["visual_family"], "qualitative-image-plate")
            spec["panels"][0]["encodings"]["image"] = "missing"
            with self.assertRaises(ValueError):
                figure_renderer.render(spec, spec_path, root)

    def test_palette_requires_promoted_style_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            evidence = Path(tmp)
            rules = {"rules": {"www": {"status": "promoted", "palette_status": "usable", "eligible_sources": 10, "palette_candidates": ["#123456", "#345678", "#56789A"]}, "iclr": {"status": "preliminary", "palette_status": "insufficient", "eligible_sources": 4, "palette_candidates": ["#ABCDEF"]}}}
            (evidence / "visual-style-rules.yaml").write_text(yaml.safe_dump(rules), encoding="utf-8")
            self.assertEqual(figure_style.palette_for("www", evidence)["ours"], "#123456")
            self.assertEqual(figure_style.palette_for("iclr", evidence)["ours"], figure_style.PALETTE["ours"])
            self.assertEqual(figure_style.venue_style_status("iclr", evidence)["status"], "preliminary")

    def test_visual_style_palette_requires_independent_source_prevalence(self):
        records = []
        for index in range(10):
            colors = [{"hex": "#ABCDEF", "count": 10000, "source": "vector"}] if index == 0 else []
            if index < 3:
                colors.append({"hex": "#2468AC", "count": 2, "source": "vector"})
            if 3 <= index < 6:
                colors.append({"hex": "#D06040", "count": 2, "source": "vector"})
            if 6 <= index < 9:
                colors.append({"hex": "#3C9A60", "count": 2, "source": "vector"})
            records.append({"source_id": f"www-{index}", "venue": "www", "eligibility": "style-evidence", "color_clusters": colors, "layout_archetypes": ["quantitative-grid"]})
        _stats, rules = visual_derive.promote_rules(records, target_per_venue=10)
        self.assertIn("#2468AC", rules["rules"]["www"]["palette_candidates"])
        self.assertNotIn("#ABCDEF", rules["rules"]["www"]["palette_candidates"])

    def test_palette_evidence_clusters_nearby_export_colors_by_hue_family(self):
        colors = ("#2070B0", "#306090", "#3080C0")
        records = []
        for index in range(12):
            palette = []
            if index < 4:
                palette.append({"hex": colors[index % len(colors)], "count": 5, "source": "figure-vector"})
            if 4 <= index < 8:
                palette.append({"hex": "#D06040", "count": 5, "source": "figure-vector"})
            if 8 <= index < 12:
                palette.append({"hex": "#3C9A60", "count": 5, "source": "figure-vector"})
            records.append({"source_id": f"icml-{index}", "venue": "icml", "eligibility": "style-evidence", "color_clusters": palette, "layout_archetypes": ["quantitative-grid"]})
        _stats, rules = visual_derive.promote_rules(records)
        rule = rules["rules"]["icml"]
        self.assertEqual(rule["palette_status"], "usable")
        self.assertEqual(len(rule["palette_candidates"]), 3)
        self.assertGreaterEqual(rule["palette_candidate_support"][0]["contrast_on_white"], 1.8)

    def test_promoted_style_without_three_distinct_colors_keeps_generic_palette(self):
        records = [
            {"source_id": f"iclr-{index}", "venue": "iclr", "eligibility": "style-evidence", "color_clusters": [{"hex": "#2468AC", "count": 3, "source": "figure-vector"}], "layout_archetypes": ["quantitative-grid"]}
            for index in range(10)
        ]
        _stats, rules = visual_derive.promote_rules(records, target_per_venue=10)
        rule = rules["rules"]["iclr"]
        self.assertEqual(rule["status"], "promoted")
        self.assertEqual(rule["palette_status"], "insufficient")
        self.assertEqual(rule["palette_fallback_reason"], "promoted-no-usable-palette")

    def test_icml_virtual_parser_and_candidate_merge_prefer_official_pdf(self):
        payload = {"results": [{"id": "p1", "name": "Exact Accepted Title", "paper_pdf_url": "/papers/p1.pdf", "eventtype": "Poster"}]}
        official = visual_collector.parse_icml_virtual_papers(payload, target_per_venue=2)[0]
        indexed = dict(official)
        indexed.update({"public_url": None, "source_kind": "corpus-index-public-version", "source_priority": 80, "candidate_discovery_sources": ["accepted-title-corpus-index"]})
        merged = visual_collector.merge_candidates([indexed, official])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["source_kind"], "icml-virtual-official")
        self.assertIn("accepted-title-corpus-index", merged[0]["candidate_discovery_sources"])

        no_pdf = visual_collector.parse_icml_virtual_papers({"results": [{"id": "p2", "name": "Accepted Without Hosted PDF", "paper_pdf_url": None, "eventtype": "Poster", "decision": "Accept (regular)"}]})[0]
        self.assertIsNone(no_pdf["public_url"])
        self.assertEqual(no_pdf["source_kind"], "icml-virtual-official")

    def test_candidate_limit_prefers_existing_or_public_rows_and_caps_each_venue(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            existing = root / "papers" / "WWW2026" / "verified_fulltext" / "known.pdf"
            existing.parent.mkdir(parents=True)
            existing.write_bytes(b"%PDF-test")
            rows = [
                {"venue": "www", "title": f"Holdout {index}", "source_priority": 70}
                for index in range(5)
            ]
            rows.append({"venue": "www", "title": "Known", "relative_path": "papers/WWW2026/verified_fulltext/known.pdf", "source_priority": 80})
            rows.append({"venue": "www", "title": "Public", "public_url": "https://example.test/paper.pdf", "source_priority": 90})
            selected = visual_collector.limit_candidates_per_venue(rows, root, 2)
            self.assertEqual([row["title"] for row in selected], ["Public", "Known"])

    def test_verified_manifest_rows_are_reused_when_target_window_shrinks(self):
        with tempfile.TemporaryDirectory() as tmp:
            manifest = Path(tmp) / "manifest.yaml"
            row = {"venue": "icml", "year": 2026, "title": "Previously Verified", "eligibility": "style-evidence", "public_url": "https://arxiv.org/pdf/2601.1", "relative_path": "papers/ICML2026/verified_fulltext/paper.pdf"}
            manifest.write_text(yaml.safe_dump({"sources": [row]}), encoding="utf-8")
            self.assertEqual(visual_collector.reusable_manifest_rows(manifest, ["icml"], 2026), [row])
            self.assertEqual(visual_collector.reusable_manifest_rows(manifest, ["www"], 2026), [])

    def test_legacy_openreview_accept_filter_and_expiring_cache(self):
        accepted = {"id": "accepted", "content": {"title": "Accepted Paper"}, "details": {"directReplies": [{"content": {"decision": "Accept (Poster)"}}]}}
        rejected = {"id": "rejected", "content": {"title": "Rejected Paper"}, "details": {"directReplies": [{"content": {"decision": "Reject"}}]}}
        self.assertIsNotNone(visual_collector.legacy_openreview_candidate(accepted, "iclr", 2026))
        self.assertIsNone(visual_collector.legacy_openreview_candidate(rejected, "iclr", 2026))
        now = visual_collector.datetime(2026, 7, 11, tzinfo=visual_collector.timezone.utc)
        cache = visual_collector.empty_resolver_cache()
        visual_collector.cache_result(cache, visual_collector.title_fingerprint("Missing"), "no-match", None, now - visual_collector.timedelta(days=8))
        self.assertIsNone(visual_collector.cache_entry(cache, visual_collector.title_fingerprint("Missing"), now, False))

    def test_official_public_page_candidate_seed_is_accepted_title_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "seed.yaml"
            path.write_text(yaml.safe_dump({"schema_version": 1, "official_source_page": "https://openreview.net/submissions?venue=ICLR.cc/2026/Conference", "candidates": [{"venue": "iclr", "year": 2026, "track": "Poster", "title": "Accepted Fixture"}]}), encoding="utf-8")
            rows = visual_collector.load_candidate_seed(path, ["iclr"], 2026)
            self.assertEqual(len(rows), 1)
            self.assertTrue(rows[0]["accepted_title_verified"])
            self.assertIsNone(rows[0]["public_url"])
            self.assertEqual(rows[0]["eligibility"], "holdout")

    def test_arxiv_resolver_uses_exact_title_and_cache(self):
        payload = b'''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Exact Accepted Title</title><id>http://arxiv.org/abs/2601.12345</id></entry></feed>'''
        original = visual_collector.read_url
        try:
            visual_collector.read_url = lambda *_args, **_kwargs: payload
            cache = {}
            self.assertEqual(visual_collector.resolve_arxiv_pdf("Exact Accepted Title", cache=cache), "https://arxiv.org/pdf/2601.12345")
            self.assertIsNone(visual_collector.resolve_arxiv_pdf("Different Title", cache={}))
            self.assertEqual(visual_collector.resolve_arxiv_pdf("Exact Accepted Title", cache=cache), "https://arxiv.org/pdf/2601.12345")
        finally:
            visual_collector.read_url = original

    def test_arxiv_query_budget_ignores_valid_cache_hits(self):
        cache = visual_collector.empty_resolver_cache()
        now = visual_collector.datetime.now(visual_collector.timezone.utc)
        visual_collector.cache_result(cache, visual_collector.title_fingerprint("Cached Missing"), "no-match", None, now)
        with tempfile.TemporaryDirectory() as tmp:
            cache_path = Path(tmp) / "cache.json"
            visual_collector.save_resolver_cache(cache_path, cache)
            original = visual_collector.read_url
            try:
                payload = b'''<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Fresh Exact Title</title><id>http://arxiv.org/abs/2601.99999</id></entry></feed>'''
                visual_collector.read_url = lambda *_args, **_kwargs: payload
                candidates = [
                    {"venue": "icml", "title": "Cached Missing", "source_kind": "icml-virtual-official", "candidate_discovery_sources": []},
                    {"venue": "icml", "title": "Fresh Exact Title", "source_kind": "icml-virtual-official", "candidate_discovery_sources": []},
                ]
                rows = visual_collector.resolve_title_exact_public_fulltext(candidates, 1, 5, 0, cache_path=cache_path, max_queries=1)
                self.assertIsNone(rows[0].get("public_url"))
                self.assertEqual(rows[1]["public_url"], "https://arxiv.org/pdf/2601.99999")
            finally:
                visual_collector.read_url = original

    def test_figure_evaluation_matrix_has_production_depth(self):
        document = yaml.safe_load((ROOT / "tests" / "figure-evals.yaml").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(document["cases"]), 30)
        for case in document["cases"]:
            for field in ("fixture", "cli", "expected_files", "structural_assertions", "numeric_assertions", "qa_thresholds", "failure_mode"):
                self.assertIn(field, case)

    def test_visual_style_extracts_aggregate_features_from_synthetic_pdf(self):
        import fitz

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.pdf"
            doc = fitz.open()
            page = doc.new_page(width=300, height=220)
            page.insert_text((20, 30), "Figure 1: Synthetic aggregate fixture", fontsize=10)
            page.draw_rect(fitz.Rect(20, 60, 120, 130), color=(0.1, 0.2, 0.8), fill=(0.1, 0.2, 0.8))
            page.draw_line((20, 160), (180, 190), color=(0.9, 0.3, 0.2), width=2)
            doc.save(path)
            doc.close()
            record = visual_derive.extract_pdf_visual_record(path, {"file": "synthetic.pdf", "venue": "icml", "use": "style-evidence"}, max_pages=1)
            self.assertEqual(record["venue"], "icml")
            self.assertGreaterEqual(record["feature_counts"]["drawings"], 2)
            self.assertGreaterEqual(record["feature_counts"]["figure_captions"], 1)
            self.assertTrue(record["color_clusters"])
            self.assertTrue(record["palette_signatures"])
            self.assertTrue(all("color_families" in signature and "background" in signature for signature in record["palette_signatures"]))
            self.assertNotIn("Synthetic aggregate fixture", yaml.safe_dump(record))

    def test_palette_profile_requires_stable_figure_local_cooccurrence(self):
        records = []
        colors = ("#2468AC", "#D06040", "#3C9A60")
        for index in range(10):
            records.append({
                "source_id": f"www-profile-{index}", "venue": "www", "eligibility": "style-evidence",
                "color_clusters": [{"hex": color, "count": 4, "source": "figure-vector"} for color in colors],
                "palette_signatures": [{"color_families": [1, 4, 7], "background": "light", "visual_context": "chart"}],
                "layout_archetypes": ["quantitative-grid"],
            })
        _stats, rules = visual_derive.promote_rules(records, target_per_venue=10)
        rule = rules["rules"]["www"]
        self.assertEqual(rule["anchor_status"], "usable")
        self.assertEqual(rule["profile_status"], "usable")
        self.assertGreaterEqual(rule["palette_profiles"]["categorical"]["bootstrap_retention"], 0.6)

        without_cooccurrence = [dict(record, palette_signatures=[]) for record in records]
        _stats, rules = visual_derive.promote_rules(without_cooccurrence, target_per_venue=10)
        self.assertEqual(rules["rules"]["www"]["anchor_status"], "usable")
        self.assertEqual(rules["rules"]["www"]["profile_status"], "insufficient")

    def test_visual_style_collector_verifies_and_rejects_synthetic_pdfs(self):
        import fitz

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "paper.pdf"
            title = "Robust Agents for Long-Horizon Planning"
            doc = fitz.open()
            page = doc.new_page(width=300, height=220)
            page.insert_text((20, 30), f"{title}\nPublished as a conference paper at ICLR 2026", fontsize=10)
            doc.save(path)
            doc.close()
            candidate = {
                "source_id": "iclr2026-fixture",
                "venue": "iclr",
                "year": 2026,
                "track": "Poster",
                "title": title,
                "source_kind": "openreview-accepted",
                "public_url": "https://openreview.net/pdf?id=fixture",
            }
            eligibility, status, _ = visual_collector.verify_pdf_for_candidate(path, candidate)
            self.assertEqual((eligibility, status), ("style-evidence", "title-or-venue-verified"))

            mismatch = dict(candidate)
            mismatch["title"] = "A Different Paper"
            path_no_marker = Path(tmp) / "paper-no-marker.pdf"
            doc = fitz.open()
            page = doc.new_page(width=300, height=220)
            page.insert_text((20, 30), title, fontsize=10)
            doc.save(path_no_marker)
            doc.close()
            eligibility, status, _ = visual_collector.verify_pdf_for_candidate(path_no_marker, mismatch)
            self.assertEqual((eligibility, status), ("holdout", "title-and-venue-not-verified"))

            www = dict(candidate)
            www.update({"venue": "www", "track": "Research", "source_kind": "www-accepted-research-index"})
            eligibility, status, _ = visual_collector.verify_pdf_for_candidate(path, www)
            self.assertEqual((eligibility, status), ("holdout", "www-public-fulltext-not-title-exact"))

            www.update({"source_kind": "author-public-pdf", "public_url": "https://authors.example/paper.pdf"})
            eligibility, status, _ = visual_collector.verify_pdf_for_candidate(path, www)
            self.assertEqual((eligibility, status), ("style-evidence", "title-exact-public-fulltext"))

    def test_www_discovery_failure_is_recorded_without_crashing(self):
        original = visual_collector.read_url
        try:
            visual_collector.read_url = lambda *_args, **_kwargs: (_ for _ in ()).throw(visual_collector.urllib.error.URLError("offline"))
            gaps = []
            rows = visual_collector.discover_candidates(["www"], 2026, 2, 1, 0, False, discovery_gaps=gaps)
            self.assertTrue(rows)
            self.assertEqual(gaps[0]["source"], "official-accepted-research-index")
        finally:
            visual_collector.read_url = original

    def test_visual_style_source_manifest_promotes_with_ten_eligible_records(self):
        import fitz

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            rows = []
            for index in range(10):
                relative = Path("papers") / "ICML2026" / "verified_fulltext" / f"Regular - fixture-{index}.pdf"
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                doc = fitz.open()
                page = doc.new_page(width=300, height=220)
                page.insert_text((20, 30), f"Figure {index}: Aggregate visual fixture", fontsize=10)
                page.draw_rect(fitz.Rect(20, 60, 180, 120), color=(0.2, 0.3, 0.8), fill=(0.2, 0.3, 0.8))
                doc.save(path)
                doc.close()
                rows.append({
                    "source_id": f"icml2026-fixture-{index}",
                    "venue": "icml",
                    "track": "Regular",
                    "relative_path": relative.as_posix(),
                    "sha256": visual_derive.sha256(path),
                    "eligibility": "style-evidence",
                    "collection_status": "collected",
                    "verification_status": "title-or-venue-verified",
                })
            manifest = root / "visual-style-source-manifest.yaml"
            manifest.write_text(yaml.safe_dump({"schema_version": 1, "sources": rows}, sort_keys=False), encoding="utf-8")
            output = root / "derived"
            result = visual_derive.derive(root, output, source_manifest=manifest, max_pages=1, target_per_venue=10)
            self.assertEqual(result["eligible"], 10)
            rules = yaml.safe_load((output / "visual-style-rules.yaml").read_text(encoding="utf-8"))
            stats = yaml.safe_load((output / "visual-style-stats.json").read_text(encoding="utf-8"))
            self.assertEqual(rules["rules"]["icml"]["status"], "promoted")
            self.assertEqual(stats["venues"]["icml"]["coverage"]["eligible_count"], 10)
            self.assertEqual(stats["venues"]["icml"]["coverage"]["track_mix"], {"Regular": 10})

    def test_visual_style_outputs_do_not_store_raw_images_or_caption_text(self):
        import fitz

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "synthetic.pdf"
            doc = fitz.open()
            page = doc.new_page(width=300, height=220)
            page.insert_text((20, 30), "Figure 1: Private caption text", fontsize=10)
            page.draw_rect(fitz.Rect(20, 60, 180, 120), color=(0.2, 0.3, 0.8), fill=(0.2, 0.3, 0.8))
            doc.save(source)
            doc.close()
            manifest = root / "source-manifest.yaml"
            manifest.write_text(yaml.safe_dump({"sources": [{
                "source_id": "synthetic-privacy-fixture",
                "venue": "icml",
                "relative_path": source.name,
                "eligibility": "style-evidence",
            }]}), encoding="utf-8")
            output = root / "derived"
            result = visual_derive.derive(root, output, local_only=True, max_pages=1, source_manifest=manifest)
            self.assertGreater(result["records"], 0)
            for path in output.iterdir():
                self.assertNotIn(path.suffix.lower(), {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"})
                text = path.read_text(encoding="utf-8") if path.suffix.lower() in {".yaml", ".json"} else ""
                self.assertNotIn("Figure 1:", text)

    def test_repository_does_not_store_raw_visual_corpus_artifacts(self):
        forbidden = {".pdf", ".png", ".jpg", ".jpeg", ".tif", ".tiff"}
        for root in (ROOT / "skills", ROOT / "evidence" / "derived"):
            for path in root.rglob("*"):
                if path.is_file():
                    if path.suffix.lower() == ".png" and "top-cs-figure" in path.parts and "assets" in path.parts:
                        self.assertIn(path.parent.name, {"chart-atlas", "gallery"})
                        continue
                    self.assertNotIn(path.suffix.lower(), forbidden, str(path))


class EvidenceValidatorTests(unittest.TestCase):
    def test_repository_evidence_is_valid_and_primary_paper_targets_are_met(self):
        index = yaml.safe_load((ROOT / "evidence" / "derived" / "corpus-index.yaml").read_text(encoding="utf-8"))
        rules = yaml.safe_load((ROOT / "evidence" / "derived" / "rules.yaml").read_text(encoding="utf-8"))
        result = validator.validate(index, rules, strict=True)
        self.assertTrue(result["valid"])
        self.assertFalse(any("readiness gap" in item for item in result["warnings"]))

    def test_policy_diff_detects_hash_change(self):
        current = {"official_sources": [{"source_id": "x", "sha256": "new", "availability": "collected"}]}
        previous = {"official_sources": [{"source_id": "x", "sha256": "old", "availability": "collected"}]}
        self.assertEqual(validator.policy_diff(current, previous)[0]["change"], "content-or-availability-changed")


if __name__ == "__main__":
    unittest.main()
