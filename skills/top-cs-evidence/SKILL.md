---
name: top-cs-evidence
description: Build and audit author-controlled claim-to-source evidence for top computer-science conference papers. Use for literature-positioning plans, BibTeX or DOI metadata checks, citation ledgers, claim-to-source maps, supplied source excerpts, and evidence handoffs to writing, review, or response work. Use only author-provided sources and explicit optional metadata lookup; never download full text, invent citations, or claim that a source supports a proposition without supplied source text or author notes.
---

# Top CS Evidence

Keep bibliographic identity, source-text support, and author conclusions as separate states.

## Route the request

1. Identify whether the user needs a search plan, metadata verification, claim-to-source mapping, or a handoff.
2. Treat supplied BibTeX, DOI, excerpts, PDFs, and notes as confidential author artifacts. Never copy their contents into project metadata.
3. Use `generic` evidence discipline unless a current, official venue profile is explicitly relevant.
4. Ask for the exact claims and sources when their absence changes the evidence ledger; otherwise mark the gap explicitly.

## Execute

Follow `static/core/workflow.md` in order and return the sections defined in `static/core/output-format.md`.

1. Create a claim list before looking for citations. Keep each claim narrow enough to verify.
2. Build a source plan that distinguishes background, positioning, method, and result evidence.
3. Run `scripts/paper_evidence.py verify` in offline mode by default. Use `--online` only when the author explicitly authorizes public Crossref, arXiv, and DBLP metadata queries.
4. Record metadata matches as `verified`, `partial`, `conflicting`, or `not-found`; metadata is never entailment.
5. Mark a source as supporting a claim only when the author supplies a relevant excerpt or note. Otherwise use `needs-source-text`.
6. Return a citation ledger and claim-to-source map for `top-cs-writing`, `top-cs-reviewer`, or `top-cs-response`; do not draft manuscript prose unless another specialist skill owns that task.

## Boundaries

- Do not download full text, scrape paywalled sources, modify a bibliography, or upload material.
- Do not infer novelty from a missing citation or turn metadata matches into scientific support.
- Do not claim that a venue currently requires a citation, checklist, or policy unless its official profile is current.
- Preserve unresolved items as `[CITATION NEEDED: claim]` or `AUTHOR_INPUT_NEEDED`.

## Resources

- `static/core/stance.md`, `static/core/workflow.md`, `static/core/output-format.md`: evidence stance, ordered workflow, and fixed output sections.
- `references/evidence-ledger.md`: input, output, and handoff contract.
- `references/source-boundaries.md`: source hierarchy and online-lookup boundary.
- `scripts/paper_evidence.py`: deterministic plan, verify, and map commands.
