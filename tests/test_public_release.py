from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE_SKILLS = (
    "top-cs-writing",
    "top-cs-polishing",
    "top-cs-reviewer",
    "top-cs-response",
    "top-cs-figure",
)
WORKFLOW_SKILL = "top-cs-paper-workflow"
PUBLIC_TEXT_DIRECTORIES = (
    ROOT / ".github",
    ROOT / "config",
    ROOT / "docs",
    ROOT / "evidence",
    ROOT / "examples",
    ROOT / "scripts",
    ROOT / "skills",
)


def public_docs() -> list[Path]:
    docs = [
        ROOT / "README.md",
        ROOT / "README_EN.md",
        ROOT / "INSTALL.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "tests" / "README.md",
        *(ROOT / "docs").glob("*.md"),
        *(ROOT / "examples").rglob("*.md"),
    ]
    for skill in (*CORE_SKILLS, WORKFLOW_SKILL):
        docs.extend(
            [
                ROOT / "skills" / skill / "README.md",
                ROOT / "skills" / skill / "README_EN.md",
            ]
        )
    return sorted(docs)


def public_text_assets() -> list[Path]:
    suffixes = {".md", ".yaml", ".yml", ".json", ".py", ".ps1", ".sh", ".txt"}
    paths = [path for path in ROOT.iterdir() if path.is_file() and path.suffix.lower() in suffixes]
    for directory in PUBLIC_TEXT_DIRECTORIES:
        paths.extend(path for path in directory.rglob("*") if path.is_file() and path.suffix.lower() in suffixes)
    return sorted(set(paths))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class PublicReleaseTests(unittest.TestCase):
    def test_public_text_assets_contain_no_absolute_paths(self):
        forbidden = (
            re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]"),
            re.compile(r"/Users/[^/<\s]+/"),
            re.compile(r"/home/[^/<\s]+/"),
        )
        for path in public_text_assets():
            text = read_text(path)
            for pattern in forbidden:
                self.assertIsNone(pattern.search(text), f"absolute path in {path}: {pattern.pattern}")

    def test_public_docs_contain_no_personal_absolute_paths(self):
        forbidden = (
            re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
            re.compile(r"[A-Za-z]:\\桌面\\", re.IGNORECASE),
            re.compile(r"C:\\tmp\\", re.IGNORECASE),
            re.compile(r"/Users/[^/<\s]+/"),
            re.compile(r"/home/[^/<\s]+/"),
        )
        for path in public_docs():
            text = read_text(path)
            for pattern in forbidden:
                self.assertIsNone(pattern.search(text), f"personal path in {path}: {pattern.pattern}")

    def test_specialist_readme_pairs_exist_and_advertise_their_contracts(self):
        for skill in CORE_SKILLS:
            chinese = ROOT / "skills" / skill / "README.md"
            english = ROOT / "skills" / skill / "README_EN.md"
            self.assertTrue(chinese.is_file())
            self.assertTrue(english.is_file())
            self.assertIn("[English](README_EN.md)", read_text(chinese))
            self.assertIn("[中文说明](README.md)", read_text(english))
            self.assertIn("##", read_text(chinese), skill)
            self.assertIn("##", read_text(english), skill)

    def test_workflow_coordinator_is_optional_and_has_a_public_contract(self):
        workflow = ROOT / "skills" / WORKFLOW_SKILL
        expected = (
            workflow / "SKILL.md",
            workflow / "README.md",
            workflow / "README_EN.md",
            workflow / "manifest.yaml",
            workflow / "scripts" / "paper_workflow.py",
            workflow / "references" / "handoff-and-checkpoints.md",
            ROOT / "skills" / "_shared" / "contracts" / "workflow-manifest.schema.yaml",
        )
        for path in expected:
            self.assertTrue(path.is_file(), str(path))

        chinese = read_text(workflow / "README.md")
        english = read_text(workflow / "README_EN.md")
        self.assertIn("[English](README_EN.md)", chinese)
        self.assertIn("[中文说明](README.md)", english)
        self.assertIn("optional", english.lower())
        self.assertIn("five", english.lower())

        chinese_home = read_text(ROOT / "README.md")
        english_home = read_text(ROOT / "README_EN.md")
        self.assertIn(WORKFLOW_SKILL, chinese_home)
        self.assertIn(WORKFLOW_SKILL, english_home)
        self.assertIn("五个", chinese_home)
        self.assertIn("five", english_home.lower())

    def test_root_readme_pair_has_required_landing_sections_and_consistent_navigation(self):
        chinese = read_text(ROOT / "README.md")
        english = read_text(ROOT / "README_EN.md")
        required_chinese = (
            "## 适用范围与边界",
            "## 快速开始",
            "## 选择技能",
            "## 技能索引",
            "## 可选完整论文工作流",
            "## 项目结构与安装边界",
            "## 文档导航",
        )
        required_english = (
            "## Scope and Boundaries",
            "## Quick Start",
            "## Choose a Skill",
            "## Skill Index",
            "## Optional Full-paper Workflow",
            "## Repository Layout and Installation Boundary",
            "## Documentation",
        )
        for heading in required_chinese:
            self.assertIn(heading, chinese)
        for heading in required_english:
            self.assertIn(heading, english)
        for target in ("INSTALL.md", "docs/WORKFLOW.md", "docs/HOSTS.md", "docs/README.md"):
            self.assertIn(target, chinese)
            self.assertIn(target, english)

    def test_public_markdown_relative_links_resolve(self):
        link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        for path in public_docs():
            text = read_text(path)
            for raw_target in link_pattern.findall(text):
                target = raw_target.strip().split()[0]
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = target.split("#", 1)[0]
                resolved = (path.parent / target).resolve()
                self.assertTrue(resolved.exists(), f"broken link in {path}: {raw_target}")

    def test_installation_interface_is_documented_for_both_hosts(self):
        text = "\n".join(read_text(path) for path in (ROOT / "README.md", ROOT / "README_EN.md", ROOT / "INSTALL.md", ROOT / "docs" / "HOSTS.md"))
        for token in (
            "python scripts/install_skills.py",
            "--host codex",
            "--host claude",
            "--skill top-cs-writing",
            "--workflow",
            "--check",
            "--prune",
            "--target <skills-root>",
            "~/.codex/skills",
            "~/.claude/skills",
            "skills/_shared",
        ):
            self.assertIn(token, text)
        self.assertIn("does not write", text)
        self.assertIn("不会修改", text)

    def test_synthetic_workflow_example_is_complete_and_explicitly_non_private(self):
        example = ROOT / "examples" / "synthetic-paper"
        expected = (
            example / "README.md",
            example / "project-brief.md",
            example / "claims-evidence.yaml",
            example / "figure-brief.md",
            example / "review-issue.md",
            example / "revision-ledger.md",
        )
        for path in expected:
            self.assertTrue(path.is_file(), str(path))
        text = "\n".join(read_text(path) for path in expected)
        self.assertIn("synthetic", text.lower())
        self.assertIn("CLM-001", text)
        self.assertIn("FIG-001", text)
        self.assertIn("RSK-001", text)
        self.assertIn("pending", text.lower())

    def test_open_source_metadata_exists(self):
        expected = (
            ROOT / "LICENSE",
            ROOT / "requirements.txt",
            ROOT / "requirements-dev.txt",
            ROOT / "assets" / "top-cs-paper-skills-banner.png",
            ROOT / "config" / "evidence" / "data-preparation.yaml",
            ROOT / "config" / "evidence" / "public-sources.yaml",
            ROOT / "docs" / "README.md",
            ROOT / "docs" / "WORKFLOW.md",
            ROOT / "docs" / "HOSTS.md",
            ROOT / "tests" / "README.md",
            ROOT / "tests" / "cases" / "acceptance-cases.yaml",
            ROOT / "tests" / "cases" / "deep-acceptance-cases.yaml",
            ROOT / "tests" / "cases" / "figure-evals.yaml",
            ROOT / ".github" / "workflows" / "ci.yml",
            ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
            ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
        )
        for path in expected:
            self.assertTrue(path.is_file(), str(path))

    def test_root_has_no_maintenance_yaml(self):
        self.assertEqual(list(ROOT.glob("*.yaml")), [])
        self.assertFalse((ROOT / "corpus-sources.yaml").exists())


if __name__ == "__main__":
    unittest.main()
