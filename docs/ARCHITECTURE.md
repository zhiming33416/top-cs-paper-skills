# Architecture

Top CS Paper Skills contains five installable skills and one shared resource directory. Each skill keeps its own stance, workflow, output contract, on-demand references, and task-specific scripts while reusing common evidence and venue material.

## Package layout

```text
skills/
├── _shared/                 # Common contracts, venue material, evidence rules, and scripts
├── top-cs-writing/
├── top-cs-polishing/
├── top-cs-reviewer/
├── top-cs-response/
└── top-cs-figure/
```

Each skill is installed as a complete directory. Router-style skills use:

- `SKILL.md` for the trigger, workflow entrypoint, and non-negotiable boundaries;
- `manifest.yaml` for always-loaded files, routing axes, and on-demand references;
- `static/core/` for stance, workflow, failure modes, and output contracts;
- `static/fragments/` for route-specific content;
- `references/` for detailed guidance loaded only when relevant;
- `scripts/` and `assets/` for executable or visual resources.

## Skill responsibilities

- `top-cs-writing` routes by venue, paper type, section, and language to plan or draft a manuscript.
- `top-cs-polishing` uses the same main axes but operates on existing prose or LaTeX and preserves source evidence.
- `top-cs-reviewer` treats venue as its content axis and takes manuscript scope and audit mode as runtime inputs.
- `top-cs-response` uses a linear issue-state workflow for review intake, evidence mapping, drafting, and revision verification.
- `top-cs-figure` owns figure contracts, rendering, descriptive statistics, visual grammar, export bundles, and image QA.

## Shared contracts

Writing, polishing, review, response, and figure work exchange machine-readable records for citations, figure briefs, render specs, response issues, and regression suites. The shared contracts prevent one skill from silently changing another skill's evidence or output assumptions.

## Installation boundary

The skills intentionally retain sibling references to `_shared`. Figure style routing also consumes repository-derived evidence that the installer places under `_shared/evidence/derived`. The installer therefore always copies shared resources even when the user selects only one skill.

## Compatibility

The repository preserves existing `SKILL.md`, manifest, and evidence interfaces. Public documentation and installation tooling may evolve, but changes to runtime contracts require corresponding schema, acceptance-test, and migration updates.
