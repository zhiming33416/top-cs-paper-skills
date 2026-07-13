# CS subdomain audit gates

Provenance: `conservative-implementation`. Load only gates triggered by visible claims; these are not corpus-frequency claims or universal checklists.

## Deep learning empirical work

- Confirm the experimental unit, data split, preprocessing, model selection, tuning budget, seeds, run count, and uncertainty.
- Check whether baseline implementations and compute budgets are comparable.
- Tie architecture claims to ablations and generalization claims to appropriate shifts or datasets.
- Inspect checkpoint selection, test-set reuse, hyperparameter search leakage, and reporting of failed runs.
- Separate scale benefit from method benefit when parameter count, data, or pretraining differs.

## Foundation, language, and generative models

- Record model versions, prompts/templates, decoding, sampling, tool access, context limits, and evaluation dates.
- Check contamination, benchmark memorization, judge-model dependence, prompt sensitivity, and stochastic variance.
- Require human-evaluation protocol, annotator qualifications, blinding, agreement, and adjudication when human judgments support claims.
- Separate model capability, pipeline/tool capability, retrieval quality, and evaluation-model preference.
- Audit safety and data-governance claims against visible evidence rather than demos.

## Graph learning, recommendation, search, and Web data

- Check temporal and entity leakage, transductive versus inductive setting, negative sampling, candidate generation, and exposure bias.
- Verify that splits reflect the claimed deployment chronology and that user/item overlap is disclosed.
- For recommender evaluation, inspect ranking candidate sets, offline-online distinction, popularity effects, and fairness across groups.
- For Web/social data, inspect platform sampling, bot filtering, deleted content, temporal drift, privacy, and terms/license boundaries.
- Do not treat use of a Web graph or platform as sufficient WWW relevance.

## Systems and efficiency

- Define service-level target, workload distribution, hardware, software stack, precision, batching, concurrency, warm-up, and measurement boundary.
- Compare at equivalent quality, reliability, and operating points.
- Separate preprocessing, training, inference, communication, storage, and external-service cost.
- Inspect scaling curves, bottlenecks, tail latency, failure recovery, resource saturation, and variance.
- A microbenchmark supports a component claim, not automatically the end-to-end system claim.

## Theory and optimization

- Audit quantifiers, definitions, assumption necessity, theorem scope, proof dependencies, edge regimes, and comparison under equal assumptions.
- Check whether constants or lower-order terms make an asymptotic result vacuous in the claimed regime.
- Distinguish convergence to a stationary point, global optimum, approximation guarantee, and empirical stability.
- Verify oracle access, stochastic assumptions, smoothness, convexity, and data/model dependence.
- Experiments may illustrate but cannot repair an invalid proof.

## Dataset and benchmark work

- Check provenance, consent/license, inclusion/exclusion, deduplication, annotation, agreement, adjudication, subgroup coverage, and documentation.
- Audit contamination, train/test entity overlap, temporal leakage, metric construct validity, benchmark saturation, and hidden test governance.
- Ask whether representative model families reveal the intended capability and whether rankings are stable under metric choices.
- Require maintenance, versioning, access, privacy, misuse, and deprecation plans when central to reuse claims.

## Robustness, privacy, and security

- State the threat model, adversary knowledge, budget, access, adaptive capability, and success criterion.
- Check whether attacks and defenses use matched information and whether evaluation includes adaptive or transfer settings appropriate to the claim.
- Distinguish empirical attack failure from a security guarantee.
- For privacy, identify the protected unit, adjacency relation, accounting, composition, utility tradeoff, and implementation assumptions.
- For robustness, define perturbation set, distribution shift, certified versus empirical guarantee, and clean-performance tradeoff.

## Causal and statistical claims

- Identify estimand, treatment/exposure, outcome, intervention or observational design, confounders, selection, and identification assumptions.
- Check whether prediction, association, mediation, and causation are distinguished.
- Inspect multiple testing, post-selection inference, missing data, clustering, repeated measures, and uncertainty unit.
- An ablation or representation visualization does not identify causality without a valid design.

## Gate-to-issue rule

For every triggered gate, cite the visible claim and artifact. If the required information may be outside the supplied scope, ask a confidence-calibrated question. Do not output the entire gate list.
