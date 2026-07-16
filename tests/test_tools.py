from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from unittest import mock
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
        self.assertEqual(
            install_mod.selected_units(None, workflow=True),
            (*install_mod.UNITS, install_mod.WORKFLOW_SKILL),
        )

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

    def test_default_targets_are_host_specific(self):
        self.assertEqual(install_mod.default_target(), Path.home() / ".codex" / "skills")
        self.assertEqual(install_mod.default_target("claude"), Path.home() / ".claude" / "skills")

    def test_codex_and_claude_targets_filter_host_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex_target = root / "codex-skills"
            claude_target = root / "claude-skills"
            self.assertEqual(
                install_mod.main(
                    ["--host", "codex", "--target", str(codex_target), "--skill", "top-cs-writing"]
                ),
                0,
            )
            self.assertEqual(
                install_mod.main(
                    ["--host", "claude", "--target", str(claude_target), "--skill", "top-cs-writing"]
                ),
                0,
            )
            self.assertTrue((codex_target / "top-cs-writing" / "agents" / "openai.yaml").is_file())
            self.assertFalse((claude_target / "top-cs-writing" / "agents" / "openai.yaml").exists())
            self.assertTrue((claude_target / "top-cs-writing" / "SKILL.md").is_file())
            self.assertTrue((codex_target / ".top-cs-paper-skills-codex.install.json").is_file())
            self.assertTrue((claude_target / ".top-cs-paper-skills-claude.install.json").is_file())
            self.assertEqual(
                install_mod.main(
                    ["--host", "claude", "--target", str(claude_target), "--skill", "top-cs-writing", "--check"]
                ),
                0,
            )

    def test_default_install_keeps_five_core_skills_not_optional_workflow(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            self.assertEqual(install_mod.main(["--target", str(target)]), 0)
            self.assertEqual(
                {path.name for path in target.iterdir() if path.is_dir()},
                set(install_mod.UNITS),
            )
            self.assertFalse((target / install_mod.WORKFLOW_SKILL).exists())

    def test_workflow_install_expands_to_all_dependencies(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            self.assertEqual(install_mod.main(["--target", str(target), "--workflow"]), 0)
            self.assertTrue((target / "_shared").is_dir())
            for unit in (*install_mod.SKILLS, install_mod.WORKFLOW_SKILL):
                self.assertTrue((target / unit / "SKILL.md").is_file())
            self.assertEqual(install_mod.main(["--target", str(target), "--workflow", "--check"]), 0)

    def test_check_detects_modified_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            self.assertEqual(install_mod.main(["--target", str(target), "--skill", "top-cs-writing"]), 0)
            skill_file = target / "top-cs-writing" / "SKILL.md"
            skill_file.write_text("user modification\n", encoding="utf-8")
            self.assertEqual(
                install_mod.main(["--target", str(target), "--skill", "top-cs-writing", "--check"]),
                1,
            )

    def test_check_and_prune_keep_user_modified_and_unrelated_files_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            self.assertEqual(install_mod.main(["--target", str(target), "--skill", "top-cs-writing"]), 0)
            unchanged = target / "top-cs-writing" / "legacy-unchanged.txt"
            modified = target / "top-cs-writing" / "legacy-modified.txt"
            sentinel = target / "another-project" / "keep.txt"
            unchanged.write_text("installed legacy\n", encoding="utf-8")
            modified.write_text("installed legacy\n", encoding="utf-8")
            sentinel.parent.mkdir(parents=True)
            sentinel.write_text("not owned\n", encoding="utf-8")

            manifest_file = install_mod.manifest_path(target, "codex")
            manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            manifest["files"]["top-cs-writing/legacy-unchanged.txt"] = install_mod._sha256(unchanged)
            manifest["files"]["top-cs-writing/legacy-modified.txt"] = install_mod._sha256(modified)
            manifest_file.write_text(json.dumps(manifest), encoding="utf-8")
            modified.write_text("user changed this legacy file\n", encoding="utf-8")

            self.assertEqual(
                install_mod.main(["--target", str(target), "--skill", "top-cs-writing", "--check"]),
                1,
            )
            self.assertEqual(install_mod.main(["--target", str(target), "--prune"]), 0)
            self.assertFalse(unchanged.exists())
            self.assertTrue(modified.exists())
            self.assertTrue(sentinel.exists())

            pruned_manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
            self.assertNotIn("top-cs-writing/legacy-unchanged.txt", pruned_manifest["files"])
            self.assertIn("top-cs-writing/legacy-modified.txt", pruned_manifest["files"])

    def test_installer_refuses_to_write_through_a_symlinked_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "skills"
            target.mkdir()
            with mock.patch.object(Path, "is_symlink", return_value=True):
                with self.assertRaisesRegex(RuntimeError, "symlinked install directory"):
                    install_mod._assert_unsymlinked_parent(
                        target,
                        Path("top-cs-writing") / "SKILL.md",
                    )

    def test_workflow_and_skill_selection_are_mutually_exclusive(self):
        with self.assertRaises(SystemExit) as error:
            install_mod.main(["--workflow", "--skill", "top-cs-writing"])
        self.assertEqual(error.exception.code, 2)

    def test_platform_wrappers_only_delegate_to_python_installer(self):
        powershell = (ROOT / "install.ps1").read_text(encoding="utf-8")
        shell = (ROOT / "install.sh").read_text(encoding="utf-8")
        self.assertIn("scripts/install_skills.py", powershell)
        self.assertIn("$RemainingArgs", powershell)
        self.assertIn("scripts/install_skills.py", shell)
        self.assertIn('"$@"', shell)

    def test_list_mode_does_not_install(self):
        self.assertEqual(install_mod.main(["--list"]), 0)


if __name__ == "__main__":
    unittest.main()
