# Abstract drafting guide

Provenance: `corpus-derived` for the promoted gap-approach-evidence sequence; all detailed variants below are `conservative-implementation` and examples are `synthetic-example`.

## Pre-draft contract

Recover these fields before writing:

| Field | Question |
|---|---|
| Problem | What concrete task, system, or scientific question is addressed? |
| Setting | Under which data, assumptions, resources, or deployment conditions? |
| Gap | What capability remains unavailable, not merely understudied? |
| Contribution | What one advance answers that gap? |
| Mechanism | Which technical idea plausibly creates the advance? |
| Evidence | Which supplied result most directly tests the central claim? |
| Boundary | What does the evaluation not establish? |

If contribution, evidence, or boundary is absent, use a visible placeholder or request the minimum missing input. Do not hide the absence with generic significance language.

## Select an argument shape

### Challenge-led

Use when the bottleneck is already recognized:

`problem -> concrete challenge -> approach -> decisive evidence -> bounded implication`

### Observation-led

Use when a supplied analysis reveals the design insight:

`problem -> observed failure/pattern -> insight -> method -> evidence -> boundary`

Do not present an exploratory observation as established mechanism.

### Capability-led

Use for systems or resource papers where the new capability is the contribution:

`unmet capability -> why existing operating points fail -> system/resource -> measured capability -> cost/boundary`

### Theory-led

Use when the central result is formal:

`question -> limitation of existing guarantee -> theorem/result under assumptions -> implication -> regime boundary`

State changed assumptions and applicable regimes; do not translate an asymptotic result into an unconditional practical claim.

### Multiple-contribution

Use only when contributions are independently meaningful. Keep one central thesis, then connect each supporting contribution to evidence. Do not turn modules into a list of equal claims.

## Sentence-job audit

Assign every sentence one job: context, gap, contribution, mechanism, evidence, or boundary. Merge repeated jobs; remove implementation detail that does not help identify the contribution. Include a concrete result only when its metric, direction, condition, and comparator are supplied.

## Failure diagnostics

- **Result-free abstract:** asks the reader to trust adjectives rather than evidence.
- **Gap by omission:** claims novelty because citations are absent.
- **Component list:** names modules without the capability they establish.
- **Metric without context:** reports a number without task, comparator, or direction.
- **Scope escalation:** moves from benchmark evidence to universal deployment claims.
- **Mechanism overclaim:** treats correlation, ablation, or attention visualization as causal proof.
- **Conclusion inflation:** ends with broad social or scientific impact not established by the paper.

## Synthetic patterns

Weak: `We propose a novel and comprehensive framework that significantly outperforms existing methods.`

Repair contract: name `[task]`, `[tested setting]`, `[specific bottleneck]`, `[technical move]`, `[supplied metric/result]`, `[matched comparator]`, and `[scope boundary]`.

Theory pattern: `For [problem] under [assumptions], existing guarantees depend on [limitation]. We establish [result] with [bound/regime]. The result implies [bounded consequence], while [excluded regime] remains unresolved.`

Systems pattern: `Existing systems cannot maintain [quality/service target] under [workload/resource condition]. We introduce [system move]. On [supplied workloads and hardware], it achieves [result] at [operating point] relative to [baseline], with [cost/boundary].`

## Final checks

- Central claim matches title, introduction, and conclusion.
- Every result exists in the supplied manuscript.
- Quantifiers and causal verbs match evidence.
- Abbreviations are necessary and defined.
- No citation is added or moved without verification.
- Venue-specific relevance and length constraints are verified rather than guessed.
