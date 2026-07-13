from __future__ import annotations

import unittest
from collections import Counter
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = ROOT / "tests" / "deep-acceptance-cases.yaml"


class DeepAcceptanceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.document = yaml.safe_load(CASE_FILE.read_text(encoding="utf-8"))
        cls.cases = cls.document["cases"]

    def test_two_source_backed_semantic_cases_per_skill(self):
        counts = Counter(case["skill"] for case in self.cases)
        self.assertEqual(counts, {
            "top-cs-writing": 2,
            "top-cs-polishing": 2,
            "top-cs-reviewer": 2,
            "top-cs-response": 2,
            "top-cs-figure": 2,
        })

    def test_every_case_has_source_semantics_and_manual_rubric(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertTrue((CASE_FILE.parent / case["source_file"]).is_file())
                contract = case.get("semantic_contract", {})
                self.assertTrue(contract.get("required_sections"))
                self.assertTrue(contract.get("fact_invariants"))
                self.assertTrue(contract.get("forbidden_claim_patterns"))
                self.assertGreaterEqual(len(case.get("manual_rubric", [])), 4)

    def test_preservation_cases_use_real_source_tokens(self):
        for case in self.cases:
            kinds = case.get("semantic_contract", {}).get("preserve_from_source", [])
            if not kinds:
                continue
            source = (CASE_FILE.parent / case["source_file"]).read_text(encoding="utf-8")
            with self.subTest(case=case["id"]):
                if "numbers" in kinds:
                    self.assertRegex(source, r"\d")
                if "citations" in kinds:
                    self.assertIn("\\cite", source)
                if "labels" in kinds:
                    self.assertIn("\\label", source)


if __name__ == "__main__":
    unittest.main()
