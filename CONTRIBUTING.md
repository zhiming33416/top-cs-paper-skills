# Contributing

欢迎使用中文或英文提交 Issue 和 Pull Request。Contributions are welcome in Chinese or English.

## Before opening a change

- Use an Issue for new skills, new venue support, policy changes, or behavior that affects several skills.
- Keep a pull request focused on one coherent change.
- Do not include unpublished manuscripts, reviewer correspondence, private evaluation data, downloaded papers, credentials, or personal filesystem paths.
- Do not copy third-party code, images, datasets, or distinctive text unless its license permits redistribution; retain required attribution and license notices.
- Cite an official source for venue-policy claims and record the date or edition to which the claim applies.
- Label corpus observations as soft evidence rather than venue requirements.

## Skill documentation

Every public skill must keep `README.md` and `README_EN.md` aligned. Each pair should let a reader quickly determine:

- what the skill is for;
- typical requests;
- required inputs;
- expected outputs;
- boundaries and refusal conditions;
- runtime dependencies and related skills.

Detailed rules belong in `references/`, `static/`, schemas, or scripts rather than being duplicated in the public README.

## Validation

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_evidence.py --index evidence/derived/corpus-index.yaml --rules evidence/derived/rules.yaml --strict
python skills/top-cs-figure/scripts/run_figure_evals.py
git diff --check
```

If a change affects installation, also run an isolated install and `--check` as described in [INSTALL.md](INSTALL.md).

## Pull requests

Describe what changed, why it is needed, user impact, evidence or source basis, and the checks you ran. New or changed behavior should include tests. Visual changes should include synthetic, redistributable previews and provenance records.

By contributing, you agree that your contribution is licensed under the repository's [MIT License](LICENSE).
