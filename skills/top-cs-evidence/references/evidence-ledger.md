# Evidence ledger contract

Use one narrow claim per row. A ledger records IDs, metadata status, source-text status, and a safe relative path to an author-controlled note when supplied; it never embeds manuscript text, PDF text, or review text.

## Minimal workflow

1. Create `claim_id` and `statement` records.
2. Run metadata verification for supplied bibliography records.
3. Add a source record only after checking its relation to the exact claim.
4. Use `needs-source-text` when a source is identified but no author-provided excerpt or note can establish support.
5. Hand the resulting IDs to writing, review, or response work without copying source contents.

`supported`, `partial`, and `contradicted` describe an author-reviewed mapping, not an automated scholarly judgement.
