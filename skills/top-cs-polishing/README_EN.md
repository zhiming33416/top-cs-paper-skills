# `top-cs-polishing` Skill

[中文说明](README.md) · [Repository home](../../README_EN.md)

Status: **Beta**

Translate, tighten, restructure, or diagnose computer-science prose and LaTeX while preserving evidence, technical meaning, and author intent.

## What To Use It For

- Faithful Chinese-to-English academic rewriting.
- Paragraph flow, section structure, terminology, and claim-strength revision.
- Removing redundancy, vague language, and generic AI phrasing.
- Auditing multi-file LaTeX projects, floats, overflow, and layout defects.

## Typical Requests

- `Rewrite this Chinese paragraph as concise English while preserving every number, dataset, and qualifier.`
- `Shorten this Related Work section by 20% without removing citations or comparison relationships.`
- `Diagnose the overfull boxes and figure-placement problems in this LaTeX project.`

## What You Need To Provide

Provide the source text or LaTeX project, target section and venue, plus terminology, facts, values, citations, and formatting constraints that must not change.

## Outputs

Revised prose or safe LaTeX edits, an explanation of material changes, preservation checks, risk notes, and a revision ledger when useful.

## Boundaries

The skill does not invent missing research content or turn weak evidence into strong conclusions. Use `top-cs-writing` for argument construction and `top-cs-reviewer` for submission-level review.

## Runtime and Dependencies

Core prose revision has no extra Python dependency. LaTeX QA uses locally available TeX tools and runs compilation in an isolated temporary directory. See the [installation guide](../../INSTALL.md).

## Related Skills

- [`top-cs-writing`](../top-cs-writing/README_EN.md): plan and draft content.
- [`top-cs-reviewer`](../top-cs-reviewer/README_EN.md): identify manuscript-level risks.
- [`top-cs-response`](../top-cs-response/README_EN.md): bind revisions to review issues.
