# Evidence-calibrated phrase families

Provenance: `conservative-implementation`. These are compositional patterns, not corpus-frequency claims or wording to copy mechanically.

## Select verbs by evidence relation

| Relation | Prefer | Avoid unless established |
|---|---|---|
| Direct observation | `shows`, `reports`, `obtains`, `is higher/lower` | `proves`, `guarantees` |
| Multiple supporting tests | `supports`, `provides evidence for` | `fully validates` |
| Indirect or incomplete evidence | `suggests`, `indicates`, `is consistent with` | `demonstrates mechanism` |
| Formal result | `establishes`, `proves`, `bounds` with assumptions | unconditional practical claims |
| Causal identification | `causes`, `leads to` only under a valid design | causal verbs from correlation or ablation |
| Capability | `enables`, `permits`, `supports` under stated conditions | `solves`, `eliminates` |

Retain the author's intended strength when evidence supports it; do not weaken every claim by default.

## Contrast

State the dimension of contrast:

- assumption: `[Approach A] requires [information], whereas [approach B] operates with [information].`
- operating point: `At matched [quality/resource], [method] uses [supplied cost].`
- scope: `The improvement appears under [setting] but not under [excluded setting].`
- mechanism: `Unlike [verified operation], the proposed module [actual distinction].`

Do not use `unlike previous methods` without naming a verified family and distinction.

## Addition and progression

Use addition only for parallel evidence. Use progression when the second sentence changes the argument:

- parallel: `In addition, [second independent result].`
- consequence: `Consequently, [supported consequence].`
- condition: `Under [condition], however, [different result].`
- refinement: `More specifically, [narrower statement].`
- boundary: `This interpretation is limited to [scope].`

Replace repeated `Moreover` or `Furthermore` when the real relation is cause, contrast, qualification, or sequence.

## Gap language

Prefer capability gaps:

- `[family] does not provide [capability] when [condition].`
- `It remains unclear whether [claim] holds under [regime].`
- `Existing guarantees depend on [assumption], which excludes [target case].`

Avoid `few studies`, `has not received attention`, or `there is room for improvement` unless a verified literature review supports the statement and the missing capability is explained.

## Comparison with prior work

- `Under the shared [protocol], [supplied result].`
- `The methods differ in [assumption/resource], so the reported values are not directly comparable.`
- `[Prior work] establishes [verified capability]; the present work addresses [different bounded capability].`

Keep attribution symmetric: describe both prior and current work at comparable technical resolution.

## Limitation and uncertainty

- evidence boundary: `The evaluation does not establish [excluded claim].`
- data boundary: `The result is limited to [population/dataset/period].`
- assumption boundary: `The guarantee requires [assumption].`
- mechanism uncertainty: `[Observation] is consistent with [explanation], although [alternative] remains possible.`
- deployment boundary: `Performance under [unobserved condition] remains untested.`

Do not use limitations as generic apologies; tie each one to a claim.

## Implication

- scientific: `These results refine [understanding] by showing [bounded change].`
- methodological: `The analysis identifies [design requirement] for [setting].`
- practical: `Under [tested conditions], the method may support [specific use].`

Avoid broad social or field-level impact unless the supplied evidence connects directly to it.

## Future work

Use only when it follows from a demonstrated boundary: `Evaluating [specific untested condition] would determine whether [bounded claim] generalizes.` Do not append a generic list of additional datasets, modalities, or applications.
