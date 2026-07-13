# Citation verification boundary

Use four distinct states for manuscript work:

1. `needed`: the proposition needs a source but no candidate is supplied.
2. `candidate`: a possible source is named but bibliographic identity is not verified.
3. `metadata-verified`: independent metadata supports that the work exists and the entry is substantially correct.
4. `claim-verified`: the cited source text has been inspected and supports the exact bounded proposition.

The verifier's `verified` bibliographic status maps only to `metadata-verified`. Never infer claim support, novelty, correctness, quality, or venue authority from metadata existence.

For unresolved cases, preserve `[CITATION NEEDED: proposition]`. Report title, author, year, or identifier conflicts instead of silently repairing a bibliography. When source text is unavailable, set claim entailment to `needs-source-text` or `not-checked`.

Use `_shared/scripts/verify_citations.py` for a supplied BibTeX file; the repository also exposes `scripts/verify_citations.py` as a CLI wrapper. Do not download paper full text. Treat service errors and offline cache misses as `error`, not `not-found`.
