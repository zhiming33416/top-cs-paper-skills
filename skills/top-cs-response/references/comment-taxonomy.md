# Comment taxonomy

Provenance: `conservative-implementation`.

## Split compound comments

Create one stable ID per independently answerable requirement. Preserve the full original wording in the letter and link sibling IDs when one numbered reviewer comment contains several asks. Never merge distinct asks merely to shorten the response.

## Severity

- `blocking`: threatens the validity or assessability of the central case, or a verified mandatory instruction.
- `major`: requires substantive evidence, analysis, proof, or claim restructuring.
- `minor`: localized reporting, clarity, citation, or presentation action.
- `question`: answer determines severity or strategy.
- `not-assessable`: supplied material cannot establish whether the issue is resolved.

Severity describes the underlying concern, not reviewer tone.

## Categories

### Editorial and compliance

Required files, declarations, formatting, anonymity, scope, deadlines, length, track fit, or editor-specific instructions. Editor items use `E.*` IDs and precede reviewer items.

### Correctness and theory

Logical error, undefined object, invalid assumption, proof gap, algorithmic correctness, convergence, theorem scope, or mismatch between formal claim and implementation.

### Evidence and interpretation

Missing validation, unsupported generality, causal overclaim, weak mechanism evidence, absent failure analysis, or interpretation exceeding observation.

### Experimental design and comparison

Split construction, leakage, baseline fairness, tuning parity, metric choice, uncertainty, run count, ablation, robustness, efficiency, or operating-point mismatch.

### Statistics

Experimental unit, sample size, test assumptions, multiple comparisons, missing data, effect size, confidence interval, aggregation, post-selection, or causal identification.

### Reproducibility and artifacts

Data/code access, software version, hardware, hyperparameters, preprocessing, implementation detail, license, documentation, or anonymous artifact integrity.

### Novelty and related work

Closest-work distinction, missing verified citation, unfair characterization, changed assumptions, incremental contribution, or unsupported priority claim.

### Scope and limitations

Population, task, dataset, regime, compute, deployment, failure case, external validity, or requested work outside the current study design.

### Presentation

Structure, terminology, notation, figure/table legibility, caption completeness, ambiguity, or writing clarity. Do not downgrade a hidden scientific ambiguity to presentation merely because it can be rewritten.

### Ethics and integrity

Privacy, consent, licensing, bias, misuse, societal impact, data integrity, duplicate publication, attribution, or conflicts with policy. Escalate rather than cosmetically rewrite a real integrity concern.

## Duplicate and conflict links

Record `duplicate-of`, `overlaps-with`, or `conflicts-with`. Draft a shared evidence core but answer each reviewer-specific framing. Editor priority and scientific evidence boundaries override incompatible promises.
