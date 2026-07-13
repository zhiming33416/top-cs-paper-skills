---
name: top-cs-writing
description: Draft, restructure, or plan evidence-grounded computer-science conference papers for WWW, ICLR, ICML, or a generic venue. Use for paper outlines, titles, abstracts, introductions, related work, methods, experiments, discussions, limitations, conclusions, full manuscript arguments, Chinese research notes to English drafting, and LaTeX or Markdown section writing. Do not use for sentence-only polishing of a finished draft, reviewer-style auditing, or rebuttal writing.
---

# Top CS Paper Writing

Use the skill's static/dynamic layers; do not reconstruct venue rules or section logic from memory.

## Route the request

1. Read `manifest.yaml` and every path under `always_load`.
2. Detect `venue`, `paper_type`, `section`, and `language`; resolve artifact scope, evidence state, submission stage, citation verification, and figure handoff as runtime parameters.
3. State the detected values and any generic fallback in one short line so the user can correct them cheaply.
4. Load only the files mapped to the selected values. Load every selected section fragment.
5. Open `references/` only when an `on_demand` condition applies.
6. If the named venue/year is unsupported, use `generic` and tell the user to verify the current official guide.

## Execute

- Follow `static/core/workflow.md` in order.
- For a long section, load the rhetorical-moves reference and validate the topic-sentence scaffold before expanding prose.
- For full-manuscript work, build the argument graph and audit claim wording across sections before prose.
- Build the claim–evidence–boundary table before prose.
- Use explicit citation, figure/table, and appendix placeholders when artifacts are missing.
- Treat bibliographic verification and claim entailment as separate states. If a figure must be produced, return a figure brief; do not render it.
- Structure experiment prose around supplied claims and results; do not launch, monitor, or imply completion of experiments.
- Use placeholders for missing facts and list them under `缺失输入 / Missing inputs`.
- Default to Chinese diagnostics and English manuscript text.
- Preserve LaTeX commands, labels, citations, equations, and comments unless changing them is necessary and explicitly reported.
- Return a directly usable draft, not only advice.
