# Corpus-calibrated revision moves

Use these observations to diagnose structure, not to imitate wording. Evidence comes from 90 unique accepted-title-verified public versions: 30 each for ICLR, ICML, and WWW Research. Topic and paper-type labels remain candidates pending human confirmation, so label-dependent style rules are not promoted.

## Abstract revision

Make gap, approach, and evidence recoverable in that order when the source facts support them. This sequence is supported across 11 sources from WWW, ICLR, and ICML (`cross-venue-polishing-abstract-argument-recovery`). Do not force identical opening language or invent a gap.

## Introduction revision

An explicit contribution preview is supported across the three venues (`cross-venue-polishing-contribution-evidence-alignment`). Revise feature lists into contribution–evidence pairs. Preserve uncertainty and do not label implementation components as independent scientific contributions without evidence.

## Related-work revision

- ICML: the expanded sample favors a dedicated section (25/30), but this is not official policy (`icml2026-polishing-related-work-placement`).
- ICLR: related work was detected in 26/30 after combining text headings and PDF outlines, while integrated placement still occurs across Oral and Poster samples (`iclr2026-related-work-placement-flexible`).
- WWW Research: related work was detected in 23/30 (`www2026-polishing-related-work-placement`); use the observation for structure diagnosis, not as a required heading.

## Claim and diction boundary

The corpus does not justify a venue phrasebank or universal verb-frequency rule. Continue to calibrate `demonstrates`, `shows`, `supports`, `suggests`, and `is consistent with` from evidence strength, not observed frequency. Never copy distinctive source phrasing.

## Length boundary

Extracted abstract medians are descriptive only (approximately 219 words ICLR, 179 ICML, 314 WWW Research). Public-version extraction and version differences make them unsuitable as target word limits; use current official forms and templates for constraints.

Full source IDs are recorded in `evidence/derived/rules.yaml` in the source repository and `_shared/evidence/derived/rules.yaml` after installation.
