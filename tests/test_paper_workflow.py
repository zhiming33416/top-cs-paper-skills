from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "top-cs-paper-workflow" / "scripts" / "paper_workflow.py"
FIXTURE = ROOT / "tests" / "fixtures" / "workflow" / "valid-chain.yaml"
SCHEMA = ROOT / "skills" / "_shared" / "contracts" / "workflow-manifest.schema.yaml"


def load_workflow_module():
    spec = importlib.util.spec_from_file_location("paper_workflow", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


workflow = load_workflow_module()


class PaperWorkflowTests(unittest.TestCase):
    def run_main(self, *args: str) -> tuple[int, str, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = workflow.main(list(args))
        return result, stdout.getvalue(), stderr.getvalue()

    def test_init_creates_project_local_manifest_via_direct_script(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "paper-project"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT), "init", "--project", str(project)],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            manifest_path = project / ".top-cs-paper" / "workflow.yaml"
            self.assertTrue(manifest_path.is_file())
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(workflow.validate_manifest(manifest), [])
            self.assertEqual(manifest["project"]["author_confirmation"], "pending")

    def test_init_refuses_to_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "paper-project"
            self.assertEqual(self.run_main("init", "--project", str(project))[0], 0)
            manifest_path = project / ".top-cs-paper" / "workflow.yaml"
            original = manifest_path.read_text(encoding="utf-8")
            result, _, stderr = self.run_main("init", "--project", str(project))
            self.assertEqual(result, 2)
            self.assertIn("already exists", stderr)
            self.assertEqual(manifest_path.read_text(encoding="utf-8"), original)

    def test_inventory_hashes_only_explicit_in_project_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "paper-project"
            source = project / "paper" / "main.tex"
            source.parent.mkdir(parents=True)
            source.write_text("private source text must not be copied", encoding="utf-8")
            self.assertEqual(self.run_main("init", "--project", str(project))[0], 0)
            result, stdout, _ = self.run_main(
                "inventory", "--project", str(project), "--include", "paper/main.tex"
            )
            self.assertEqual(result, 0)
            self.assertIn("no file contents were copied", stdout)
            manifest = yaml.safe_load((project / ".top-cs-paper" / "workflow.yaml").read_text(encoding="utf-8"))
            self.assertEqual(manifest["materials"][0]["path"], "paper/main.tex")
            self.assertEqual(manifest["materials"][0]["kind"], "manuscript")
            self.assertNotIn("private source text", yaml.safe_dump(manifest))

    def test_inventory_rejects_traversal(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project = root / "paper-project"
            project.mkdir()
            (root / "outside.txt").write_text("outside", encoding="utf-8")
            self.assertEqual(self.run_main("init", "--project", str(project))[0], 0)
            result, _, stderr = self.run_main(
                "inventory", "--project", str(project), "--include", "../outside.txt"
            )
            self.assertEqual(result, 2)
            self.assertIn("safe relative path", stderr)
            manifest = yaml.safe_load((project / ".top-cs-paper" / "workflow.yaml").read_text(encoding="utf-8"))
            self.assertEqual(manifest["materials"], [])

    def test_inventory_rejects_internal_state_and_classifies_review_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "paper-project"
            self.assertEqual(self.run_main("init", "--project", str(project))[0], 0)
            result, _, stderr = self.run_main(
                "inventory", "--project", str(project), "--include", ".top-cs-paper/workflow.yaml"
            )
            self.assertEqual(result, 2)
            self.assertIn("cannot index workflow state", stderr)
            self.assertEqual(workflow.infer_material_kind("reviewer-comments.pdf"), "review")

    def test_schema_and_cli_reject_noncanonical_windows_paths_and_boolean_version(self):
        schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
        pattern = re.compile(schema["properties"]["materials"]["items"]["properties"]["path"]["pattern"])
        self.assertTrue(pattern.fullmatch("manuscript/main.tex"))
        for path in ("..\\private.tex", "\\\\server\\share\\paper.tex", "C:/paper.tex", "paper//main.tex"):
            with self.subTest(path=path):
                self.assertIsNone(pattern.fullmatch(path))
                self.assertFalse(workflow.is_safe_relative_path(path))
        manifest = workflow.initial_manifest()
        manifest["schema_version"] = True
        self.assertIn("schema_version must be 1", workflow.validate_manifest(manifest))

    def test_advisory_status_warns_but_strict_status_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "paper-project"
            self.assertEqual(self.run_main("init", "--project", str(project))[0], 0)
            result, markdown, _ = self.run_main("status", "--project", str(project))
            self.assertEqual(result, 0)
            self.assertIn("author-confirmation-pending", markdown)
            strict_result, json_output, _ = self.run_main(
                "status", "--project", str(project), "--format", "json", "--strict"
            )
            self.assertEqual(strict_result, 1)
            report = json.loads(json_output)
            self.assertTrue(report["strict"])
            self.assertGreater(report["warning_count"], 0)

    def test_empty_ready_checkpoints_fail_strict_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "paper-project"
            self.assertEqual(self.run_main("init", "--project", str(project))[0], 0)
            manifest_path = project / ".top-cs-paper" / "workflow.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["project"]["author_confirmation"] = "confirmed"
            manifest["checkpoints"] = {name: "ready" for name in manifest["checkpoints"]}
            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
            result, output, _ = self.run_main("status", "--project", str(project), "--format", "json", "--strict")
            self.assertEqual(result, 1)
            codes = {warning["code"] for warning in json.loads(output)["warnings"]}
            self.assertTrue(
                {"ready-claims-missing-handoff", "ready-evidence-missing-handoff", "ready-figures-missing-handoff", "ready-manuscript-missing-handoff"}.issubset(codes)
            )

    def test_complete_claim_evidence_figure_review_revision_chain_passes_strict(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "paper-project"
            self.assertEqual(self.run_main("init", "--project", str(project))[0], 0)
            manifest_path = project / ".top-cs-paper" / "workflow.yaml"
            manifest_path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
            result, output, stderr = self.run_main(
                "status", "--project", str(project), "--format", "json", "--strict"
            )
            self.assertEqual(result, 0, stderr)
            report = json.loads(output)
            self.assertEqual(report["warnings"], [])
            self.assertTrue(report["schema_valid"])


if __name__ == "__main__":
    unittest.main()
