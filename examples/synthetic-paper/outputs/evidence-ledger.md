# Output Sample: top-cs-evidence

> Synthetic demonstration output. The BibTeX keys below are invented and resolve to nothing; the point is the ledger format, not the sources.

**Input:** claim `CLM-001` + two author-supplied synthetic BibTeX entries + no excerpts

## Route

`task_mode=map-claims · source_access=offline · source_text_state=missing · venue=generic`

## Claim list

| ID | Statement |
| --- | --- |
| `CLM-001` | The manuscript will distinguish measured evidence, pending evidence, and author decisions. |

## Source plan

| Claim | Evidence kind | What a source must show |
| --- | --- | --- |
| `CLM-001` | positioning | Prior work that separates reported states in evaluation or provenance records |

## Citation metadata ledger

| BibTeX key | Metadata check (offline) | Status |
| --- | --- | --- |
| `syn2026provenance` | fields complete; year/venue internally consistent | `verified` (metadata only) |
| `syn2025audit` | missing DOI and venue field | `partial` |

## Claim-to-source map

| Claim | Source | Support status | Reason |
| --- | --- | --- | --- |
| `CLM-001` | `syn2026provenance` | `needs-source-text` | No author-provided excerpt establishes that the source discusses state separation |
| `CLM-001` | `syn2025audit` | `needs-source-text` | Metadata match only; metadata is never entailment |

## Unresolved evidence gaps

- `[CITATION NEEDED: CLM-001 positioning]` — both candidate sources await author-reviewed excerpts.
- `AUTHOR_INPUT_NEEDED` — authorize online metadata lookup (Crossref/arXiv/DBLP) or supply excerpts.

## Handoff

`claim-to-source map → top-cs-writing` (introduction gap paragraph); ledger IDs remain stable for later review and response work.
