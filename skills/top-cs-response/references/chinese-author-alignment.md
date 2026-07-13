# Chinese author alignment

Translate intent, not literal wording. Convert vague notes into evidence requirements before drafting English responses.

| Author note | Required handling |
|---|---|
| `我们已经改了` | Ask what changed, where it appears, and which artifact verifies it. |
| `我们补了实验` | Require experiment name, conditions, sample/run details, result, uncertainty, and figure/table location. |
| `我们补了分析` | Require method, data source, result, interpretation boundary, and location. |
| `审稿人误解了` | Treat first as a manuscript clarity problem; correct with evidence and a clarifying revision. |
| `这个问题不重要` | Explain the claim/evidence boundary or flag defensiveness; do not dismiss it. |
| `因为时间不够没做` | Do not use time as scientific justification; state a true scope/design boundary or mark unresolved. |
| `详见正文` | Require a stable section, page, equation, figure, table, or placeholder. |

Default output: polished English response text plus a concise `Chinese confirmation` list containing only missing facts, author decisions, and high-risk claims.
