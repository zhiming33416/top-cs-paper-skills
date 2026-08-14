# Evidence workflow

Follow these steps in order. Skip a step only when its inputs are absent, and record the skip as a gap.

1. **Claim inventory.** List each claim with a stable `claim_id` and a statement narrow enough to verify. Split compound claims.
2. **Source plan.** For each claim, state what kind of evidence it needs: background, positioning, method, or result. Distinguish claims the paper must prove from claims it only needs to situate.
3. **Metadata verification.** Run `scripts/paper_evidence.py verify` offline by default. Use `--online` only after the author explicitly authorizes public Crossref, arXiv, and DBLP metadata lookup. Record each entry as `verified`, `partial`, `conflicting`, or `not-found`.
4. **Claim-to-source mapping.** Mark a source as `supported`, `partial`, or `contradicted` only when the author supplies a relevant excerpt or note for that exact claim. Otherwise mark `needs-source-text`.
5. **Handoff.** Return the citation ledger and claim-to-source map with stable IDs for `top-cs-writing`, `top-cs-reviewer`, or `top-cs-response`. Do not copy source contents into the handoff.

Ask the author at most two high-leverage questions when their answers change the ledger; otherwise proceed and mark gaps explicitly.
