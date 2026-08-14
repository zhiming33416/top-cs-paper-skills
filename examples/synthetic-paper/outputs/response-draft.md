# Output Sample: top-cs-response

> Synthetic demonstration output. The reviewer concern below is invented for the tutorial; no real review text is reproduced anywhere in this repository.

**Input:** one synthetic reviewer concern + [revision-ledger.md](../revision-ledger.md) + current revision state

## Issue board

| ID | Concern (paraphrased) | Class | Decision-critical | Linked revision |
| --- | --- | --- | --- | --- |
| `ISS-001` | "Figure 1 appears to show an empirical workflow result, but no experiment is described." | clarity / overclaim risk | yes | `REV-001` |

## Point-by-point response draft

**Reviewer concern ISS-001.**

> We thank the reviewer for identifying this ambiguity. Figure `FIG-001` is a conceptual workflow illustration, not an empirical result. We have updated the caption and the surrounding prose in Section [X] to state "conceptual workflow; no empirical result shown" (revision `REV-001`, status: `pending-author-confirmation`). We do not claim any measured outcome for this figure.

## What this response deliberately does not do

- It does not promise a new experiment: whether to run one remains an author decision recorded in `RSK-002`.
- It does not claim the revision is complete: `REV-001` stays `pending-author-confirmation` until the author verifies the final wording and location.
- It does not paraphrase reviewer text beyond what is needed to anchor the reply.

## Revision ledger update

| Revision | Linked issue | Status before | Status after response |
| --- | --- | --- | --- |
| `REV-001` | `ISS-001` / `RSK-001` | `pending-author-confirmation` | unchanged — a response is not evidence of a change |
