# Paper-type audit packs

Use the primary contribution type to prioritize checks. Convert an omission into a major issue only after explaining which central claim it threatens.

## Empirical

- Identify the unit of observation, sampling frame, exclusions, split construction, and leakage controls.
- Check whether baselines receive comparable information, preprocessing, tuning budget, compute, and stopping criteria.
- Match every effectiveness claim to metrics, aggregation, uncertainty, number of runs, and statistical unit where relevant.
- Require ablations for component claims, robustness tests for scope claims, and failure analysis for deployment claims.
- Distinguish statistical significance, practical importance, and cherry-picked best-case results.

## Algorithmic

- Recover the formal input, output, objective, constraints, and changed assumptions.
- Check algorithm correctness, convergence or termination conditions, complexity, memory, and regimes where costs dominate.
- Compare under matched compute, oracle access, data, and implementation effort.
- Require sensitivity or stability evidence for consequential hyperparameters.
- Do not accept performance gains as evidence for a claimed algorithmic property without a direct test or proof.

## Theoretical

- Audit definitions, quantifiers, assumption necessity, theorem statement, and proof dependencies separately.
- Check whether the claimed improvement holds under equal assumptions and in a meaningful parameter regime.
- Look for hidden regularity, asymptotic-only gains, vacuous bounds, circular lemmas, and unhandled edge cases.
- Separate proof completeness from exposition quality; a plausible intuition is not a proof.
- Verify that experiments illustrate rather than substitute for the theorem.

## Systems

- Map requirements to architecture decisions and each design claim to an end-to-end measurement.
- Check workload representativeness, deployment conditions, warm-up, concurrency, hardware, software versions, and operating points.
- Compare latency, throughput, quality, reliability, and resource cost under equivalent service constraints.
- Require bottleneck analysis, failure recovery, scaling behavior, and sensitivity to workload shifts.
- Flag microbenchmarks that do not establish the system-level claim.

## Dataset and benchmark

- Audit provenance, consent, license, collection process, exclusions, coverage, documentation, and intended use.
- Check annotation protocol, annotator population, agreement, adjudication, uncertainty, and subgroup quality.
- Inspect train/test contamination, duplicate entities, temporal leakage, benchmark saturation, and metric validity.
- Ask whether representative model families and baselines reveal what the benchmark measures.
- Require maintenance, versioning, access, misuse, privacy, and deprecation plans where relevant.

For hybrid papers, apply a secondary pack only to claims that depend on it. Do not turn the report into an unprioritized checklist.
