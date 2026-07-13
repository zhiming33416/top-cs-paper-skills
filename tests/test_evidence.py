from __future__ import annotations

import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence" / "derived"


class EvidenceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = yaml.safe_load((EVIDENCE / "corpus-index.yaml").read_text(encoding="utf-8"))
        cls.rules = yaml.safe_load((EVIDENCE / "rules.yaml").read_text(encoding="utf-8"))["rules"]
        cls.sources = {
            item["source_id"]: item
            for group in ("official_sources", "paper_sources", "review_sources")
            for item in cls.index[group]
        }

    def test_expected_corpus_counts_and_deduplication(self):
        self.assertEqual(self.index["schema_version"], 2)
        self.assertEqual(self.index["summary"], {
            "pdf_files": 100,
            "unique_pdfs": 99,
            "primary_writing_evidence": 90,
        })
        self.assertEqual(len(self.index["duplicates"]), 1)
        duplicate = self.index["duplicates"][0]
        self.assertEqual(len(duplicate["occurrences"]), 2)
        self.assertIn("Agent0-VL", " ".join(item["relative_path"] for item in duplicate["occurrences"]))

    def test_primary_evidence_by_venue_and_www_track_exclusion(self):
        primary = [s for s in self.index["paper_sources"] if s["eligibility"] == "primary-writing-evidence"]
        counts = {conference: sum(s["conference"] == conference for s in primary) for conference in ("ICLR2026", "ICML2026", "WWW2026")}
        self.assertEqual(counts, {"ICLR2026": 30, "ICML2026": 30, "WWW2026": 30})
        for source in self.index["paper_sources"]:
            if source["conference"] == "WWW2026" and "Research" not in source["tracks"]:
                self.assertEqual(source["eligibility"], "indexed-nonresearch")

    def test_public_versions_are_never_format_evidence(self):
        for source in self.index["paper_sources"]:
            self.assertEqual(source["source_type"], "accepted-title-verified-public-version")
            self.assertEqual(source["document_version"], "public-preprint-or-author-version")
            self.assertFalse(source["official_format_evidence"])
            self.assertIn("paper_type", source)
            self.assertIn("topic_tags_candidate", source)
            self.assertIn("artifact_pairs", source)
            self.assertIn("section_order", source["structure"])

    def test_index_contains_no_raw_text_or_absolute_paths(self):
        forbidden = {"full_text", "abstract", "content", "review_content", "rebuttal"}
        for source in self.index["paper_sources"] + self.index["review_sources"]:
            self.assertTrue(forbidden.isdisjoint(source))
            relative = source["relative_path"]
            self.assertFalse(Path(relative).is_absolute())
            self.assertNotIn("C:\\", relative)

    def test_every_rule_source_resolves_and_matches_type(self):
        for rule in self.rules:
            with self.subTest(rule=rule["rule_id"]):
                self.assertEqual(rule["support_count"], len(rule["source_ids"]))
                self.assertEqual(len(rule["source_ids"]), len(set(rule["source_ids"])))
                for source_id in rule["source_ids"]:
                    self.assertIn(source_id, self.sources)
                    self.assertEqual(self.sources[source_id]["source_type"], rule["source_type"])

    def test_soft_rule_promotion_thresholds(self):
        for rule in self.rules:
            if rule["source_type"] == "official-policy":
                self.assertGreaterEqual(rule["support_count"], 1)
                continue
            selected = [self.sources[source_id] for source_id in rule["source_ids"]]
            if rule["source_type"] == "accepted-title-verified-public-version":
                if rule["venue"] == "cross-venue":
                    self.assertGreaterEqual(rule["support_count"], 6)
                    self.assertGreaterEqual(len({source["conference"] for source in selected}), 2)
                elif rule["venue"] == "www":
                    self.assertGreaterEqual(rule["support_count"], 3)
                    self.assertTrue(all("Research" in source["tracks"] for source in selected))
                else:
                    self.assertGreaterEqual(rule["support_count"], 3)
                    self.assertGreaterEqual(len({track for source in selected for track in source["tracks"]}), 2)
            elif rule["source_type"] == "historical-public-review":
                self.assertGreaterEqual(rule["support_count"], 5)
                self.assertTrue(all(source["discussion_threads"] > 0 for source in selected))
                self.assertGreaterEqual(len({source["decision"] for source in selected}), 2)

    def test_review_policy_boundary_is_explicit(self):
        for source in self.index["review_sources"]:
            self.assertIn("not current venue policy", source["policy_boundary"].lower())

    def test_official_sources_have_freshness_or_explicit_gap(self):
        for source in self.index["official_sources"]:
            self.assertEqual(source["valid_for_year"], 2026)
            self.assertEqual(source["expires_after_year"], 2026)
            if source["availability"] == "collected":
                self.assertTrue(source["sha256"])
                self.assertEqual(source["verification_status"], "hash-verified-local-copy")
            else:
                self.assertEqual(source["verification_status"], "explicit-gap")

    def test_polishing_has_independent_evidence_rules(self):
        polishing = [rule for rule in self.rules if rule["skill"] == "top-cs-polishing"]
        self.assertGreaterEqual(len(polishing), 3)

    def test_policy_matrix_marks_www_reviewer_gap(self):
        matrix = yaml.safe_load((EVIDENCE / "policy-matrix.yaml").read_text(encoding="utf-8"))
        self.assertEqual(matrix["schema_version"], 2)
        self.assertEqual(matrix["venues"]["www"]["categories"]["reviewer"]["status"], "not-public-or-not-collected")
        self.assertEqual(matrix["venues"]["icml"]["categories"]["artifact-reproducibility"]["status"], "verified")

    def test_full_section_rules_resolve_to_structural_evidence(self):
        document = yaml.safe_load((EVIDENCE / "full-section-rules.yaml").read_text(encoding="utf-8"))
        sources = {source["source_id"]: source for source in self.index["paper_sources"]}
        self.assertEqual({rule["section"] for rule in document["rules"]}, {"method", "experiments", "discussion", "limitations", "conclusion"})
        for rule in document["rules"]:
            matched = [source_id for source_id in document["population_source_ids"] if rule["section"] in sources[source_id]["structure"]["section_order"]]
            self.assertEqual(rule["matched_source_ids"], matched)
            self.assertEqual(rule["matched_count"], len(matched))
            self.assertEqual(rule["population_count"], 90)


if __name__ == "__main__":
    unittest.main()
