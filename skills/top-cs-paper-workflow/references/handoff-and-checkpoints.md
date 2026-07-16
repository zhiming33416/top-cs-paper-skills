# Workflow handoffs and checkpoints

The workflow manifest is a small project-state record, not a second manuscript. Keep only identifiers, statuses, relative paths, and hashes. The paper, data, PDF, reviewer text, and citation text stay in the user-selected project and are never copied by the tool.

## Checkpoints

| Checkpoint | Ready means | Normal owner |
| --- | --- | --- |
| `brief` | The contribution target and venue context are confirmed or explicitly generic. | writing |
| `claims` | Claims have stable IDs and are linked to their evidence needs. | writing |
| `evidence-and-figures` | Evidence and figure briefs are linked honestly; planned or unverified work remains visible. | figure + writing |
| `manuscript` | The project has completed its chosen drafting/refinement pass. | writing + polishing |
| `review` | Pre-submission findings are either resolved, recorded, or marked not applicable. | reviewer |
| `response` | Each reviewer issue is linked to a concrete revision or an explicit unresolved state. | response |

`ready` is a workflow checkpoint, not a correctness or acceptance claim. Use `not-applicable` for stages that genuinely do not apply; do not use it merely to silence a warning.

## Handoff links

Use reciprocal links whenever the referenced object exists:

```text
claim.evidence_ids <-> evidence.claim_ids
claim.figure_ids   <-> figure.claim_ids
review.revision_ids <-> revision.issue_ids
```

A figure may be a method overview and may have no data evidence. If its `evidence_status` is `available`, an evidence link is normally expected; otherwise keep its planned, partial, missing, or unverified state explicit. `top-cs-figure` owns figure rendering and visual QA.

## Status interpretation

`status` validates the metadata shape, then reports incomplete checkpoints, unresolved links, unverified evidence, and pending author confirmation as warnings. Advisory mode exits zero after a valid manifest. `--strict` treats every such warning as a block and returns non-zero. Structural errors always return non-zero.

Use the status output to decide the next specialist skill. It does not replace current venue policies, bibliography verification, experiment execution, or human authorship judgment.
