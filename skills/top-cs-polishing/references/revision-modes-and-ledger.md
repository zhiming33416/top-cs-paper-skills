# Revision modes and ledger

- `light-edit`: preserve sentence order and argument structure; change grammar, concision, and local clarity only.
- `structural-revision`: reorder claims and evidence, split or merge paragraphs, and expose missing premises.
- `compression`: preserve every supported claim, number, citation relation, and boundary while reducing redundancy.
- `zh-to-en`: recover intent and logical relations before producing English; maintain a terminology ledger.

For every material change, record `location`, `before claim`, `after claim`, `reason`, `evidence effect`, and `verification status`. Mark LaTeX as `structurally-checked`, `compiled`, or `not-compiled`; never imply successful compilation without running it.
