from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SHARED = ROOT / "skills" / "_shared"


class V23CapabilityContractTests(unittest.TestCase):
    def test_rhetorical_moves_cover_full_manuscript(self):
        text = (SHARED / "references" / "rhetorical-moves.md").read_text(encoding="utf-8")
        for section in ("Title", "Abstract", "Introduction", "Related work", "Method", "Experiments", "Discussion", "Limitations", "Conclusion"):
            self.assertIn(f"| {section} |", text)
        self.assertIn("Topic-sentence scaffold", text)
        self.assertIn("Optional introduction-twice", text)

    def test_experiment_boundary_forbids_execution(self):
        guide = (ROOT / "skills" / "top-cs-writing" / "references" / "experiments-guide.md").read_text(encoding="utf-8")
        self.assertIn("does not execute code", guide)
        self.assertIn("claim ID, research question", guide)

    def test_shared_schemas_have_required_fields_and_closed_statuses(self):
        citation = yaml.safe_load((SHARED / "contracts" / "citation-record.schema.yaml").read_text(encoding="utf-8"))
        figure = yaml.safe_load((SHARED / "contracts" / "figure-brief.schema.yaml").read_text(encoding="utf-8"))
        render = yaml.safe_load((SHARED / "contracts" / "figure-render-spec.schema.yaml").read_text(encoding="utf-8"))
        visual = yaml.safe_load((SHARED / "contracts" / "visual-style-record.schema.yaml").read_text(encoding="utf-8"))
        issue = yaml.safe_load((SHARED / "contracts" / "response-issue.schema.yaml").read_text(encoding="utf-8"))
        self.assertTrue({"citation_key", "bibliographic_status", "claim_entailment_status"}.issubset(citation["required"]))
        self.assertTrue({"claim_ids", "research_question", "panels", "caption_draft", "evidence_status"}.issubset(figure["required"]))
        self.assertTrue({"figure_id", "visual_family", "data_sources", "encodings", "output_base"}.issubset(render["required"]))
        self.assertTrue({"layout", "panels", "data_provenance", "spec_version"}.issubset(render["properties"]))
        self.assertTrue({"source_hash", "feature_counts", "color_clusters", "confidence"}.issubset(visual["required"]))
        self.assertEqual(issue["properties"]["round"]["maximum"], 3)
        self.assertEqual(set(issue["properties"]["status"]["enum"]), {"unresolved", "evidence-needed", "drafted", "verified", "planned", "cannot-complete", "author-input-needed"})

    def test_response_stress_test_has_cap_and_stop_condition(self):
        text = (ROOT / "skills" / "top-cs-response" / "references" / "issue-board-and-stress-test.md").read_text(encoding="utf-8")
        self.assertIn("Rounds 2 and 3 audit only", text)
        self.assertIn("Stop early", text)
        self.assertIn("may not create results", text)

    def test_figure_boundary_excludes_rendering_ownership(self):
        text = (SHARED / "references" / "figure-handoff.md").read_text(encoding="utf-8")
        self.assertIn("render and export figures only in `top-cs-figure`", text)
        self.assertIn("`top-cs-figure` owns rendering backend", text)
        self.assertTrue((ROOT / "skills" / "top-cs-figure").exists())

    def test_external_projects_are_workflow_inspiration_only(self):
        provenance = yaml.safe_load((SHARED / "rule-provenance.yaml").read_text(encoding="utf-8"))
        source = provenance["sources"]["external-workflow-inspiration"]
        self.assertEqual(source["label"], "workflow-inspiration")
        self.assertEqual(len(source["projects"]), 5)
        self.assertIn("nature-figure", {project["id"] for project in source["projects"]})
        self.assertIn("No external wording", source["boundary"])


if __name__ == "__main__":
    unittest.main()
