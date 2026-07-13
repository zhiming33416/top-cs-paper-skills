# `top-cs-response` Skill

[中文说明](README.md) · [Repository home](../../README_EN.md)

Status: **Beta**

Parse editor and reviewer feedback, then bind issues, evidence, response text, and manuscript revisions into a verifiable response package.

## What To Use It For

- Organize decision emails, reviews, discussions, or revision requests.
- Merge duplicate concerns and maintain stable issue IDs and states.
- Draft point-by-point responses, rebuttals, cover letters, and revision ledgers.
- Verify that claimed experimental, textual, and figure changes were actually completed.

## Typical Requests

- `Merge these three reviews into a prioritized issue board and draft point-by-point responses.`
- `Check whether this rebuttal promises experiments that have not been completed.`
- `Generate a response letter and revision ledger from the revised manuscript and reviewer comments.`

## What You Need To Provide

Provide the complete editor or reviewer text, target venue, current response phase, available evidence, revised manuscript, experiment results, and commitments that must not be made.

## Outputs

An issue board, point-by-point responses, evidence mappings, revision locations, unresolved actions, cover letters, and LaTeX response templates.

## Boundaries

The skill does not invent experiment results, manuscript changes, reviewer attitudes, venue policies, or future promises. Missing evidence remains an explicit placeholder and author action.

## Runtime and Dependencies

Templates and the core workflow have no extra Python dependency. Citation-verification helpers use packages listed in the repository `requirements.txt`. See the [installation guide](../../INSTALL.md).

## Related Skills

- [`top-cs-reviewer`](../top-cs-reviewer/README_EN.md): find issues before real review.
- [`top-cs-polishing`](../top-cs-polishing/README_EN.md): apply promised prose changes.
- [`top-cs-figure`](../top-cs-figure/README_EN.md): revise figures raised by reviewers.
