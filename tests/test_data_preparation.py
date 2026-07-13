from __future__ import annotations

import unittest
from pathlib import Path
from collections import Counter

import yaml


ROOT = Path(__file__).resolve().parents[1]


class DataPreparationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = yaml.safe_load((ROOT / "data-preparation.yaml").read_text(encoding="utf-8"))
        cls.index = yaml.safe_load((ROOT / "evidence" / "derived" / "corpus-index.yaml").read_text(encoding="utf-8"))

    def test_scope_and_storage_boundary(self):
        self.assertEqual(self.plan["schema_version"], 2)
        supported = {(x["venue"], x["year"]) for x in self.plan["scope"]["supported"]}
        self.assertEqual(supported, {("www", 2026), ("iclr", 2026), ("icml", 2026), ("generic", None)})
        self.assertEqual(self.plan["storage_policy"]["raw_public_material"], "external-corpus-only")
        self.assertFalse(self.plan["storage_policy"]["install_private_cases"])

    def test_every_venue_has_every_required_policy_category(self):
        required = set(self.plan["official_policy"]["required_categories"])
        allowed = set(self.plan["official_policy"]["statuses"])
        official_ids = {source["source_id"] for source in self.index["official_sources"]}
        for venue, profile in self.plan["official_policy"]["venues"].items():
            with self.subTest(venue=venue):
                self.assertEqual(set(profile["categories"]), required)
                for category, cell in profile["categories"].items():
                    self.assertIn(cell["status"], allowed, f"{venue}/{category}")
                    if cell["status"] == "collected":
                        self.assertTrue(cell["source_ids"], f"{venue}/{category}")
                        self.assertTrue(set(cell["source_ids"]).issubset(official_ids), f"unresolved source for {venue}/{category}")
                    else:
                        self.assertFalse(cell["source_ids"], f"{venue}/{category}")

    def test_www_reviewer_gap_does_not_borrow_other_venues(self):
        www = self.plan["official_policy"]["venues"]["www"]
        self.assertEqual(www["categories"]["reviewer-guide"]["status"], "not-public")
        self.assertEqual(www["categories"]["review-form"]["status"], "not-public")
        self.assertEqual(www["categories"]["reviewer-guide"]["fallback"], "author-side-criteria-only")

    def test_iclr_and_icml_response_protocols_are_structured(self):
        iclr = self.plan["official_policy"]["venues"]["iclr"]["response_protocol"]
        self.assertTrue(iclr["public_discussion"])
        self.assertTrue(iclr["manuscript_revision_during_discussion"])
        self.assertTrue(iclr["automated_pdf_diff"])
        icml = self.plan["official_policy"]["venues"]["icml"]["response_protocol"]
        self.assertEqual(icml["responses_per_official_review"], 1)
        self.assertEqual(icml["revised_manuscript_during_feedback"], "prohibited")
        self.assertTrue(icml["final_justification_required"])

    def test_paper_targets_and_current_counts_match_index(self):
        papers = self.plan["papers"]
        self.assertEqual(papers["target_total_unique_primary"], 90)
        self.assertEqual(papers["target_unique_primary_per_venue"], {"www": 30, "iclr": 30, "icml": 30})
        primary = [x for x in self.index["paper_sources"] if x["eligibility"] == "primary-writing-evidence"]
        actual = {
            "www": sum(x["conference"] == "WWW2026" for x in primary),
            "iclr": sum(x["conference"] == "ICLR2026" for x in primary),
            "icml": sum(x["conference"] == "ICML2026" for x in primary),
        }
        self.assertEqual(papers["current_unique_primary"], actual)
        self.assertEqual(papers["gaps"], {k: 30 - v for k, v in actual.items()})
        self.assertFalse(papers["eligibility"]["public_preprint_is_format_evidence"])

    def test_diversity_and_track_requirements(self):
        diversity = self.plan["papers"]["diversity_requirements"]
        self.assertGreaterEqual(diversity["minimum_paper_types"], 4)
        self.assertGreaterEqual(diversity["minimum_topics"], 6)
        self.assertLessEqual(diversity["maximum_single_topic_fraction"], 0.25)
        self.assertEqual(self.plan["papers"]["eligibility"]["www_primary_track"], "Research")
        for source in self.index["paper_sources"]:
            if source["conference"] == "WWW2026" and "Research" not in source["tracks"]:
                self.assertNotEqual(source["eligibility"], "primary-writing-evidence")

        for conference in ("WWW2026", "ICLR2026", "ICML2026"):
            selected = [
                source for source in self.index["paper_sources"]
                if source["conference"] == conference and source["eligibility"] == "primary-writing-evidence"
            ]
            topics = {}
            for source in selected:
                topics[source["research_area"]] = topics.get(source["research_area"], 0) + 1
            paper_types = {source["paper_type"] for source in selected}
            self.assertGreaterEqual(len(topics), diversity["minimum_topics"])
            self.assertLessEqual(max(topics.values()) / len(selected), diversity["maximum_single_topic_fraction"])
            self.assertGreaterEqual(len(paper_types), diversity["minimum_paper_types"])

    def test_diversity_labels_remain_candidates_until_human_confirmation(self):
        diversity = self.plan["papers"]["diversity_requirements"]
        primary = [x for x in self.index["paper_sources"] if x["eligibility"] == "primary-writing-evidence"]
        self.assertTrue(diversity["labels_require_human_verification"])
        self.assertEqual(diversity["labels_awaiting_human_confirmation"], len(primary))
        self.assertEqual({x["label_status"] for x in primary}, {diversity["current_label_status"]})
        imbalance = self.plan["papers"]["known_candidate_label_imbalance"]
        self.assertEqual(imbalance["total_paper_types"], dict(Counter(x["paper_type"] for x in primary)))
        self.assertEqual(imbalance["provisional_gaps"], {"www": 0, "iclr": 6, "icml": 4})

    def test_review_promotion_and_storage_rules(self):
        reviews = self.plan["reviews_and_responses"]
        self.assertEqual(reviews["minimum_valid_discussion_flows_for_venue_mode"], 30)
        self.assertEqual(reviews["target_public_flows"], {"iclr": 50, "icml": 50, "www": "unsupported"})
        self.assertEqual(reviews["raw_text_distribution"], "prohibited")
        self.assertNotIn("review_text", reviews["stored_fields"])
        self.assertFalse(any(reviews["venue_specific_response_mode"].values()))

    def test_version_pairs_and_private_material_are_not_promoted(self):
        pairs = self.plan["version_pairs"]
        self.assertEqual(pairs["target_verified"], {"iclr": 20, "icml": 20})
        self.assertEqual(pairs["current_verified"], {"iclr": 0, "icml": 0})
        private = self.plan["private_regression"]
        self.assertTrue(private["excluded_from_install"])
        self.assertTrue(private["excluded_from_corpus_index"])
        self.assertIn("immutable_facts", private["required_acceptance_labels"])
        self.assertIn("forbidden_outputs_or_citations", private["required_acceptance_labels"])

    def test_no_raw_corpus_artifacts_inside_skills(self):
        forbidden_suffixes = {".pdf", ".jsonl", ".zip", ".tex", ".bib"}
        offenders = [p for p in (ROOT / "skills").rglob("*") if p.is_file() and p.suffix.lower() in forbidden_suffixes]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
