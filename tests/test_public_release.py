from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "top-cs-writing",
    "top-cs-polishing",
    "top-cs-reviewer",
    "top-cs-response",
    "top-cs-figure",
)


def public_docs() -> list[Path]:
    docs = [
        ROOT / "README.md",
        ROOT / "README_EN.md",
        ROOT / "INSTALL.md",
        ROOT / "CONTRIBUTING.md",
        *(ROOT / "docs").glob("*.md"),
    ]
    for skill in SKILLS:
        docs.extend(
            [
                ROOT / "skills" / skill / "README.md",
                ROOT / "skills" / skill / "README_EN.md",
            ]
        )
    return sorted(docs)


class PublicReleaseTests(unittest.TestCase):
    def test_public_docs_contain_no_personal_absolute_paths(self):
        forbidden = (
            re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
            re.compile(r"[A-Za-z]:\\桌面\\", re.IGNORECASE),
            re.compile(r"C:\\tmp\\", re.IGNORECASE),
            re.compile(r"/Users/[^/<\s]+/"),
            re.compile(r"/home/[^/<\s]+/"),
        )
        for path in public_docs():
            text = path.read_text(encoding="utf-8")
            for pattern in forbidden:
                self.assertIsNone(pattern.search(text), f"personal path in {path}: {pattern.pattern}")

    def test_skill_readme_pairs_exist_and_have_matching_sections(self):
        for skill in SKILLS:
            chinese = ROOT / "skills" / skill / "README.md"
            english = ROOT / "skills" / skill / "README_EN.md"
            self.assertTrue(chinese.is_file())
            self.assertTrue(english.is_file())
            zh_sections = [line for line in chinese.read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
            en_sections = [line for line in english.read_text(encoding="utf-8").splitlines() if line.startswith("## ")]
            self.assertEqual(len(zh_sections), len(en_sections), skill)
            self.assertEqual(len(zh_sections), 7, skill)
            self.assertIn("[English](README_EN.md)", chinese.read_text(encoding="utf-8"))
            self.assertIn("[中文说明](README.md)", english.read_text(encoding="utf-8"))

    def test_root_readme_pair_has_matching_sections(self):
        chinese = (ROOT / "README.md").read_text(encoding="utf-8")
        english = (ROOT / "README_EN.md").read_text(encoding="utf-8")
        zh_sections = [line for line in chinese.splitlines() if line.startswith("## ")]
        en_sections = [line for line in english.splitlines() if line.startswith("## ")]
        self.assertEqual(len(zh_sections), len(en_sections))
        self.assertEqual(len(zh_sections), 9)

    def test_public_markdown_relative_links_resolve(self):
        link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        for path in public_docs():
            text = path.read_text(encoding="utf-8")
            for raw_target in link_pattern.findall(text):
                target = raw_target.strip().split()[0]
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = target.split("#", 1)[0]
                resolved = (path.parent / target).resolve()
                self.assertTrue(resolved.exists(), f"broken link in {path}: {raw_target}")

    def test_installation_interface_is_documented(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        install = (ROOT / "INSTALL.md").read_text(encoding="utf-8")
        for token in (
            "python scripts/install_skills.py",
            "--skill top-cs-writing",
            "--check",
            "--list",
            "~/.codex/skills",
            "skills/_shared",
        ):
            self.assertIn(token, readme + install)

    def test_open_source_metadata_exists(self):
        expected = (
            ROOT / "LICENSE",
            ROOT / "requirements.txt",
            ROOT / ".github" / "workflows" / "ci.yml",
            ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
        )
        for path in expected:
            self.assertTrue(path.is_file(), str(path))


if __name__ == "__main__":
    unittest.main()
