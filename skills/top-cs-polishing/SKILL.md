---
name: top-cs-polishing
description: Polish, translate, tighten, structurally revise, or diagnose existing computer-science manuscript prose and LaTeX for WWW, ICLR, ICML, or a generic venue while preserving evidence. Use for Chinese-to-English academic rewriting, paragraph flow, section-level revision, claim calibration, concision, terminology consistency, reducing generic AI prose, revision ledgers, and LaTeX layout or float-placement problems. Do not use to invent a paper from sparse notes, simulate peer review, or write a reviewer response.
---

# Top CS Paper Polishing

## Route the request

1. Read `manifest.yaml` and every `always_load` path.
2. Detect and state venue, paper type, section, language, revision mode, artifact scope, evidence state, submission stage, citation verification, and figure handoff.
3. Load only the static fragments mapped to those values.
4. Open deeper references only when an `on_demand` condition applies.
5. Use `generic` for unsupported venue/year combinations and warn that official rules require verification.

## Execute

1. Extract immutable facts: quantities, comparison direction, conditions, citations, equations, uncertainty, and explicit boundaries.
2. Build or update the terminology ledger for multi-paragraph work.
3. Diagnose in this order: framing, rhetorical structure, evidence connection, terminology, and sentence form.
4. Respect the selected revision mode: keep `light-edit` local, permit reordering in `structural-revision`, and prove information preservation in `compression`.
5. Revise in the order `paper role -> section job -> paragraph logic -> claim/evidence/boundary -> sentence form`.
6. Record every material change and any claim-strength, citation, or figure-reference shift in the revision ledger.
7. Verify preserved facts, citations, LaTeX, terminology, and reader workflow; report what was compiled, rendered, structurally checked, or not verified.

Preserve scientific meaning and never silently strengthen novelty, causality, generality, or significance. Preserve LaTeX commands, labels, citations, equations, and comments unless a necessary change is explicitly reported. For a supplied LaTeX project, run `scripts/check_latex_project.py` when an engine is available; never enable shell escape or write build artifacts into the source project.

When auditing figures, check claim, caption, callout, terminology, and label alignment only. Return a corrected handoff brief when necessary; do not render or restyle the figure. Metadata verification does not establish that a cited source supports the manuscript claim.

For page-layout or float-placement requests, load `references/latex-layout.md`, compile to an isolated output directory, and inspect rendered pages before and after. Do not judge layout from source alone.

Default to Chinese revision notes and English revised prose. Return paste-ready text, not only advice.
