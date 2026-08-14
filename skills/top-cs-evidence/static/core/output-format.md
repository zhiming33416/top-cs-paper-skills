# Evidence output format

Return:

1. `Route` — task mode, source access, source-text state, and venue in one line
2. `Claim list` — stable IDs and narrow statements
3. `Source plan` — evidence kind per claim
4. `Citation metadata ledger` — per-entry `verified` / `partial` / `conflicting` / `not-found`
5. `Claim-to-source map` — per-pair `supported` / `partial` / `contradicted` / `needs-source-text`
6. `Unresolved evidence gaps` — every `needs-source-text`, `[CITATION NEEDED: claim]`, and `AUTHOR_INPUT_NEEDED` item
7. `Handoff` — which specialist skill receives which IDs

For a single-lookup request, compress planning items but always keep the metadata-versus-entailment distinction and the gap list. Keep diagnostics in Chinese and ledger content in English unless requested otherwise.
