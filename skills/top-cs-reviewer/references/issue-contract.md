# Review issue contract

Represent each substantive concern with these fields:

| Field | Requirement |
|---|---|
| ID | Stable identifier such as `T1`, `E2`, or `V1`. |
| Anchor | Page, section, paragraph, equation, theorem, figure, table, or explicit missing artifact. |
| Observation | What is visible in the supplied material, without inferred intent. |
| Threatened claim | Exact central or supporting claim affected. |
| Evidence | Manuscript evidence supporting the concern; state `not supplied` when bounded. |
| Consequence | Why the issue matters for correctness, evidence, reproducibility, or venue fit. |
| Severity | `blocking`, `major`, `minor`, `question`, or `not assessable`. |
| Confidence | `high`, `medium`, or `low`, based on supplied scope and directness. |
| Resolution | Smallest evidence, analysis, proof, clarification, or claim narrowing that resolves it. |
| Fixability | `text-only`, `analysis-needed`, `experiment-needed`, `proof-needed`, `policy/compliance`, or `author-decision`. |

Example pattern:

`E2 | Table 3 and Sec. 4.2 | The efficiency claim reports latency without hardware or batch size | "lower inference cost" | Table 3 | The comparison cannot be interpreted at an equivalent operating point | major | high | report matched hardware, batch size, and throughput/quality tradeoff | analysis-needed`

Do not use severity as tone. A major issue needs a major consequence for the paper's central case, not merely a strong reviewer preference.
