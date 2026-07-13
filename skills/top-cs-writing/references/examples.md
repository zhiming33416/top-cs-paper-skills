# Structural examples

Use these as reasoning patterns, never as wording templates. Replace every bracketed field with supplied evidence or an explicit missing-input marker.

## Abstract

`[consequential problem] -> [specific unresolved gap] -> [approach] -> [principal result with condition/comparator] -> [bounded implication]`

Weak: `We propose a novel framework that achieves superior performance.`

Diagnose: no task boundary, comparator, metric, or evidence. Do not repair it by inventing numbers.

Grounded pattern: `We study [task] under [setting], where [specific limitation]. We introduce [approach]. On [supplied evaluation], it [supplied result] relative to [comparator], suggesting [bounded implication].`

## Introduction contribution

Use one contribution-evidence pair per bullet: capability, mechanism, direct evidence, and boundary. Avoid component inventories such as `we propose A, B, and C` when the manuscript does not explain the claim each component supports.

## Method module

`motivation -> input/output contract -> operation -> interaction -> objective or complexity -> testable expectation`

Keep empirical benefits as expectations until the experiment section supplies evidence.

## Experiment paragraph

`question -> protocol -> fair comparator -> metric and direction -> supplied result -> interpretation -> boundary or failure`

If a result, run count, uncertainty estimate, or tuning budget is absent, insert `[DETAIL NEEDED]` rather than completing the sentence speculatively.

## Discussion paragraph

`supported finding -> change relative to prior expectation -> plausible explanation -> alternative explanation -> scope boundary`

Use causal language only when the design identifies causality. Preserve null and mixed results when they qualify the central claim.
