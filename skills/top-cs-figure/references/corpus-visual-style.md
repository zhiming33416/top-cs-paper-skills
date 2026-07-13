# Corpus-Derived Visual Style

Load this when venue-specific figure style, palette choice, or visual evidence confidence matters.

## Evidence files

- `../../evidence/derived/visual-style-source-manifest.yaml`: public source provenance, hashes, verification status, and external relative paths.
- `../../evidence/derived/visual-style-index.yaml`: aggregate per-source records.
- `../../evidence/derived/visual-style-stats.json`: venue aggregates.
- `../../evidence/derived/visual-style-rules.yaml`: independent `style_status`, `anchor_status`, and `profile_status` guidance.

These files contain only hashes, counts, color clusters, layout labels, and confidence. They do not contain page images, figure crops, source data, captions, or paper text.

## Use rules

- `promoted` plus `profile_status: usable`: may guide venue-calibrated profiles, still not official policy.
- `promoted` plus `anchor_status: usable` but `profile_status: insufficient`: keep generic semantic roles and report `anchors-usable-profile-unstable`.
- `promoted` plus `anchor_status: insufficient`: keep generic semantic roles and report `promoted-no-usable-palette`.
- `preliminary`: may guide conservative defaults with a confidence note.
- `external-corpus-required`: do not claim venue-specific style; use generic style and report the gap.

Current derived snapshot (2026-07-13; always re-read the rules file):

- WWW Research: 30 independent eligible sources, `style_status: promoted`, `anchor_status: usable`, `profile_status: usable`.
- ICLR: 30 independent eligible sources, `style_status: promoted`, `anchor_status: usable`, `profile_status: usable`.
- ICML: 30 independent eligible sources, `style_status: promoted`, `anchor_status: usable`, `profile_status: usable`.

Documentation must not hard-code these states as future expectations. Routing, acceptance, rendering, and audit behavior read `visual-style-rules.yaml` at execution time.

## Source acquisition provenance

Use `visual-style-source-manifest.yaml` when judging whether venue style evidence is enough to use. It records only public source metadata, SHA-256 hashes, download/verification status, and relative external PDF paths under the corpus root. It must not contain abstracts, captions, paper body text, figure crops, page images, or experiment tables.

For 2026 corpus expansion, target 30 verified main-track public PDFs per venue. Promote venue defaults only from rows with `eligibility: style-evidence` and successfully extracted visual records. Treat `holdout`, `download-error`, `duplicate-of:*`, and title/venue mismatch rows as provenance gaps, not style evidence.

The collector uses official 2026 accepted indexes first: OpenReview API2 with legacy OpenReview fallback for ICLR, and ICML Virtual accepted-paper JSON before PMLR fallback for ICML. When OpenReview challenge protection blocks both APIs, an external `--candidate-seed` may contain only titles visibly labeled Poster/Oral on the official public submissions pages; the seed is title-index provenance, not fulltext evidence. ICML Virtual records remain accepted-title candidates even when `paper_pdf_url` is empty. A public arXiv preprint is accepted only through exact title matching, hash verification, and first-page title/venue verification. Resolver cache failures expire and are retried; valid cache hits do not consume the network-query budget.

Palette candidates are extracted only from bounded regions adjacent to Figure captions. Text/link colors, page chrome, and neutral colors are excluded. Nearby export colors are clustered into circular hue families, each paper contributes independent family coverage, candidates require white-background contrast, and selected families are separated by at least 36 degrees. A family needs `max(3, ceil(25% of eligible sources))` support, which is eight independent papers in the current 30-paper venue corpora. A corpus anchor set needs three such families; one frequent paper or one exact RGB value cannot replace generic semantic roles.

Schema v3 also stores aggregate-only per-region palette signatures: dominant hue families, sampled color share, light/mid/dark background, drawing/image counts, and a coarse visual context. It stores no pixels or text. Profile promotion uses independent-paper color-family co-occurrence, deterministic paper bootstrap retention, and leave-one-paper-out stability. `palette_status` remains compatible with anchor availability; `profile_status` is the runtime gate.

Current profile stability uses 24 WWW, 22 ICLR, and 24 ICML independent sources with usable figure-local signatures. Bootstrap retention is 0.855, 0.782, and 0.750 respectively; all exceed the 0.60 profile threshold. Recompute these values from the live rules rather than treating this paragraph as permanent evidence.

## WWW public fulltext gap

WWW Research source discovery starts from the official accepted Research list. Count a WWW paper as style evidence only when a title-exact public fulltext PDF is found outside restricted ACM DL access. Do not use Companion, Short, Industry, Web4Good, or ACM-restricted PDFs to fill WWW Research style gaps.

Never describe a palette or layout as improving acceptance probability.
