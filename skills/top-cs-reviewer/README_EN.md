# `top-cs-reviewer` Skill

[中文说明](README.md) · [Repository home](../../README_EN.md)

Status: **Beta**

Run a conservative author-side pre-submission audit for WWW, ICLR, ICML, or a generic computer-science venue to expose rejection risks and evidence gaps early.

## What To Use It For

- Check whether claims are supported by methods, experiments, figures, and citations.
- Audit experimental design, baselines, fairness, statistical reporting, and reproducibility.
- Check anonymity, scope, track, and venue fit.
- Prioritize revisions for a full manuscript or a partial section.

## Typical Requests

- `Audit this complete manuscript before ICLR submission and prioritize issues that could cause rejection.`
- `Review only the Experiments section for baseline fairness and reproducibility gaps.`
- `Assess whether this systems paper fits WWW Research or should use generic mode, and state the uncertainty.`

## What You Need To Provide

Provide the manuscript or an explicit section scope, target venue or track, and any available appendix, code description, experimental protocol, or anonymity context.

## Outputs

A scope statement, prioritized issues, severity, evidence locations, actionable revisions, missing information, and a readiness summary.

## Boundaries

This is an author-side simulation, not an official peer review or a substitute for domain experts. It does not impersonate reviewers, infer identities, or present unverified venue policy as certain.

## Runtime and Dependencies

The core audit has no extra Python dependency but requires complete `_shared`, venue-policy, and derived-evidence resources. See the [installation guide](../../INSTALL.md).

## Related Skills

- [`top-cs-writing`](../top-cs-writing/README_EN.md): rebuild the argument after an audit.
- [`top-cs-polishing`](../top-cs-polishing/README_EN.md): apply prose and LaTeX revisions.
- [`top-cs-response`](../top-cs-response/README_EN.md): handle actual reviewer feedback.
