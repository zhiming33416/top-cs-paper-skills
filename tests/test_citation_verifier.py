from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script():
    path = ROOT / "skills" / "_shared" / "scripts" / "verify_citations.py"
    spec = importlib.util.spec_from_file_location("verify_citations", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


verify = load_script()


class FakeResponse:
    def __init__(self, body: str):
        self.body = body.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self):
        return self.body


class CitationVerifierTests(unittest.TestCase):
    def entry(self, **updates):
        value = {"citation_key": "smith2026", "entry_type": "article", "title": "Reliable Graph Learning", "authors": ["Alice Smith"], "year": 2026, "doi": "10.1/example", "arxiv_id": None}
        value.update(updates)
        return value

    def test_bibtex_parser_preserves_nested_title_and_identifiers(self):
        entries = verify.parse_bibtex('@article{smith2026, title={Reliable {Graph} Learning}, author={Alice Smith and Bob Lee}, year={2026}, doi={https://doi.org/10.1/example}}')
        self.assertEqual(entries[0]["citation_key"], "smith2026")
        self.assertEqual(entries[0]["doi"], "10.1/example")
        self.assertEqual(entries[0]["authors"], ["Alice Smith", "Bob Lee"])

    def test_exact_doi_is_verified_but_claim_is_not(self):
        body = json.dumps({"message": {"DOI": "10.1/example", "title": ["Reliable Graph Learning"], "author": [{"given": "Alice", "family": "Smith"}], "published": {"date-parts": [[2026]]}}})
        fetcher = verify.Fetcher(None, False, 1, 0, opener=lambda *_args, **_kwargs: FakeResponse(body))
        record = verify.verify_entry(self.entry(), ["crossref"], fetcher)
        self.assertEqual(record["bibliographic_status"], "verified")
        self.assertEqual(record["claim_entailment_status"], "needs-source-text")

    def test_two_fuzzy_title_sources_verify_metadata(self):
        original = verify.LOOKUPS.copy()
        candidate = {"title": "Reliable graph learning", "authors": ["A. Smith"], "year": 2026, "identifier": "x", "url": None, "exact_identifier": False}
        try:
            verify.LOOKUPS["crossref"] = lambda *_: (candidate, False)
            verify.LOOKUPS["dblp"] = lambda *_: (candidate, False)
            record = verify.verify_entry(self.entry(doi=None), ["crossref", "dblp"], verify.Fetcher(None, True, 1, 0))
        finally:
            verify.LOOKUPS.clear()
            verify.LOOKUPS.update(original)
        self.assertEqual(record["bibliographic_status"], "verified")

    def test_author_or_year_conflict_is_reported(self):
        original = verify.LOOKUPS.copy()
        candidate = {"title": "Reliable Graph Learning", "authors": ["Other Person"], "year": 2024, "identifier": "x", "url": None, "exact_identifier": False}
        try:
            verify.LOOKUPS["dblp"] = lambda *_: (candidate, False)
            record = verify.verify_entry(self.entry(doi=None), ["dblp"], verify.Fetcher(None, True, 1, 0))
        finally:
            verify.LOOKUPS.clear()
            verify.LOOKUPS.update(original)
        self.assertEqual(record["bibliographic_status"], "conflicting")
        self.assertEqual(len(record["conflicts"]), 2)

    def test_source_failure_is_error_not_not_found(self):
        original = verify.LOOKUPS.copy()
        try:
            verify.LOOKUPS["crossref"] = lambda *_: (_ for _ in ()).throw(RuntimeError("service unavailable"))
            record = verify.verify_entry(self.entry(), ["crossref"], verify.Fetcher(None, True, 1, 0))
        finally:
            verify.LOOKUPS.clear()
            verify.LOOKUPS.update(original)
        self.assertEqual(record["bibliographic_status"], "error")

    def test_cache_supports_offline_replay(self):
        with tempfile.TemporaryDirectory() as tmp:
            cache = Path(tmp)
            online = verify.Fetcher(cache, False, 1, 0, opener=lambda *_args, **_kwargs: FakeResponse('{"ok": true}'))
            body, cached = online.get("crossref", "https://example.test/item")
            self.assertFalse(cached)
            offline = verify.Fetcher(cache, True, 1, 0, opener=lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("network used")))
            replay, cached = offline.get("crossref", "https://example.test/item")
            self.assertTrue(cached)
            self.assertEqual(body, replay)


if __name__ == "__main__":
    unittest.main()
