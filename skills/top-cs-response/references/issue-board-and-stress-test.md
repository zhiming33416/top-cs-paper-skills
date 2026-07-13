# Issue board and response stress test

Use the routed `skills/_shared/contracts/response-issue.schema.yaml` as the record contract. Preserve stable issue IDs across rounds. Link duplicate concerns with `duplicate_of`, but keep each reviewer-facing reply self-contained.

## State rules

Allowed states are `unresolved`, `evidence-needed`, `drafted`, `verified`, `planned`, `cannot-complete`, and `author-input-needed`.

- Start at `unresolved` unless a missing artifact already requires `evidence-needed` or `author-input-needed`.
- Move to `drafted` when a grounded reply exists but has not passed response QA.
- Move to `verified` only when every factual statement and claimed manuscript action has supplied support.
- Use `planned` for feasible future work or manuscript edits not verified in a supplied revision.
- Use `cannot-complete` when the requested work cannot be completed in the response window; explain the bounded alternative.
- Record every transition with round and reason. Never transition `planned` to `verified` without new supplied evidence.

## Up-to-three-round stress test

1. Round 1 audits the full response for coverage, provenance, commitments, tone, contradictions, venue protocol, and unsupported claims.
2. Rounds 2 and 3 audit only pivotal or unresolved issues plus changes made since the previous round.
3. Stop early when the round introduces no new substantive issue. Stop after round 3 even if preferences remain.

The stress test may challenge reasoning, identify missing evidence, or narrow wording. It may not create results, citations, manuscript changes, reviewer positions, or policy. Treat feedback produced in the same context as an adversarial self-check, not independent reviewer evidence.

For each round return new issues, resolved issues, remaining pivotal issues, forbidden state transitions, and a stop/continue decision with reason.
