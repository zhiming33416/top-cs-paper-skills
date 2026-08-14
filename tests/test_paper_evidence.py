from __future__ import annotations

import contextlib
import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "top-cs-evidence" / "scripts" / "paper_evidence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("paper_evidence", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


evidence = load_module()


class PaperEvidenceTests(unittest.TestCase):
    def run_main(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = evidence.main(list(args))
        return result, stdout.getvalue(), stderr.getvalue()

    def test_plan_requires_unique_claim_ids(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = root / "claims.yaml"
            claims.write_text(
                "claims:\n  - {claim_id: CLM-001, statement: A synthetic result.}\n  - {claim_id: CLM-001, statement: Duplicate.}\n",
                encoding="utf-8",
            )
            result, _, stderr = self.run_main("plan", "--claims", str(claims), "--output", str(root / "plan.yaml"))
            self.assertEqual(result, 2)
            self.assertIn("duplicate claim_id", stderr)

    def test_verify_is_offline_by_default_and_records_metadata_boundary(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            bib = root / "refs.bib"
            output = root / "ledger.yaml"
            bib.write_text(
                "@article{synthetic, title={Synthetic Citation}, author={Example, Ada}, year={2026}}\n",
                encoding="utf-8",
            )
            result, _, _ = self.run_main("verify", "--bib", str(bib), "--output", str(output), "--sources", "crossref")
            self.assertEqual(result, 0)
            ledger = yaml.safe_load(output.read_text(encoding="utf-8"))
            self.assertFalse(ledger["online_lookup_authorized"])
            self.assertIn("claim entailment", ledger["boundary"].lower())
            self.assertEqual(ledger["records"][0]["citation_key"], "synthetic")

    def test_map_requires_author_note_before_claim_support_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = root / "claims.yaml"
            ledger = root / "ledger.yaml"
            notes = root / "notes.yaml"
            output = root / "map.yaml"
            claims.write_text("claims:\n  - {claim_id: CLM-001, statement: A synthetic claim.}\n", encoding="utf-8")
            ledger.write_text("records:\n  - {citation_key: synthetic, bibliographic_status: verified}\n", encoding="utf-8")
            notes.write_text(
                "sources:\n  - {citation_key: synthetic, claim_ids: [CLM-001], claim_entailment_status: supported}\n",
                encoding="utf-8",
            )
            result, _, _ = self.run_main(
                "map", "--claims", str(claims), "--ledger", str(ledger), "--notes", str(notes), "--output", str(output)
            )
            self.assertEqual(result, 0)
            document = yaml.safe_load(output.read_text(encoding="utf-8"))
            self.assertEqual(document["sources"][0]["claim_entailment_status"], "needs-source-text")

    def test_map_rejects_unsafe_note_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claims = root / "claims.yaml"
            ledger = root / "ledger.yaml"
            notes = root / "notes.yaml"
            claims.write_text("claims:\n  - {claim_id: CLM-001, statement: A synthetic claim.}\n", encoding="utf-8")
            ledger.write_text("records:\n  - {citation_key: synthetic, bibliographic_status: verified}\n", encoding="utf-8")
            notes.write_text(
                "sources:\n  - {citation_key: synthetic, claim_ids: [CLM-001], note_path: ../private.md}\n",
                encoding="utf-8",
            )
            result, _, stderr = self.run_main(
                "map", "--claims", str(claims), "--ledger", str(ledger), "--notes", str(notes), "--output", str(root / "map.yaml")
            )
            self.assertEqual(result, 2)
            self.assertIn("project-relative", stderr)


if __name__ == "__main__":
    unittest.main()
