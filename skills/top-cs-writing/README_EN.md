# `top-cs-writing` Skill

[中文说明](README.md) · [Repository home](../../README_EN.md)

Status: **Beta**

Plan arguments, organize sections, and draft papers for WWW, ICLR, ICML, or a generic computer-science venue from verifiable research material.

## What To Use It For

- Plan the central claims, evidence chain, and section architecture of a paper.
- Draft titles, abstracts, introductions, related work, methods, experiments, discussions, limitations, and conclusions.
- Turn Chinese research notes into evidence-constrained English drafts.
- Check terminology, figure references, and claim strength across sections.

## Typical Requests

- `Design the argument and section outline for an ICLR empirical paper from these results.`
- `Turn these Chinese method notes into an English Method section without inventing implementation details.`
- `Check whether the abstract, contribution list, and conclusion describe the same contributions.`

## What You Need To Provide

Provide a target venue or `generic` mode, paper type, target section, and available results, method notes, figures, citations, or author notes. Missing evidence should remain explicit.

## Outputs

Argument graphs, section plans, paragraph contracts, Chinese or English drafts, evidence-gap lists, and figure or citation handoffs when needed.

## Boundaries

The skill does not invent experiments, citations, data, implementation details, or venue policy. Use `top-cs-polishing` for sentence-level revision, and the review or response skill for those workflows.

## Runtime and Dependencies

The skill depends on sibling `skills/_shared` resources and derived evidence. Follow the [installation guide](../../INSTALL.md) and preserve the complete directory. The core writing workflow has no extra Python dependency.

## Related Skills

- [`top-cs-polishing`](../top-cs-polishing/README_EN.md): revise existing prose.
- [`top-cs-reviewer`](../top-cs-reviewer/README_EN.md): audit a submission draft.
- [`top-cs-figure`](../top-cs-figure/README_EN.md): render figures from a figure brief.
