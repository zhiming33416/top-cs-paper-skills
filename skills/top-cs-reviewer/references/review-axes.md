# Review axes

Provenance: named venue dimensions are `official-policy`; the questions and decomposition are `conservative-implementation`.

## Shared axes

### Correctness and soundness

- Is the formal, algorithmic, empirical, or systems reasoning internally valid?
- Are assumptions visible and consistent with experiments or proofs?
- Do conclusions follow from the supplied evidence rather than plausibility?

### Originality and positioning

- What exact capability, result, or understanding is claimed as new?
- Is the distinction from the closest verified work explicit and technically meaningful?
- Does the contribution change an assumption, regime, operating point, or evidence base?

Do not infer novelty from missing citations or the local corpus.

### Significance and relevance

- Which audience benefits and what decision or capability changes?
- Is the advance field-local, broadly reusable, or mainly incremental?
- For WWW, is Web and selected-track relevance explicit under current policy?

### Evidence and evaluation

- Which artifact directly supports each central claim?
- Are comparators, metrics, uncertainty, and evaluation scope appropriate?
- Are negative evidence, failures, and boundaries visible?

### Reproducibility

- Can a competent reader recover data, procedure, objective, selection, implementation, and measurement conditions?
- Which missing details threaten a central claim rather than merely convenience?

### Presentation and reader access

- Can a reviewer recover problem, distinction, evidence, reuse path, and boundary?
- Are terms defined, figures legible, equations motivated, and claims located near support?

### Ethics, anonymity, and compliance

- Are privacy, consent, licensing, misuse, societal impact, and disclosure issues addressed when relevant?
- Are anonymous artifacts and document metadata compliant with the verified venue profile?

## Venue mapping

- **ICML:** keep soundness, presentation, significance, and originality separately auditable; add limitations, societal impact, reproducibility, and ethics where applicable.
- **ICLR:** assess whether the stated contribution is substantiated, the main paper is self-contained, and discussion-stage verified revisions are incorporated when reviewing post-response material.
- **WWW Research:** assess technical merit, originality, impact, execution, presentation, related work, reproducibility, ethics, Web relevance, and track fit under the current profile.
- **Generic:** apply shared axes without inventing a score scale, page limit, response process, or mandatory section.

## Weighting

Weight axes by the central claim. A theoretical paper may be blocked by proof validity even when experiments are strong; a benchmark paper may be blocked by contamination or license defects even when model results are clear. Do not average away a central invalidity with presentation strengths.
