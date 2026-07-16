# Top CS Paper Skills

[中文说明](README.md) · [Installation](INSTALL.md) · [Full-paper workflow](docs/WORKFLOW.md) · [Host compatibility](docs/HOSTS.md) · [Skill index](#skill-index) · [Documentation](docs/README.md) · [Contributing](CONTRIBUTING.md)

[![CI](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Specialist skills](https://img.shields.io/badge/specialist_skills-5-6f42c1)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)

![Top CS Paper Skills: evidence-grounded Codex skills for leading CS conferences](assets/top-cs-paper-skills-banner.png)

Five specialist skills for computer-science paper workflows: argument design and drafting, fidelity-preserving polishing, pre-submission review, reviewer responses, and reproducible scientific figures. They share evidence boundaries, traceable inputs and outputs, and conservative claims. An optional `top-cs-paper-workflow` coordinator supports long-running, cross-skill paper projects; it is not a sixth specialist skill.

## Scope and Boundaries

- The current venue-evidence snapshot covers WWW Research, ICLR, and ICML 2026. Always re-check a target venue's official pages before submission.
- `generic` mode offers general writing, review, and evidence checks; it never presents historical patterns as a venue's current policy.
- The repository releases only original code, documentation, synthetic figures, and aggregate evidence. It contains no full papers, review text, private experiment data, user artifacts, or credentials.
- The full-paper workflow records only relative paths and optional hashes for files explicitly selected by the user. It neither copies nor uploads manuscripts, data, PDFs, or review material.
- Read [Evidence and provenance](docs/EVIDENCE.md) for sources, snapshot coverage, limitations, and privacy boundaries.

## Quick Start

The easiest route is to send this prompt to Codex:

~~~text
Install all Top CS Paper Skills from https://github.com/zhiming33416/top-cs-paper-skills.git into Codex.
Clone the repository and run:
python scripts/install_skills.py --host codex
python scripts/install_skills.py --host codex --check
Preserve the complete skills/top-cs-* folders, skills/_shared, and derived evidence;
do not copy only SKILL.md. When finished, remind me to start a new Codex session.
~~~

Or install manually:

~~~bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python scripts/install_skills.py --host codex
python scripts/install_skills.py --host codex --check
~~~

For a full paper that crosses several stages, install the optional coordinator too:

~~~bash
python scripts/install_skills.py --workflow --host codex
python scripts/install_skills.py --workflow --host codex --check
~~~

The default target is `~/.codex/skills`. See [INSTALL.md](INSTALL.md) for individual skills, Claude Code, updates, `--prune`, Windows/macOS/Linux, and troubleshooting.

## Choose a Skill

| Goal | Start with | You provide | You receive |
| --- | --- | --- | --- |
| Build a paper from results and ideas | [top-cs-writing](skills/top-cs-writing/README_EN.md) | Research question, findings, target section | Argument structure, outline, English draft |
| Translate, compress, or revise LaTeX faithfully | [top-cs-polishing](skills/top-cs-polishing/README_EN.md) | Existing prose or LaTeX and revision scope | Revised text and an auditable change ledger |
| Find technical and experimental risks before submission | [top-cs-reviewer](skills/top-cs-reviewer/README_EN.md) | Manuscript, appendix, venue, audit mode | Prioritized author-side risk audit |
| Reply to reviews and track revisions | [top-cs-response](skills/top-cs-response/README_EN.md) | Reviews, evidence, revision state | Issue matrix, point-by-point response, revision ledger |
| Produce or audit submission-ready figures | [top-cs-figure](skills/top-cs-figure/README_EN.md) | Figure brief, CSV, or render spec | Editable figures, export bundle, visual QA report |
| Coordinate a full paper across specialist skills | [top-cs-paper-workflow](skills/top-cs-paper-workflow/README_EN.md) (optional) | An explicitly selected project root and stage-material inventory | Status checks, gap warnings, and handoff list |

## Skill Index

| Skill | Stage | You provide | Deliverable | Typical request |
| --- | --- | --- | --- | --- |
| [top-cs-writing](skills/top-cs-writing/README_EN.md) | Plan and draft | Contributions, evidence, paper type, section, venue | Argument graph, outline, draft, evidence gaps | “Use top-cs-writing to plan an ICLR introduction from these results.” |
| [top-cs-polishing](skills/top-cs-polishing/README_EN.md) | Revise faithfully | Chinese/English prose or LaTeX and goal | Revised version, change ledger, unresolved inputs | “Use top-cs-polishing to turn this Chinese paragraph into concise academic English without strengthening claims.” |
| [top-cs-reviewer](skills/top-cs-reviewer/README_EN.md) | Audit before submission | Manuscript, experiments, appendix, venue | Technical, experimental, reproducibility, and scope risks | “Use top-cs-reviewer to identify likely rejection risks in this WWW manuscript.” |
| [top-cs-response](skills/top-cs-response/README_EN.md) | Discuss and revise | Reviews, completed evidence, revision state | Response draft, evidence map, revision ledger | “Use top-cs-response to turn these reviews into point-by-point responses and a revision plan.” |
| [top-cs-figure](skills/top-cs-figure/README_EN.md) | Produce and QA figures | Data, figure brief, export needs | SVG/PDF/PNG bundle, render record, QA report | “Use top-cs-figure to produce editable benchmark and ablation figures from this CSV.” |

Every specialist-skill page defines its task fit, inputs, outputs, boundaries, dependencies, and related skills. `skills/_shared` is a shared dependency, not a sixth standalone skill.

## Optional Full-paper Workflow

For a task confined to one stage, invoke the corresponding specialist skill directly. For a paper that moves through drafting, figures, review, and response, install the optional coordinator and keep resumable state under a user-selected project root:

~~~text
Contribution and argument -> Evidence and principal figures -> Manuscript and polish -> Pre-submission review -> Response and revision
     top-cs-writing              top-cs-figure              top-cs-polishing        top-cs-reviewer       top-cs-response
                 └──────────────── top-cs-paper-workflow (optional coordination and status checks) ────────────────┘
~~~

| Handoff | Traceable information | Consumed by | Author confirmation that cannot be automated |
| --- | --- | --- | --- |
| Writing → figure | claim ID, evidence state, figure brief | `top-cs-figure` | Whether data supports the claim |
| Figure → review | figure ID, render record, QA result | `top-cs-reviewer` | Caption, readability, and conclusion consistency |
| Review → response | risk/issue ID, evidence gap, action | `top-cs-response` | Whether a new experiment or revision is promised |
| Response → manuscript | response ID, revision ID, final location | `top-cs-polishing` / `top-cs-writing` | Whether the edit accurately reflects completed work |

The coordinator keeps its manifest at `<project-root>/.top-cs-paper/`. It reports gaps as warnings by default; only `--strict` treats a declared-ready but incomplete handoff as a failure. See [Full-paper workflow](docs/WORKFLOW.md) for commands, stages, and privacy rules.

## Figure Examples

All previews below are generated from deterministic synthetic inputs and repository renderers. They contain neither paper screenshots nor user data.

| Benchmark and ablation | Systems scaling tradeoff | Venue-aware example |
| --- | --- | --- |
| ![Benchmark and ablation](skills/top-cs-figure/assets/gallery/benchmark-ablation.png) | ![Systems scaling tradeoff](skills/top-cs-figure/assets/gallery/systems-scaling-tradeoff.png) | ![ICML heatmap](skills/top-cs-figure/assets/gallery/icml-heatmap-venue.png) |

`unified-family` is a reusable generic palette and hierarchy system, not an official visual policy of any venue or journal. See [palette profiles](skills/top-cs-figure/references/palette-profiles.md) for venue-aware profiles, generic fallback behavior, and evidence provenance.

## Repository Layout and Installation Boundary

~~~text
.
├── .github/                 # CI, Issue templates, and PR template
├── assets/                  # README visual assets; not installed
├── config/evidence/         # Maintainer source and policy configuration; not installed
├── docs/                    # Architecture, evidence, workflow, and development docs
├── evidence/derived/        # Public aggregate evidence installed with shared resources
├── examples/synthetic-paper/ # Redistributable cross-skill tutorial materials
├── scripts/                 # Installation, routing, collection, and validation tools
├── skills/
│   ├── _shared/             # Contracts, venue material, and shared resources
│   ├── top-cs-paper-workflow/ # Optional coordinator
│   └── top-cs-*/            # Five installable specialist packages
└── tests/                   # Synthetic tests, acceptance, and figure-regression fixtures
~~~

The installer copies only selected skills, `skills/_shared`, and `evidence/derived`. `assets/`, `config/`, `docs/`, `examples/`, `scripts/`, and `tests/` support presentation, maintenance, and contribution; they are not installed into a user's skills directory. Read [tests/README.md](tests/README.md) for the public-test boundary.

## Documentation

| Document | Read it when |
| --- | --- |
| [Installation guide](INSTALL.md) | Installing, selecting skills, updating, using another host, or troubleshooting. |
| [Full-paper workflow](docs/WORKFLOW.md) | Coordinating handoffs, project state, or strict checks. |
| [Host compatibility](docs/HOSTS.md) | Choosing installation targets for Codex or Claude Code. |
| [Architecture](docs/ARCHITECTURE.md) | Understanding shared resources, routing, and compatibility boundaries. |
| [Evidence and provenance](docs/EVIDENCE.md) | Checking sources, snapshots, licensing, or privacy boundaries. |
| [Development guide](docs/DEVELOPMENT.md) | Running tests, updating evidence, or maintaining scripts. |
| [Documentation index](docs/README.md) | Browsing all public maintainer documentation. |

## Development and Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and the [development guide](docs/DEVELOPMENT.md) before proposing rules, skills, scripts, or documentation. Public CI runs the complete suite on Ubuntu and Windows with Python 3.10 and 3.12, plus macOS installation and routing smoke checks.

~~~bash
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_evidence.py --index evidence/derived/corpus-index.yaml --rules evidence/derived/rules.yaml --strict
python skills/top-cs-figure/scripts/run_figure_evals.py
python -m ruff check --select E9,F --ignore E402 scripts/install_skills.py scripts/route_skill.py skills/top-cs-paper-workflow tests/test_public_release.py
~~~

Issues and pull requests are welcome in Chinese or English. Do not contribute private manuscripts, reviewer correspondence, credentials, raw corpora, or third-party material that cannot be redistributed.

## License

This project is available under the [MIT License](LICENSE). MIT applies only to this repository's original code, documentation, and synthetic assets; linked venue sites, papers, templates, and other third-party material remain subject to their own terms.
