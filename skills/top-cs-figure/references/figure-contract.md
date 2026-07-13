# Figure Contract

Use this before writing or editing plotting code.

## Minimum contract

```text
Figure ID:
Claim IDs:
Research question:
Purpose:
Visual family:
Data sources:
Data state:
Metric direction:
Panel map:
  a:
  b:
  c:
Expected observation:
Caption draft:
Manuscript callout:
Final size:
Export formats:
Unresolved inputs:
```

## Rules

- If a shared figure brief is supplied, preserve its IDs, evidence status, panel jobs, caption draft, and manuscript callout unless the user explicitly asks for revision.
- If only data and a target chart are supplied, infer a provisional contract and state assumptions before styling.
- If data are missing, planned, or unverified, do not produce result-like values. Use placeholders or a labeled layout mockup.
- Every panel must have one evidence job. Merge or drop panels that do not change the reader's ability to assess the claim.
- Treat expected observations as design targets until supplied data establish them.
