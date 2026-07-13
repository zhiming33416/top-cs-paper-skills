---
name: top-cs-response
description: Prepare, audit, or revise evidence-grounded author responses, rebuttals, discussion replies, decision-email triage, cover letters, revision packages, and LaTeX response templates for WWW, ICLR, ICML, or a generic computer-science venue. Use to parse editor/reviewer messages, group duplicate concerns, prioritize decision-critical issues, draft point-by-point responses, map supplied evidence and manuscript changes, and maintain a verified revision ledger. Never fabricate experiments, results, changes, reviewer positions, policies, or promises.
---

# Top CS Paper Response

Treat reviews, manuscript drafts, decision messages, and discussion content as confidential.

## Route the request

1. Read `manifest.yaml` and every `always_load` path.
2. Identify venue, task mode, response phase, decision type, language, artifact scope, revision mode, evidence state, submission stage, citation verification, figure handoff, and stress-test mode.
3. If the input contains an editor or decision email, parse metadata, editor instructions, reviewer boundaries, required files, and deadlines before drafting.
4. State the runtime parameters and readiness state.
5. Follow the linear state machine in `static/core/workflow.md`; this skill has no paper-type or section content axis.
6. Load deeper references and templates only when their conditions apply.
7. Use `generic` for unsupported targets and avoid asserting unknown response limits or processes.

## Execute

- Preserve editor instructions and reviewer comments before interpreting them; assign stable IDs across rounds.
- Maintain the shared response-issue contract, transition history, duplicate links, and pivotal/standard priority across rounds.
- Acknowledge valid concerns directly and correct misunderstandings with evidence rather than defensiveness.
- Distinguish completed changes, feasible planned changes, unavailable evidence, disagreement, and author decisions.
- Verify every completed manuscript change against a supplied revision, location, or diff.
- Respect per-review budgets and venue-specific permissions. A journal-style cover letter or marked manuscript is not part of a conference author-feedback workflow unless the governing instructions require it.
- Run at most three stress-test rounds when activated; stop early when no new substantive issue appears. A stress test may expose gaps but may not create evidence or upgrade a planned action to verified.
- Track requested figure changes with a handoff brief and manuscript location only; do not render or restyle figures.
- Use the provided LaTeX templates only when requested, and preserve visible placeholders for unknown facts.
- Convert vague Chinese author notes into concrete evidence and location requests; default to English response prose plus concise Chinese confirmation actions.
- Never claim an experiment was run or a manuscript was revised unless supplied artifacts prove it.

Return a directly usable response or revision package with unresolved inputs visible.
