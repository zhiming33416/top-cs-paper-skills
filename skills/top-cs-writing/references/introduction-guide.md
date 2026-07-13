# Introduction drafting guide

Provenance: contribution previews and common related-work placement are `corpus-derived`; the reasoning variants and examples below are `conservative-implementation` and `synthetic-example`.

## Work backward before drafting forward

Answer first:

1. What exact claim should a reviewer remember?
2. Which result most directly supports it?
3. Which capability gap makes that result consequential?
4. Which closest approach families fail to close the gap, under what assumptions?
5. Why should the target venue's readers care?

Then draft forward: relevance -> bottleneck -> existing approaches -> remaining gap -> present answer -> contribution-evidence map.

## Paragraph map

### Paragraph 1: problem and relevance

Name the task, setting, and consequence of failure. For WWW, make Web relevance and track relevance explicit when the verified policy requires it. Do not rely on a Web dataset or platform name as the relevance argument.

### Paragraph 2: technical bottleneck

Explain why the problem is hard in operational terms: information unavailable, assumptions violated, optimization unstable, cost prohibitive, evaluation incomplete, or deployment conditions changed. Avoid generic statements such as `real-world data are complex`.

### Paragraphs 3-n: approach-family synthesis

Group work by strategy, information assumption, optimization target, or operating point. For each family: state capability, enabling assumption, and remaining limitation for the present setting. Use verified citations; do not create a straw man.

### Gap paragraph

State the missing capability that follows from the prior analysis. A defensible gap is not `few studies have used X`; it is `available methods cannot provide Y under Z conditions` with support.

### Present-work paragraph

Give the central answer, mechanism-level intuition, and boundary. Do not front-load low-level architecture.

### Contribution-evidence preview

For each contribution record capability, technical move, direct evidence, and boundary. Keep at most the contributions needed to establish the central thesis.

## Select a framing variant

### Existing task, unresolved technical constraint

Lead with the established task and isolate the constraint prior methods share.

### New task or setting

First justify why the task is distinct and measurable. Then explain why simply applying existing methods does not answer it. Avoid declaring a task new without literature verification.

### Observation-driven method

Lead from a supplied empirical or theoretical observation to the design requirement. Distinguish the observation from the proposed explanation.

### Systems requirement

Lead with service-level or resource requirements, then show why existing operating points are unsuitable. Keep quality, latency, throughput, reliability, and cost jointly visible.

### Theoretical question

Lead with the unresolved formal question, current assumption or bound, new result, and changed regime. Do not use empirical motivation as a substitute for theorem significance.

## Contribution diagnostics

- A feature is not a contribution unless it supports a claim.
- A result is not a contribution unless it changes capability or understanding.
- `First`, `novel`, and `unified` require verified scope and close-work comparison.
- Improvement on one benchmark does not by itself establish generality.
- A contribution list should preview where evidence appears.

## Synthetic contrast

Weak gap: `Existing methods have achieved promising results, but there is still room for improvement.`

Repair pattern: `Methods in [verified family] rely on [assumption]. Under [target setting], that assumption causes [specific failure], leaving [capability] unresolved.`

Weak contribution: `We design modules A, B, and C.`

Repair pattern: `We enable [capability] by [technical move]; [artifact] tests the resulting [claim] under [boundary].`

## Final adversarial questions

- Could a close-work author recognize their approach fairly?
- Does the gap logically follow from the review, or appear only after the method is revealed?
- Can every contribution be mapped to evidence?
- Is decisive evidence inside the main-paper boundary?
- Does the final paragraph overstate novelty, scope, or venue relevance?
