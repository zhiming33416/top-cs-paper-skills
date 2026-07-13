# Synthetic anchored-review example

Provenance: `synthetic-example`. The facts below are invented solely to demonstrate output structure.

## Input summary

The fictional paper claims lower inference cost for a retrieval model. Table 3 reports latency but omits hardware, batch size, throughput, and retrieval quality at the compared operating point.

## Example issue

| Field | Content |
|---|---|
| ID | E1 |
| Anchor | Table 3; Section 4.2 |
| Observation | Latency values are reported without hardware, batch size, concurrency, or matched retrieval quality. |
| Threatened claim | `The method provides lower inference cost than prior systems.` |
| Evidence | Table 3 supplies latency only. |
| Consequence | The comparison cannot distinguish method efficiency from hardware, batching, or a lower-quality operating point. |
| Severity | major |
| Confidence | high |
| Resolution | Report hardware, precision, batch size, concurrency, measurement boundary, throughput, and quality at matched operating points; otherwise narrow the claim. |
| Fixability | analysis-needed |

## Example narrative

Strength: the paper identifies a practically relevant bottleneck and reports an end-to-end measurement rather than only parameter count.

Concern: the current evidence does not yet support the comparative cost claim because the operating points are not recoverable. This is not a request for unrelated scaling experiments; it is the minimum context required to interpret the reported table.

Decision-relevant question: were all methods measured on the same hardware, precision, batch size, concurrency, and retrieval-quality target? If not, which comparison can be made at a matched operating point?

Revision priority: repair Table 3 and Section 4.2 before polishing presentation. If matched measurements are unavailable, narrow the abstract and conclusion from comparative efficiency to the observed latency under the authors' setup.

## Anti-patterns

- `The experiments are weak.` No anchor, claim, or consequence.
- `Please test on more datasets.` No explanation of which scope claim requires them.
- `This should be rejected.` Editorial decision without a reasoned author-side audit.
- `Reviewer 2, a systems expert, believes...` Invented identity and role.
