# Intake and routing

Provenance: `conservative-implementation`; venue permissions come only from `official-policy`.

## Determine task mode

- `draft`: create responses from reviews and author evidence.
- `audit`: test an existing response for completeness, factuality, tone, and protocol.
- `revise`: repair an existing response while preserving verified facts.
- `triage-only`: classify concerns and request missing inputs without drafting factual answers.
- `cover-letter`: prepare only a revision cover letter when requested or required.
- `revision-package`: assemble tracker, response, ledger, cover letter, and permitted marked material.
- `latex-template`: instantiate selected assets while preserving placeholders.
- `appeal-like`: identify procedural basis and governing policy; do not draft a routine rebuttal.

## Identify phase and authority

Record venue, year, track, response phase, decision type, submission stage, interaction model, manuscript-revision permission, and live character budget. If any policy field is unverified, use `generic` behavior and a visible placeholder.

Do not assume that `major revision`, `rebuttal`, `discussion`, and `author feedback` permit the same actions.

## Inventory artifacts

| Artifact | Purpose | Missing consequence |
|---|---|---|
| Editor/decision message | decision, instructions, deadline, required files | cannot claim compliance |
| Full reviews/comments | stable item extraction | coverage cannot be verified |
| Submitted manuscript | existing-evidence and location checks | responses remain provisional |
| Revised manuscript | completed-change verification | changes stay `planned` |
| Diff | exact revision evidence | location/status confidence reduced |
| New analyses/results | factual response support | use `AUTHOR_INPUT_NEEDED` |
| Existing response draft | audit/revise mode | not needed for fresh draft |

## Readiness states

- `ready-to-submit`: all comments covered; facts, actions, and locations verified; protocol checked; no unresolved placeholders.
- `draft-with-placeholders`: structurally complete but contains visible location, metadata, or wording placeholders.
- `needs-author-input`: one or more factual answers require missing evidence or a scientific decision.
- `blocked`: credible completion is prevented by central evidence, integrity, policy, or confirmed appeal routing.

Readiness is package-level. Preserve item-level statuses separately.

## Minimum inputs by output

### Triage

Require review/editor text. Manuscript absence limits claim and location checks but does not block classification.

### Draft response

Require each comment plus author evidence or a clear `AUTHOR_INPUT_NEEDED` path. Do not transform a vague author assertion into a completed response.

### Submission-ready response

Require verified manuscript/revision locations, supplied result details, citation metadata, protocol limits, and resolution of every material placeholder.

### Cover letter

Require manuscript metadata, decision context, verified major changes, required-file list, and corresponding-author details or visible placeholders.

## Clarifying-question rule

Ask only questions that change factual content, action choice, protocol compliance, or readiness. Group them by issue ID and request the minimum fields. Do not delay triage or safe drafting for cosmetic preferences.

## Routing safeguards

- Appeal-like requests remain triage-only until policy and procedural basis are supplied.
- A conference response does not receive a journal cover letter or marked manuscript by default.
- A manuscript change cannot be `verified` without a supplied location, revision, or diff.
- Unknown character limits remain `[CHARACTER LIMIT NEEDED]`.
