# Top CS Evidence

[中文说明](README.md)

Build author-controlled claim-to-source evidence for conference papers: plan literature positioning, verify BibTeX/DOI metadata, record source relationships, and hand unresolved gaps to writing, review, or response work.

## Task fit

- Plan citations for contributions, related work, or reviewer responses.
- Verify author-provided BibTeX, DOI, or arXiv metadata.
- Map author-provided excerpts or notes to a specific claim.

## Inputs and deliverables

Provide a claim list, BibTeX/DOIs, and optional author excerpts or notes. Receive a source plan, citation ledger, claim-to-source map, and gap list. The skill never invents citations or manuscript prose.

## Quick use

```bash
python scripts/paper_evidence.py plan --claims claims.yaml --output evidence-plan.yaml
python scripts/paper_evidence.py verify --bib references.bib --output citation-ledger.yaml
python scripts/paper_evidence.py verify --bib references.bib --output citation-ledger.yaml --online
```

Offline mode is the default. Only `--online` queries public Crossref, arXiv, and DBLP metadata; it never downloads full text.

## Boundaries and related skills

Verified metadata does not establish that a source supports a claim. Mark claim entailment as supported only with an author-provided excerpt or note. Hand the ledger to `top-cs-writing`, `top-cs-reviewer`, or `top-cs-response`; use `top-cs-paper-workflow` for project-level IDs and status.
