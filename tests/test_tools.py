from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


corpus = load_script("build_corpus_manifest")
audit_mod = load_script("audit_submission")
install_mod = load_script("install_skills")


class CorpusClassificationTests(unittest.TestCase):
    def test_www_companion_never_becomes_main_style_evidence(self):
        result = corpus.classify("Companion Proceedings of the ACM Web Conference 2026 (WWW Companion '26)")
        self.assertEqual(result["venue"], "www")
        self.assertEqual(result["track"], "companion")
        self.assertEqual(result["use"], "comparison-only")

    def test_iclr_and_icml_explicit_markers(self):
        self.assertEqual(corpus.classify("Published as a conference paper at ICLR 2026")["status"], "verified-main")
        self.assertEqual(corpus.classify("Proceedings of the 43rd International Conference on Machine Learning")["venue"], "icml")

    def test_unverified_preprint_is_not_style_evidence(self):
        result = corpus.classify("Preprint: a promising paper")
        self.assertEqual(result["status"], "preprint")
        self.assertEqual(result["use"], "comparison-only")


class AuditTests(unittest.TestCase):
    def test_www_flags_identity_and_missing_web_relevance(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "paper.tex"
            source.write_text(
                "\\begin{abstract}A model.</abstract>\n\\section{Introduction}Test. alice@example.com\n\\bibliography{refs}",
                encoding="utf-8",
            )
            report = audit_mod.audit(source, "www", 2026, audit_mod.DEFAULT_POLICIES)
            codes = {item["code"] for item in report["findings"]}
            self.assertIn("anonymity-email", codes)
            self.assertIn("www-first-page-relevance", codes)

    def test_generic_does_not_assert_venue_policy(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "paper.md"
            source.write_text("# Abstract\nText\n# Introduction\nText\n# References\n", encoding="utf-8")
            report = audit_mod.audit(source, "generic", 2026, audit_mod.DEFAULT_POLICIES)
            self.assertIsNone(report["policy_source"])
            self.assertNotIn("main-page-limit", {item["code"] for item in report["findings"]})

    def test_www_companion_text_is_rejected_as_research_track(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "paper.md"
            source.write_text(
                "WWW Companion '26\n# Abstract\nWeb research\n# Introduction\nWeb platform\n# References\n",
                encoding="utf-8",
            )
            report = audit_mod.audit(source, "www", 2026, audit_mod.DEFAULT_POLICIES)
            self.assertIn("www-companion-mismatch", {item["code"] for item in report["findings"]})

    def test_numbered_plaintext_introduction_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "extracted.txt"
            source.write_text("ABSTRACT\nText\n1. INTRODUCTION\nText\nREFERENCES\n", encoding="utf-8")
            report = audit_mod.audit(source, "generic", 2026, audit_mod.DEFAULT_POLICIES)
            self.assertNotIn("missing-introduction", {item["code"] for item in report["findings"]})


class InstallTests(unittest.TestCase):
    def test_source_units_exist_and_compare_cleanly_after_copy(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            for unit in install_mod.UNITS:
                self.assertTrue((install_mod.SOURCE / unit).is_dir())
                import shutil
                shutil.copytree(install_mod.SOURCE / unit, target / unit)
                self.assertEqual(install_mod.differences(install_mod.SOURCE / unit, target / unit), [])
            self.assertTrue(install_mod.EVIDENCE.is_dir())

    def test_selected_units_include_shared_dependency(self):
        self.assertEqual(
            install_mod.selected_units(["top-cs-writing", "top-cs-figure"]),
            ("_shared", "top-cs-writing", "top-cs-figure"),
        )
        self.assertEqual(install_mod.selected_units(None), install_mod.UNITS)

    def test_single_skill_install_and_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            self.assertEqual(
                install_mod.main(["--target", str(target), "--skill", "top-cs-writing"]),
                0,
            )
            self.assertTrue((target / "top-cs-writing" / "SKILL.md").is_file())
            self.assertTrue((target / "_shared" / "evidence" / "derived" / "rules.yaml").is_file())
            self.assertFalse((target / "top-cs-figure").exists())
            self.assertEqual(
                install_mod.main(["--target", str(target), "--skill", "top-cs-writing", "--check"]),
                0,
            )

    def test_multiple_skill_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            result = install_mod.main(
                [
                    "--target",
                    str(target),
                    "--skill",
                    "top-cs-polishing",
                    "--skill",
                    "top-cs-reviewer",
                ]
            )
            self.assertEqual(result, 0)
            self.assertTrue((target / "top-cs-polishing" / "SKILL.md").is_file())
            self.assertTrue((target / "top-cs-reviewer" / "SKILL.md").is_file())
            self.assertFalse((target / "top-cs-writing").exists())

    def test_full_install_and_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            self.assertEqual(install_mod.main(["--target", str(target)]), 0)
            for unit in install_mod.UNITS:
                self.assertTrue((target / unit).is_dir())
            self.assertEqual(install_mod.main(["--target", str(target), "--check"]), 0)

    def test_default_target_is_codex_skills_directory(self):
        self.assertEqual(install_mod.default_target(), Path.home() / ".codex" / "skills")

    def test_list_mode_does_not_install(self):
        self.assertEqual(install_mod.main(["--list"]), 0)


if __name__ == "__main__":
    unittest.main()
