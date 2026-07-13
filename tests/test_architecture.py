from __future__ import annotations

import unittest
from pathlib import Path

import yaml
from collections import Counter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
PAPER_SKILLS = ("top-cs-writing", "top-cs-polishing", "top-cs-reviewer", "top-cs-response")
ALL_SKILLS = PAPER_SKILLS + ("top-cs-figure",)


def load_manifest(skill: str):
    path = SKILLS / skill / "manifest.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8")), path.parent


def declared_paths(manifest: dict):
    def emit(value):
        if isinstance(value, list):
            for item in value:
                yield from emit(item)
        else:
            yield value

    for value in manifest.get("always_load", []):
        yield from emit(value)
    for axis in manifest.get("axes", {}).values():
        for value in axis.get("values", {}).values():
            yield from emit(value)
    for item in manifest.get("references", {}).get("on_demand", []):
        yield from emit(item["path"])
    for paths in manifest.get("reference_routes", {}).values():
        yield from emit(paths)


class ArchitectureTests(unittest.TestCase):
    def test_every_declared_path_exists(self):
        for skill in ALL_SKILLS:
            manifest, base = load_manifest(skill)
            for relative in declared_paths(manifest):
                with self.subTest(skill=skill, path=relative):
                    self.assertTrue((base / relative).resolve().is_file())

    def test_writing_and_polishing_use_four_content_axes(self):
        expected = {"venue", "paper_type", "section", "language"}
        for skill in ("top-cs-writing", "top-cs-polishing"):
            manifest, _ = load_manifest(skill)
            self.assertEqual(set(manifest["axes"]), expected)
            self.assertEqual(len(manifest["axes"]["section"]["values"]), 9)
            self.assertGreaterEqual(len(manifest["references"]["on_demand"]), 3)

    def test_reviewer_only_routes_content_by_venue(self):
        manifest, _ = load_manifest("top-cs-reviewer")
        self.assertEqual(set(manifest["axes"]), {"venue"})
        self.assertEqual(
            set(manifest["runtime_parameters"]),
            {"manuscript_scope", "review_mode", "paper_type", "artifact_scope", "evidence_state", "submission_stage", "citation_verification", "figure_handoff"},
        )

    def test_response_is_linear_and_has_no_content_axes(self):
        manifest, _ = load_manifest("top-cs-response")
        self.assertNotIn("axes", manifest)
        self.assertEqual(
            set(manifest["runtime_parameters"]),
            {"venue", "task_mode", "response_phase", "decision_type", "language", "artifact_scope", "revision_mode", "evidence_state", "submission_stage", "citation_verification", "figure_handoff", "stress_test"},
        )
        self.assertGreaterEqual(len(manifest["references"]["on_demand"]), 7)

    def test_each_skill_has_local_static_core(self):
        for skill in ALL_SKILLS:
            manifest, base = load_manifest(skill)
            local_core = [p for p in manifest["always_load"] if p.startswith("static/core/")]
            self.assertEqual(len(local_core), 3)
            for relative in local_core:
                self.assertTrue((base / relative).is_file())

    def test_writing_and_polishing_runtime_parameters_do_not_add_axes(self):
        writing, _ = load_manifest("top-cs-writing")
        polishing, _ = load_manifest("top-cs-polishing")
        self.assertEqual(set(writing["runtime_parameters"]), {"artifact_scope", "evidence_state", "submission_stage", "citation_verification", "figure_handoff"})
        self.assertEqual(set(polishing["runtime_parameters"]), {"artifact_scope", "revision_mode", "evidence_state", "submission_stage", "citation_verification", "figure_handoff"})

    def test_contract_routes_and_figure_skill_boundary(self):
        skill_dirs = sorted(path.name for path in SKILLS.iterdir() if path.is_dir() and not path.name.startswith("_"))
        self.assertEqual(skill_dirs, ["top-cs-figure", "top-cs-polishing", "top-cs-response", "top-cs-reviewer", "top-cs-writing"])
        for skill in PAPER_SKILLS:
            manifest, _ = load_manifest(skill)
            self.assertEqual(manifest["version"], "2.3.0")
            self.assertIn("citation-verification", manifest["reference_routes"])
            self.assertIn("figure-handoff", manifest["reference_routes"])
        figure, _ = load_manifest("top-cs-figure")
        self.assertEqual(figure["version"], "4.1.0")
        self.assertIn("python-workflow", figure["reference_routes"])
        self.assertIn("visual-qa", figure["reference_routes"])
        self.assertIn("figure-handoff", figure["reference_routes"])
        self.assertIn("visual-style", figure["reference_routes"])
        forbidden_names = {"render_figure.py", "generate_figure.py", "figure_backend.py"}
        for skill in PAPER_SKILLS:
            self.assertFalse(any(path.name in forbidden_names for path in (SKILLS / skill).rglob("*.py")))

    def test_each_skill_has_seven_executable_acceptance_cases(self):
        document = yaml.safe_load((ROOT / "tests" / "acceptance-cases.yaml").read_text(encoding="utf-8"))
        counts = Counter(case["skill"] for case in document["cases"])
        self.assertEqual(
            counts,
            {
                "top-cs-writing": 7,
                "top-cs-polishing": 7,
                "top-cs-reviewer": 7,
                "top-cs-response": 7,
                "top-cs-figure": 17,
            },
        )


if __name__ == "__main__":
    unittest.main()
