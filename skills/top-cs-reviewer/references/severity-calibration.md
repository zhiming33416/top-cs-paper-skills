# Severity and confidence calibration

Provenance: `conservative-implementation`; examples are `synthetic-example`.

## Consequence test

Before assigning severity, complete: `If unresolved, this issue causes [specific consequence] for [claim or policy].` If that sentence cannot be made concrete, classify it as a question, preference, or minor presentation issue.

## Blocking

Use when a central claim is invalid, uninterpretable, contradicted, or prevented from assessment; or when a verified desk-reject/compliance rule is violated.

Examples:

- Test leakage directly determines the reported benchmark advantage.
- A theorem conclusion does not follow under its stated assumptions.
- The only evaluation uses information unavailable in the defined task.
- A verified anonymity violation exposes author identity before review.

Do not use `blocking` for every missing ablation or desired dataset.

## Major

Use when the central case remains plausible but materially under-supported or ambiguously scoped and needs substantive analysis, experiment, proof, or restructuring.

Examples:

- An efficiency claim lacks hardware and operating-point information.
- A component is presented as the source of gains without a test separating alternatives.
- A dataset paper does not document annotation quality for the target labels.
- The closest-work comparison changes assumptions without disclosure.

## Minor

Use when the issue is localized and a text, reporting, or presentation fix resolves it without changing the main evidence.

Examples: undefined notation recoverable from context, missing unit in one caption, inconsistent abbreviation, or a claim whose boundary is established elsewhere but not repeated locally.

## Question

Use when the answer could change severity or interpretation and the supplied artifact does not resolve it. Phrase the question around the decision: `Is X measured under Y? If not, claim Z would require narrowing.`

## Not assessable

Use when relevant material was not supplied or lies outside the requested scope. Do not convert `not assessable` into a defect.

## Confidence

- `high`: direct manuscript evidence and stable anchor.
- `medium`: consequence is clear but an ambiguity or missing local artifact remains.
- `low`: concern depends on inferred intent, unavailable material, or domain expertise not established by the packet.

Severity and confidence are independent. A potentially blocking issue may have low confidence and should be framed as a decision-critical question.

## Preference filter

Do not elevate preferred notation, section order, writing voice, favorite baseline, or research direction unless it changes correctness, evidence, reproducibility, reader access, or verified venue compliance.
