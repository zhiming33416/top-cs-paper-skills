# Action and status mapping

Provenance: `conservative-implementation` and `output-contract`.

## Action labels

- `ACCEPT_TEXT`: clarify, define, reorganize, or correct manuscript text.
- `ACCEPT_ANALYSIS`: add a supplied analysis or result without implying a new experiment.
- `ACCEPT_EXPERIMENT`: report a supplied completed experiment with design and result details.
- `ADD_REPORTING`: add versions, hardware, sample/run details, metrics, statistics, or artifact instructions.
- `SOFTEN_CLAIM`: narrow scope, causality, generality, novelty, significance, or efficiency wording.
- `CITE_OR_POSITION`: add a verified citation or correct a close-work comparison.
- `CLARIFY_EXISTING`: point to supplied evidence already in the manuscript and improve discoverability.
- `DISAGREE_WITH_EVIDENCE`: explain why the requested conclusion does not follow, using an artifact or scope argument.
- `PARTIAL`: address the supported portion and expose the unresolved remainder.
- `CANNOT_COMPLETE`: state a genuine design, evidence, integrity, or policy boundary and narrow the claim.
- `AUTHOR_INPUT_NEEDED`: do not draft factual content until minimum evidence is supplied.
- `ESCALATE_INTEGRITY`: stop routine polishing and surface a potential ethics, compliance, or data-integrity issue.

## Item statuses

- `unresolved`: concern is preserved but no evidence-grounded disposition exists yet.
- `evidence-needed`: a named artifact or source is required before drafting can be factual.
- `drafted`: a grounded reply exists but has not passed final verification.
- `verified`: supplied artifact verifies every factual answer and claimed action/location.
- `planned`: scientifically feasible action is proposed but not verified as complete.
- `cannot-complete`: action is unavailable or inapplicable under a stated scientific or policy boundary.
- `author-input-needed`: an author decision or fact is missing.

## Tracker schema

| ID | Preserved concern | Category | Severity | Affected claim | Action | Evidence | Location | Status | Risk |
|---|---|---|---|---|---|---|---|---|---|

Use a stable action/status pair. `ACCEPT_EXPERIMENT + verified` requires supplied design, result, and manuscript evidence; an author note saying `we ran it` is insufficient for a final package.

## Common mappings

- Undefined term -> `ACCEPT_TEXT`, usually minor, location required.
- Missing run count -> `ADD_REPORTING`; use `AUTHOR_INPUT_NEEDED` until supplied.
- Unsupported causal claim -> `SOFTEN_CLAIM` or supplied causal analysis.
- Existing table overlooked -> `CLARIFY_EXISTING` plus local manuscript clarification.
- Requested citation -> `CITE_OR_POSITION` only after relevance and metadata verification.
- Impossible longitudinal evidence in a cross-sectional study -> `PARTIAL` or `CANNOT_COMPLETE` plus claim narrowing and limitation.
- Potential data fabrication or policy breach -> `ESCALATE_INTEGRITY`, not a polished compliance claim.
