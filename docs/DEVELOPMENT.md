# Development Guide

## Environment

Python 3.10 or newer is required for the helper scripts and test suite.

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
```

The skills themselves are instruction bundles. Third-party runtime dependencies are needed only for helper scripts, PDF inspection, or figure rendering; `requirements-dev.txt` supplies the separate Ruff lint tool.

## Repository configuration

Maintainer-only source and policy configuration lives in <code>config/evidence/</code>. These files are versioned for routing, collection, and validation, but the installer intentionally does not copy them into a user's Codex skills directory. Public aggregate outputs that skills need at runtime remain in <code>evidence/derived/</code>.

## Validation

Run the complete unit and acceptance suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Validate derived evidence:

```bash
python scripts/validate_evidence.py --index evidence/derived/corpus-index.yaml --rules evidence/derived/rules.yaml --strict
```

Run public synthetic figure evaluations:

```bash
python skills/top-cs-figure/scripts/run_figure_evals.py
```

Smoke-test installation in an isolated directory:

```bash
python scripts/install_skills.py --host codex --target <temporary-skills-dir>
python scripts/install_skills.py --host codex --target <temporary-skills-dir> --check
python scripts/install_skills.py --workflow --host claude --target <temporary-skills-dir>
python scripts/install_skills.py --workflow --host claude --target <temporary-skills-dir> --check
python -m ruff check --select E9,F --ignore E402 scripts/install_skills.py scripts/route_skill.py skills/top-cs-paper-workflow tests/test_public_release.py
```

For the project-state tool, use a disposable, synthetic project root. Verify `init`, explicit relative-path `inventory`, advisory `status`, strict warnings, traversal rejection, and no-copy behavior. Do not run it against a contributor's home directory or a real manuscript in CI.

## Common tools

```bash
python scripts/audit_submission.py --venue iclr --year 2026 --source paper.tex --pdf paper.pdf
python scripts/route_skill.py --skill top-cs-writing --venue iclr --paper-type empirical --section abstract --language zh-to-en --format json
python scripts/evaluate_skill_output.py --case tests/cases/acceptance-cases.yaml --case-id iclr-abstract-from-chinese-notes --source notes.md --output draft.md
python scripts/verify_citations.py --bib references.bib --output citation-report.json --format json --cache-dir <cache-dir>
python skills/top-cs-polishing/scripts/check_latex_project.py --project paper --root main.tex --format json
python skills/top-cs-figure/scripts/render_from_figure_spec.py --spec tests/fixtures/figure-specs/comparison.yaml --outdir <output-dir>
python skills/top-cs-figure/scripts/check_figure_bundle.py --base <output-dir>/comparison --format json
```

Corpus derivation always uses an external corpus root. Raw downloads must remain outside this repository:

```bash
python scripts/collect_public_sources.py --config config/evidence/public-sources.yaml --cache-root <corpus-root> --dry-run
python scripts/collect_visual_style_corpus.py --corpus-root <corpus-root> --year 2026 --target-per-venue 30 --venues www,iclr,icml
python scripts/derive_corpus_evidence.py --corpus-root <corpus-root> --output-dir evidence/derived --schema-version 2
python scripts/derive_visual_style_evidence.py --corpus-root <corpus-root> --source-manifest evidence/derived/visual-style-source-manifest.yaml --output-dir evidence/derived
```

## Change discipline

- Keep official policy, corpus observations, synthetic examples, and author artifacts explicitly labeled.
- Do not commit raw corpus files, private evaluation suites, resolver caches, generated user figures, or credentials.
- Keep workflow manifests and local workflow outputs out of the repository root; only synthetic examples may be committed under `examples/` or `tests/fixtures/`.
- Update tests and schemas with any interface change.
- Keep Chinese and English public README pages aligned.
- Run `git diff --check` before committing.
