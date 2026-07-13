from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def manifest(skill: str) -> dict:
    return yaml.safe_load((SKILLS / skill / "manifest.yaml").read_text(encoding="utf-8"))


class SkillDepthTests(unittest.TestCase):
    def test_rule_provenance_labels_and_source_routes(self):
        provenance = yaml.safe_load((SKILLS / "_shared" / "rule-provenance.yaml").read_text(encoding="utf-8"))
        self.assertEqual(
            set(provenance["labels"]),
            {"official-policy", "corpus-derived", "author-artifact", "conservative-implementation", "output-contract", "synthetic-example", "workflow-inspiration"},
        )
        for skill in ("top-cs-writing", "top-cs-polishing", "top-cs-reviewer", "top-cs-response", "top-cs-figure"):
            routes = manifest(skill)["reference_routes"]
            self.assertIn("source-basis", routes)
            for relative in routes["source-basis"]:
                self.assertTrue((SKILLS / skill / relative).resolve().is_file())

    def test_shared_reader_and_terminology_are_routed(self):
        for skill in ("top-cs-writing", "top-cs-polishing"):
            always = set(manifest(skill)["always_load"])
            self.assertIn("../_shared/core/terminology-ledger.md", always)
            self.assertIn("../_shared/core/reader-workflow.md", always)

    def test_writing_supports_alignment_and_targeted_revision(self):
        workflow = read("skills/top-cs-writing/static/core/workflow.md")
        alignment = read("skills/top-cs-writing/references/alignment-and-revision.md")
        self.assertIn("at most two high-leverage questions", workflow)
        self.assertIn("Preserve unaffected text", alignment)
        self.assertIn("terminology ledger", workflow.lower())

    def test_polishing_has_diagnosis_examples_and_rendered_layout_checks(self):
        routes = manifest("top-cs-polishing")["reference_routes"]
        self.assertIn("style-diagnostics", routes)
        self.assertIn("examples", routes)
        self.assertIn("latex-layout", routes)
        layout = read("skills/top-cs-polishing/references/latex-layout.md")
        self.assertIn("Render affected pages", layout)
        self.assertIn("without shell escape", layout)

    def test_reviewer_issue_contract_is_consequence_based(self):
        contract = read("skills/top-cs-reviewer/references/issue-contract.md")
        for field in ("Anchor", "Threatened claim", "Consequence", "Confidence", "Resolution", "Fixability"):
            self.assertIn(field, contract)
        partial = read("skills/top-cs-reviewer/references/partial-manuscript-protocol.md")
        self.assertIn("visible defect", partial)
        self.assertIn("not assessable", partial)

    def test_response_package_modes_templates_and_conference_guard(self):
        values = set(manifest("top-cs-response")["runtime_parameters"]["task_mode"]["values"])
        self.assertTrue({"cover-letter", "revision-package", "latex-template"}.issubset(values))
        for name in ("cover-letter.tex.template", "response-to-reviewers.tex.template", "revision-ledger.tex.template"):
            template = SKILLS / "top-cs-response" / "assets" / name
            self.assertTrue(template.is_file())
            self.assertIn("[", template.read_text(encoding="utf-8"))
        workflow = read("skills/top-cs-response/static/core/workflow.md")
        self.assertIn("Do not apply journal revision-package conventions", workflow)

    def test_figure_skill_is_python_first_and_has_visual_families(self):
        routes = manifest("top-cs-figure")["reference_routes"]
        self.assertIn("python-workflow", routes)
        self.assertIn("visual-qa", routes)
        self.assertIn("visual-style", routes)
        self.assertIn("spec-rendering", routes)
        values = set(manifest("top-cs-figure")["axes"]["visual_family"]["values"])
        self.assertEqual(
            values,
            {"comparison", "trend-scaling", "matrix-heatmap", "embedding-scatter", "network", "method-schematic", "distribution-uncertainty", "tradeoff-frontier", "calibration-reliability", "ranking-critical-difference", "qualitative-image-plate", "forest-interval", "composition-stacked", "paired-change", "polar-summary"},
        )
        workflow = read("skills/top-cs-figure/static/core/workflow.md")
        self.assertIn("Save SVG, PDF, and PNG by default", workflow)
        stance = read("skills/top-cs-figure/static/core/stance.md")
        self.assertIn("Python/matplotlib", stance)


if __name__ == "__main__":
    unittest.main()
