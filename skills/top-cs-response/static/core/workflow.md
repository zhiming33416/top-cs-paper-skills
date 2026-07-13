# Linear response state machine

Run all applicable stages in order:

1. **Intake:** identify venue, task mode, response phase, decision type, language, artifacts, and readiness.
2. **Parse:** when given an editorial message, extract manuscript metadata, decision, deadline, editor instructions, reviewer blocks, required files, and policy statements without guessing.
3. **Preserve:** retain editor/reviewer wording and boundaries; do not paraphrase away requirements.
4. **Identify:** assign stable IDs (`E.1`, `R1.1`, `R2.1`) and retain them across follow-up rounds.
5. **Classify:** record category, severity, affected claim, evidence need, response risk, reviewer priority, parent issue, and duplicate links under the shared issue schema.
6. **Strategize:** prioritize correctness and decision-critical issues; separate editor requirements from reviewer requests.
7. **Budget:** allocate the verified per-review or global character budget; use `[CHARACTER LIMIT NEEDED]` when unknown.
8. **Draft:** use acknowledgement -> direct answer -> evidence -> manuscript action -> remaining boundary.
9. **Verify:** attach each completed change to a supplied location and diff, or retain `[LOCATION NEEDED]`.
10. **Status:** use only `unresolved`, `evidence-needed`, `drafted`, `verified`, `planned`, `cannot-complete`, or `author-input-needed`; record every transition and require supplied evidence for `verified`.
11. **Stress test:** when activated, run one full round and at most two focused rounds; stop early when no new substantive issue appears.
12. **Package:** add a cover letter, marked-manuscript plan, or LaTeX files only when requested or required by the governing process. Track figure requests without generating figures.
13. **QA:** check coverage, provenance, commitments, cross-round consistency, tone, evidence, venue protocol, anonymity, placeholders, and unsupported claims.

Appeal-like requests remain triage-only unless the user explicitly confirms an appeal and supplies the governing policy. Do not apply journal revision-package conventions to conference rebuttal or discussion phases by default.
