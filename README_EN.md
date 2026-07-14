# Top CS Paper Skills

[中文说明](README.md) · [Installation](INSTALL.md) · [Skill index](#skill-index) · [Documentation](docs/README.md) · [Contributing](CONTRIBUTING.md)

[![CI](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-5-6f42c1)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)

Five Codex skills for computer-science paper workflows: argument design and drafting, fidelity-preserving polishing, pre-submission review, reviewer responses, and reproducible scientific figures. They share evidence boundaries, traceable inputs and outputs, and conservative claims.

## Scope and Boundaries

- The current venue evidence snapshot covers WWW Research, ICLR, and ICML 2026. Always re-check the target venue's official pages before submission.
- <code>generic</code> mode offers general writing, review, and evidence checks; it never presents historical patterns as a venue's current policy.
- The repository releases only original code, documentation, synthetic figures, and aggregate evidence. It contains no full papers, review text, private experiment data, user artifacts, or credentials.
- Read [Evidence and provenance](docs/EVIDENCE.md) for sources, snapshot coverage, limitations, and privacy boundaries.

## Quick Start

The easiest route is to send this prompt to Codex:

~~~text
Install all Codex skills from https://github.com/zhiming33416/top-cs-paper-skills.git.
Clone the repository, run python scripts/install_skills.py, then run
python scripts/install_skills.py --check. Preserve the complete skills/top-cs-*,
skills/_shared, and derived evidence directories; do not copy only SKILL.md.
When finished, remind me to start a new Codex session.
~~~

Or install manually:

~~~bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python scripts/install_skills.py
python scripts/install_skills.py --check
~~~

The default target is <code>~/.codex/skills</code>. See [INSTALL.md](INSTALL.md) for skill selection, updates, Windows/macOS/Linux instructions, and troubleshooting.

## Choose a Skill

| Goal | Start with | You provide | You receive |
| --- | --- | --- | --- |
| Build a paper from results and ideas | [top-cs-writing](skills/top-cs-writing/README_EN.md) | Research question, findings, target section | Argument structure, outline, English draft |
| Translate, compress, or revise LaTeX faithfully | [top-cs-polishing](skills/top-cs-polishing/README_EN.md) | Existing prose or LaTeX and revision scope | Revised text and an auditable change ledger |
| Find technical and experimental risks before submission | [top-cs-reviewer](skills/top-cs-reviewer/README_EN.md) | Manuscript, appendix, venue, audit mode | Prioritized author-side risk audit |
| Reply to reviews and track revisions | [top-cs-response](skills/top-cs-response/README_EN.md) | Reviews, evidence, revision state | Issue matrix, point-by-point response, revision ledger |
| Produce or audit submission-ready figures | [top-cs-figure](skills/top-cs-figure/README_EN.md) | Figure brief, CSV, or render spec | Editable figures, export bundle, visual QA report |

## Skill Index

| Skill | Stage | You provide | Deliverable | Typical request |
| --- | --- | --- | --- | --- |
| [top-cs-writing](skills/top-cs-writing/README_EN.md) | Plan and draft | Contributions, evidence, paper type, section, venue | Argument graph, outline, draft, evidence gaps | “Use top-cs-writing to plan an ICLR introduction from these results.” |
| [top-cs-polishing](skills/top-cs-polishing/README_EN.md) | Revise faithfully | Chinese/English prose or LaTeX and goal | Revised version, change ledger, unresolved inputs | “Use top-cs-polishing to turn this Chinese paragraph into concise academic English without strengthening claims.” |
| [top-cs-reviewer](skills/top-cs-reviewer/README_EN.md) | Audit before submission | Manuscript, experiments, appendix, venue | Technical, experimental, reproducibility, and scope risks | “Use top-cs-reviewer to identify likely rejection risks in this WWW manuscript.” |
| [top-cs-response](skills/top-cs-response/README_EN.md) | Discuss and revise | Reviews, completed evidence, revision state | Response draft, evidence map, revision ledger | “Use top-cs-response to turn these reviews into point-by-point responses and a revision plan.” |
| [top-cs-figure](skills/top-cs-figure/README_EN.md) | Produce and QA figures | Data, figure brief, export needs | SVG/PDF/PNG bundle, render record, QA report | “Use top-cs-figure to produce editable benchmark and ablation figures from this CSV.” |

Every skill page defines its task fit, inputs, outputs, boundaries, dependencies, and related skills. <code>skills/_shared</code> is a shared dependency, not a sixth standalone skill.

## Workflow

~~~text
Research evidence and contributions
        ↓
top-cs-writing ──────────→ top-cs-figure
        ↓                       ↕
top-cs-polishing       Figure QA / revision / export
        ↓                       ↕
top-cs-reviewer ─────────→ top-cs-response
~~~

Use the figure skill while drafting principal figures, auditing readability and evidence consistency before submission, or creating supplemental and revision figures during response. No skill invents experiments, citations, reviewer positions, or venue policies.

## Figure Examples

All previews below are generated from deterministic synthetic inputs and repository renderers. They contain neither paper screenshots nor user data.

| Benchmark and ablation | Systems scaling tradeoff | Venue-aware example |
| --- | --- | --- |
| ![Benchmark and ablation](skills/top-cs-figure/assets/gallery/benchmark-ablation.png) | ![Systems scaling tradeoff](skills/top-cs-figure/assets/gallery/systems-scaling-tradeoff.png) | ![ICML heatmap](skills/top-cs-figure/assets/gallery/icml-heatmap-venue.png) |

<code>unified-family</code> is a reusable generic palette and hierarchy system, not an official visual policy of any venue or journal. See [palette profiles](skills/top-cs-figure/references/palette-profiles.md) for venue-aware profiles, generic fallback behavior, and evidence provenance.

## Repository Layout

~~~text
.
├── .github/                 # CI, Issue templates, and PR template
├── config/evidence/         # Maintainer source and policy configuration; not installed
├── docs/                    # Architecture, evidence, and development documentation
├── evidence/derived/        # Public aggregate evidence installed with shared resources
├── scripts/                 # Installation, routing, collection, and validation tools
├── skills/
│   ├── _shared/             # Contracts, venue material, and resources shared by all skills
│   └── top-cs-*/            # Five installable skill packages
├── tests/
│   ├── cases/               # Executable public acceptance and figure-evaluation matrices
│   └── fixtures/            # Small synthetic inputs and public mock records
├── README.md
├── README_EN.md
├── INSTALL.md
├── CONTRIBUTING.md
├── requirements.txt
└── LICENSE
~~~

The installer copies only the selected <code>skills/top-cs-*</code>, <code>skills/_shared</code>, and <code>evidence/derived</code>. <code>config/</code>, <code>docs/</code>, <code>scripts/</code>, and <code>tests/</code> support maintenance and contribution; they are not installed into a user's Codex skills directory. Read [tests/README.md](tests/README.md) for the public-test boundary.

## Documentation

| Document | Read it when |
| --- | --- |
| [Installation guide](INSTALL.md) | Installing, selecting skills, updating, or troubleshooting. |
| [Skill index and detail pages](#skill-index) | Choosing a task owner or checking a skill's I/O contract. |
| [Architecture](docs/ARCHITECTURE.md) | Understanding shared resources, routing, and compatibility boundaries. |
| [Evidence and provenance](docs/EVIDENCE.md) | Checking sources, snapshots, licensing, or privacy boundaries. |
| [Development guide](docs/DEVELOPMENT.md) | Running tests, updating evidence, or maintaining scripts. |
| [Documentation index](docs/README.md) | Browsing all maintainer-facing documentation. |

## Development and Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [development guide](docs/DEVELOPMENT.md) before proposing rules, skills, scripts, or documentation. Public CI runs unit tests, evidence validation, and figure evaluations on Ubuntu and Windows with Python 3.10 and 3.12.

~~~bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_evidence.py --index evidence/derived/corpus-index.yaml --rules evidence/derived/rules.yaml --strict
python skills/top-cs-figure/scripts/run_figure_evals.py
~~~

Issues and pull requests are welcome in Chinese or English. Do not contribute private manuscripts, reviewer correspondence, credentials, raw corpora, or third-party material that cannot be redistributed.

## License

This project is available under the [MIT License](LICENSE). MIT applies only to this repository's original code, documentation, and synthetic assets; linked venue sites, papers, templates, and other third-party material remain subject to their own terms.
