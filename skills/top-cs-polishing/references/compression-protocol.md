# Evidence-preserving compression

Provenance: `conservative-implementation`.

## Establish immutable content

Before deleting text, record:

- every number, unit, sign, uncertainty, and comparison direction;
- claim conditions, quantifiers, negation, and causal strength;
- citation-to-claim relations;
- equation, figure, table, section, and appendix references;
- terminology definitions and abbreviation first uses;
- negative results and boundaries that qualify the main claim.

## Compress in this order

1. Delete duplicated motivation, repeated contribution summaries, and empty metadiscourse.
2. Replace generic transitions with the actual logical relation or remove them.
3. Merge sentences that repeat one claim and share evidence.
4. Replace wordy nominal or passive constructions when agency and meaning remain stable.
5. Move low-priority implementation detail to an allowed location only when venue policy and self-containment permit it.
6. Shorten examples or enumerations after preserving representative coverage.
7. Narrow claims rather than deleting necessary caveats.

Never begin by removing limitations, uncertainty, comparator conditions, or negative evidence.

## Information ledger

| Source item | Location before | Location after | Preserved form | Status |
|---|---|---|---|---|

Use `preserved`, `rephrased`, `moved`, `removed-duplicate`, or `author-decision-needed`. A citation moved to another sentence requires alignment verification.

## Compression diagnostics

- A shorter paragraph now implies causality that the source hedged.
- A metric remains but its comparator or direction disappeared.
- The first abbreviation use was removed.
- A caveat moved to optional material while the claim stayed in the main text.
- Two distinct claims were merged under one evidence statement.
- A figure/table reference became ambiguous.

## Verification

Diff source and revision for numbers, citations, labels, references, terminology, negation, and modal verbs. For LaTeX, run the structural checker and compile when available. Report the achieved reduction only after the preservation audit.
