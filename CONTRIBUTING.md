# Contributing

Contributions are welcome in Chinese or English. This repository keeps five specialist skills as its primary public interface; the optional `top-cs-paper-workflow` coordinates their handoffs and does not replace their individual contracts.

## Before opening a change

- Use an Issue for a new skill, host, venue, policy change, workflow schema, or behavior affecting several skills.
- Keep each pull request focused on one coherent user-visible change.
- Do not include unpublished manuscripts, reviewer correspondence, private evaluation data, downloaded papers, credentials, personal filesystem paths, or user project manifests.
- Do not copy third-party code, images, datasets, or distinctive text unless its license permits redistribution; retain required attribution and license notices.
- Cite an official source for venue-policy claims and record the applicable date or edition. Label corpus observations as soft evidence, not venue requirements.
- Do not let a workflow manifest turn a proposed claim, planned experiment, conceptual figure, or reviewer-risk label into evidence.

## Skill, workflow, and documentation changes

Every public specialist skill must keep `README.md` and `README_EN.md` aligned. Each pair should quickly state task fit, typical requests, required inputs, expected outputs, boundaries, dependencies, and related skills.

For changes to the optional workflow coordinator:

- preserve the five specialist skills as the first choice for a single-stage request;
- keep project state under a user-selected `.top-cs-paper/` directory, using relative paths and optional hashes only;
- reject traversal, absolute-path inventory, and unsafe link targets rather than scanning arbitrary user storage;
- make missing evidence and author confirmation advisory by default; reserve failing behavior for explicit `--strict` checks;
- add or update only synthetic, redistributable tutorial and test materials.

Detailed operational rules belong in `references/`, schemas, scripts, and docs rather than being copied into every public README.

## Validation

```bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_evidence.py --index evidence/derived/corpus-index.yaml --rules evidence/derived/rules.yaml --strict
python skills/top-cs-figure/scripts/run_figure_evals.py
python -m ruff check --select E9,F --ignore E402 scripts/install_skills.py scripts/route_skill.py skills/top-cs-paper-workflow tests/test_public_release.py
git diff --check
```

For installation changes, run isolated Codex and Claude Code targets, then repeat the same `--host`, `--skill`/`--workflow`, and `--target` scope with `--check`. Test `--prune` only against files owned by a disposable install target; it must preserve unrelated or user-modified skills. See [INSTALL.md](INSTALL.md) and [Host compatibility](docs/HOSTS.md).

## Pull requests

Describe what changed, why it is needed, user impact, evidence or source basis, and the checks you ran. New or changed behavior needs tests. Visual changes need synthetic, redistributable previews and provenance records. Workflow changes need an explicit statement of what remains author-confirmed.

By contributing, you agree that your contribution is licensed under the repository's [MIT License](LICENSE).
