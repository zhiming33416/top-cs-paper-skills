# Output Sample: top-cs-writing

> Synthetic demonstration output. Every identifier, note, and sentence is invented; placeholders mark everything an author must supply.

**Input:** [project-brief.md](../project-brief.md) + [claims-evidence.yaml](../claims-evidence.yaml)

## Route

`venue=generic (unverified) · paper_type=systems · section=introduction · language=en · evidence_state=sparse`

## Central argument

Evaluation reports become auditable when measured evidence, pending evidence, and author decisions are recorded as separate, linkable states (`CLM-001`).

## Claim–evidence–boundary table

| Claim | Evidence | Status | Boundary |
| --- | --- | --- | --- |
| `CLM-001` separation of evidence states | `EVD-001` planned evaluation record | `pending-author-input` | Workflow claim, not a performance result; must not imply measured improvement |

## Introduction outline (paragraph jobs)

1. **Context** — why audit trails for evaluation claims matter. `[CITATION NEEDED: prior work on evaluation reporting]`
2. **Gap** — reports conflate measured results with intentions. `[CITATION NEEDED: motivating example]`
3. **Position** — introduce the three-state separation (`CLM-001`).
4. **Evidence preview** — reference the planned record `EVD-001`; do not state outcomes.
5. **Contributions** — one bullet per verifiable claim; no claim without a linked evidence ID.

## Draft excerpt

> Evaluation reports often present intended measurements and completed measurements in the same voice, which makes audits unnecessarily difficult. We propose recording each claim in one of three explicit states — measured evidence, pending evidence, or author decision — so that a reader can verify what was actually observed. `[FIGURE: FIG-001 conceptual workflow]` Our evaluation plan is described in Section [X]; results remain `PENDING-AUTHOR-INPUT` in this draft.

## Missing inputs

- Experiment results for `EVD-001` (author must supply; no outcome is assumed).
- Citations for context and gap paragraphs (see `top-cs-evidence` handoff).
- Confirmed target venue and current official author instructions.
