# Method drafting guide

Provenance: section-placement flexibility is partly `corpus-derived`; this detailed execution guide is `conservative-implementation`.

## Pre-writing questions

- What are the inputs, outputs, task, objective, and evaluation unit?
- Which assumptions are required for correctness or tractability?
- What information is available during training, inference, and evaluation?
- Which module or step addresses each identified bottleneck?
- What must a reader implement to reproduce the method?
- Which claimed benefits are formal consequences, and which require experiments?

## Recommended reasoning order

1. Problem contract and notation.
2. Assumptions and scope.
3. End-to-end overview.
4. Components or algorithmic stages.
5. Objective, optimization, or proof-relevant construction.
6. Training/inference differences or execution procedure.
7. Complexity, resource use, and implementation-critical detail.

Do not force these into identical headings. The 90-paper corpus supports placement flexibility, not a universal outline.

## Problem contract

Define entities before symbols. State shapes, domains, randomness, observed versus latent variables, and target outputs. Separate task definition from the authors' solution. Record unavailable information explicitly so a baseline cannot silently receive a different problem.

## Overview

Give the reader a map from input to output and name the job of each component. Align names with the terminology ledger and figure labels. State dependencies and data flow before local equations.

## Component contract

For every component, write:

| Element | Required content |
|---|---|
| Motivation | Specific bottleneck or requirement addressed. |
| Input/output | Data, dimensions, symbols, and interface. |
| Operation | Transformation, algorithm, or decision rule. |
| Interaction | Information exchanged with other components. |
| Objective | Loss, constraint, theorem role, or system requirement. |
| Expected effect | Testable claim, not an asserted result. |
| Cost/boundary | Complexity, resources, assumptions, or failure regime. |

## Equations and algorithms

Introduce each equation with its purpose and follow it with interpretation. Define every symbol at first use. Distinguish mathematical equality, approximation, estimator, and optimization objective. For pseudocode, specify inputs, outputs, termination, state mutation, randomness, and complexity-sensitive operations.

## Learning methods

Separate architecture, objective, optimization, data processing, selection, and inference. State which model/checkpoint is reported, how hyperparameters are selected, and whether inference uses information unavailable to baselines.

## Systems methods

Connect requirements to architecture decisions. State deployment topology, concurrency model, caching, batching, consistency, failure recovery, and measurement boundary when they support claims. Do not present implementation convenience as a principled design choice without analysis.

## Theoretical methods

State definitions, assumptions, theorem, proof idea, and full proof boundary separately. Make changed assumptions visible when comparing bounds. Do not call an empirical pattern a theorem premise unless formalized.

## Dataset and benchmark methods

Describe collection, inclusion/exclusion, provenance, license, annotation, adjudication, splits, contamination controls, metrics, and maintenance. Keep normative dataset design decisions distinct from measured properties.

## Failure diagnostics

- Symbols precede concepts.
- Overview repeats the abstract without enabling navigation.
- Modules are motivated by their own existence.
- Claimed advantages appear before formal or empirical support.
- Training and inference information differ silently.
- Implementation detail is omitted for a central result but expanded for inconsequential components.
- Complexity ignores the dominating operation or realistic regime.

## Synthetic module pattern

`[Bottleneck] prevents [required capability]. Given [input], [module] computes [operation] to produce [output]. It interacts with [component] through [interface]. We optimize [objective] under [assumption]. This design is expected to affect [claim], tested by [planned/supplied artifact], and costs [complexity/resource boundary].`

Never fill the placeholders with invented facts.
