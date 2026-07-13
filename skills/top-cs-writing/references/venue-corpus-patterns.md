# Venue writing patterns from the verified public-version corpus

Evidence snapshot: 90 unique primary sources (ICLR 30, ICML 30, WWW Research 30) within 99 unique public PDFs. All are accepted-title-verified public/preprint versions, not guaranteed camera-ready files. Use official guides for format, page, anonymity, and required-section rules. Topic and paper-type labels cover the planned diversity targets but remain assistant-reviewed candidates pending human confirmation; do not promote label-dependent rules yet.

## Cross-venue patterns

- **Abstract argument chain:** a gap → approach → evidence sequence recurs across 11 sources from all three venues. Use the sequence to make reasoning recoverable, not as a sentence template. Evidence: `cross-venue-abstract-argument-chain`.
- **Contribution preview:** explicit introduction contribution blocks recur across all three venues. Tie each contribution to visible evidence rather than listing modules. Evidence: `cross-venue-introduction-contribution-preview`.
- Do not infer that a heading, phrase, or acceptance tier caused acceptance.

## ICLR 2026 sample

- Introduction was detected in 30/30 unique sources and experiments/evaluation in 28/30.
- Related work was detected in 26/30 after combining text headings and PDF outlines; integrated placement still occurs across Oral and Poster samples. Choose placement by argument flow. Evidence: `iclr2026-related-work-placement-flexible`.
- Keep decisive evidence in the main paper because appendix reading is optional. Official evidence: `official-iclr2026-main-paper-boundary`.

## ICML 2026 sample

- Introduction appeared in 30/30, related work in 25/30, and experiments/evaluation in 21/30 unique sources.
- A dedicated related-work section is a strong sample convention, not an official requirement. Evidence: `icml2026-related-work-explicit-section`.
- Keep soundness, significance, and originality claims separable so each can be audited against evidence.

## WWW 2026 Research sample

- Thirty verified Research sources are eligible; Industry, Short, and Web4Good files remain indexed but excluded from Research style promotion.
- Related work was detected in 23/30 and experiments/evaluation in 24/30. These are structural observations, not required headings. Evidence: `www2026-research-related-work-prevalent`.
- The earlier semantic contribution/evidence rule remains supported by only three manually reviewed sources and therefore stays low confidence; the expanded corpus is not treated as semantic confirmation without human review. Evidence: `www2026-research-explicit-contribution-evidence`.
- State Web and selected-track relevance on the first page. This is official policy, not a corpus convention. Evidence: `official-www2026-first-page-relevance`.

Full source IDs and promotion thresholds are recorded in `evidence/derived/rules.yaml` in the source repository and `_shared/evidence/derived/rules.yaml` after installation.
