# Experiments drafting guide

Provenance: experiment-section prevalence and research-question organization are supported at a structural level by the corpus; detailed audit fields are `conservative-implementation`.

## Build a claim-to-test matrix

| Claim ID | Claim | Required comparison | Metric/evidence | Protocol controls | Boundary/failure | Status |
|---|---|---|---|---|---|---|

Every title, abstract, and contribution claim needs either a direct test, a formal result, or an explicit narrowing. Do not create experiments merely to fill conventional subsections.

This skill organizes supplied experimental evidence for writing. It does not execute code, start jobs, monitor training, or convert planned work into results.

## Section architecture

1. Research questions and common setup.
2. Main effectiveness or correctness evidence.
3. Component or causal-design analysis.
4. Robustness, sensitivity, or regime analysis.
5. Efficiency and resource evidence when claimed.
6. Failure cases, negative results, and limitations.

Order by decision importance, not table number.

## Baseline fairness

Record for every comparator: task definition, data, preprocessing, information access, tuning budget, compute, stopping rule, checkpoint selection, and evaluation code. Explain unavoidable mismatches rather than hiding them. A recent baseline is not automatically strong; a strong baseline must test the relevant alternative explanation.

## Metrics and uncertainty

Define metric direction, aggregation unit, macro/micro averaging, threshold selection, repeated-run unit, uncertainty interval, and statistical test when relevant. Preserve effect magnitude separately from significance. Do not invent run counts, standard deviations, or p-values.

## Ablations

Tie each ablation to one component claim. Removing a component tests necessity only under the resulting system and optimization; it does not by itself prove mechanism. For interacting components, consider factorial or conditional comparisons when supplied resources allow.

## Robustness and scope

Select tests from the claimed boundary: datasets, tasks, populations, distribution shifts, noise, hyperparameters, seeds, model sizes, hardware, workloads, or adversarial conditions. Do not demand every robustness test; require the one needed by the wording of the claim.

## Efficiency and systems evidence

Report quality with latency/throughput, hardware, precision, batch size, concurrency, memory, warm-up, and measurement boundary. Compare at equivalent operating points. Separate training cost, inference cost, amortized preprocessing, and external-service cost.

## Qualitative evidence

Define selection criteria and include representative failures. A visualization can explain behavior but rarely establishes generality alone. Keep captions self-contained: question, setting, encoding, and main observation.

## Table and figure contract

- One artifact, one reasoning job.
- Caption states protocol and notation, not unsupported interpretation.
- Metric direction and units are visible.
- Precision is consistent and no visual emphasis contradicts the text.
- Best/second-best highlighting is defined and handles ties.
- Main-paper artifacts contain decision-critical evidence; appendix artifacts provide depth.

## Result paragraph pattern

`To test [claim/question], we compare [methods] under [matched protocol] using [metric]. [Supplied result]. This evidence [supports/partially supports/does not support] [bounded claim]. [Failure, alternative, or scope limit].`

Before prose, maintain a compact experiment-to-writeup bridge: claim ID, research question, supplied artifact path or table/figure ID, protocol facts, result status, allowed interpretation, and unresolved input. Use `planned` or `[RESULT NEEDED]` when evidence is absent.

## Failure diagnostics

- Results follow table order without research questions.
- Baselines receive unequal information or tuning.
- Best-case numbers replace aggregate evidence.
- Ablations are presented as mechanism proof.
- Efficiency claims omit operating point or hardware.
- Negative evidence disappears from discussion.
- Conclusions generalize beyond tasks, datasets, or regimes tested.

## Final reproducibility pass

Check data/splits, code path, versions, seeds, run count, hyperparameter search, model selection, metrics, hardware, resource cost, and anonymous artifact instructions. Report missing items by the claim they threaten.
