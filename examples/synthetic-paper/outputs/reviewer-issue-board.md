# Output Sample: top-cs-reviewer

> Synthetic demonstration output. This is an author-side pre-submission audit, not an official review, and it invents no reviewer.

**Input:** synthetic manuscript summary + [figure-brief.md](../figure-brief.md) + `venue=generic`

## Issue board (priority order)

### RSK-001 — conceptual figure could read as a measured result

| Field | Value |
| --- | --- |
| Anchor | `FIG-001` caption and Section [X] prose |
| Threatened claim | `CLM-001` |
| Consequence | A reviewer who reads the figure as empirical evidence will judge the paper as overclaiming, which threatens the core contribution rather than a detail |
| Confidence | high — the current caption omits the pending-evidence label |
| Fixability | low effort — caption and prose edit, no new experiment required |
| Resolution | Add "conceptual workflow; no empirical result shown" to caption and surrounding prose |
| Status | `open` |

### RSK-002 — introduction promises an audit benefit without linked evidence

| Field | Value |
| --- | --- |
| Anchor | Introduction, gap paragraph |
| Threatened claim | `CLM-001` |
| Consequence | Moderate — the claim survives, but an unsupported benefit statement invites a "no evaluation" objection |
| Confidence | medium — depends on whether `EVD-001` results arrive before submission |
| Fixability | medium — either supply the evaluation record or reword to a design goal |
| Resolution | `AUTHOR_INPUT_NEEDED`: decide between adding evidence and weakening the claim |
| Status | `open` |

## Not assessable

- Experimental soundness: no experiment exists in this synthetic package.
- Venue fit and formatting: no verified official venue profile was selected.

## Calibration note

Both issues are stated with explicit confidence levels. This board does not predict acceptance and does not substitute for domain experts.
