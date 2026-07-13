# Development Guide

## Environment

Python 3.10 or newer is required for the helper scripts and test suite.

```bash
python -m pip install -r requirements.txt
```

The skills themselves are instruction bundles. Third-party Python dependencies are needed only for helper scripts, PDF inspection, or figure rendering.

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
python scripts/install_skills.py --target <temporary-skills-dir>
python scripts/install_skills.py --target <temporary-skills-dir> --check
```

## Common tools

```bash
python scripts/audit_submission.py --venue iclr --year 2026 --source paper.tex --pdf paper.pdf
python scripts/route_skill.py --skill top-cs-writing --venue iclr --paper-type empirical --section abstract --language zh-to-en --format json
python scripts/evaluate_skill_output.py --case tests/acceptance-cases.yaml --case-id iclr-abstract-from-chinese-notes --source notes.md --output draft.md
python scripts/verify_citations.py --bib references.bib --output citation-report.json --format json --cache-dir <cache-dir>
python skills/top-cs-polishing/scripts/check_latex_project.py --project paper --root main.tex --format json
python skills/top-cs-figure/scripts/render_from_figure_spec.py --spec tests/fixtures/figure-specs/comparison.yaml --outdir <output-dir>
python skills/top-cs-figure/scripts/check_figure_bundle.py --base <output-dir>/comparison --format json
```

Corpus derivation always uses an external corpus root. Raw downloads must remain outside this repository:

```bash
python scripts/collect_public_sources.py --config public-sources.yaml --cache-root <corpus-root> --dry-run
python scripts/collect_visual_style_corpus.py --corpus-root <corpus-root> --year 2026 --target-per-venue 30 --venues www,iclr,icml
python scripts/derive_corpus_evidence.py --corpus-root <corpus-root> --output-dir evidence/derived --schema-version 2
python scripts/derive_visual_style_evidence.py --corpus-root <corpus-root> --source-manifest evidence/derived/visual-style-source-manifest.yaml --output-dir evidence/derived
```

## Change discipline

- Keep official policy, corpus observations, synthetic examples, and author artifacts explicitly labeled.
- Do not commit raw corpus files, private evaluation suites, resolver caches, generated user figures, or credentials.
- Update tests and schemas with any interface change.
- Keep Chinese and English public README pages aligned.
- Run `git diff --check` before committing.
