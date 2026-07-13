# Response package

Provenance: `output-contract` and `conservative-implementation`; venue-required files are `official-policy` only when verified.

## Default assembly order

1. Parsed metadata and governing protocol.
2. Readiness and material risks.
3. Editor-instruction tracker.
4. Reviewer comment-response tracker.
5. Response strategy and budget allocation.
6. Point-by-point response.
7. Verified revision ledger.
8. Requested cover letter or marked-manuscript plan.
9. Missing-information and Chinese confirmation actions.

Omit components not requested or required. Do not imply that package completeness equals scientific adequacy.

## Strategy summary

State decision type, task mode, readiness, editor priority, central evidence risks, duplicate/conflicting reviewer clusters, and ordering. Keep it short enough to guide drafting rather than become another response letter.

## Point-by-point anatomy

For each item:

1. Preserve the full comment or a clearly marked faithful quotation.
2. State the action/status label.
3. Give a direct answer.
4. Provide supplied evidence.
5. Describe the verified or planned manuscript action.
6. Give location or `[LOCATION NEEDED]`.
7. State the remaining boundary.

Use new reviewer pages in print-oriented LaTeX when appropriate, but do not claim this is a venue requirement unless verified.

## Readiness states

- `ready-to-submit`: all facts and locations verified; no material placeholders.
- `draft-with-placeholders`: usable structure with visible unresolved metadata/location fields.
- `needs-author-input`: scientific facts or decisions missing.
- `blocked`: integrity, central evidence, policy, or appeal routing prevents credible completion.

## Cover letter boundary

Summarize verified major changes, manuscript metadata, and accompanying files. Keep it shorter than the response. Do not argue around unresolved issues or create a journal-style letter for conference author feedback unless required.

## Marked manuscript boundary

Work on a copy, preserve a clean version, and map every marked change to an issue ID. Distinguish proposed text from an actually revised manuscript. Respect phases that prohibit revised-paper upload.

## LaTeX assets

- `assets/cover-letter.tex.template`
- `assets/response-to-reviewers.tex.template`
- `assets/revision-ledger.tex.template`

Copy the selected asset to the requested output path and remove `.template` only after replacing or intentionally preserving all placeholders. Compile in isolation when an engine is available and report verification.

## Final delivery check

Ensure IDs are stable, editor items precede reviews, duplicates cross-reference consistently, every completed action has evidence, every planned action is labeled, budgets are respected, anonymity is preserved, and no unresolved placeholder is hidden.
