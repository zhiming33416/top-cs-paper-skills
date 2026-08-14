# Synthetic Paper Handoff Example

[中文首页](../../README.md) · [English home](../../README_EN.md) · [完整工作流](../../docs/WORKFLOW.md)

This directory is a fully synthetic, redistributable tutorial for the optional full-paper workflow. It contains no manuscript text, dataset, PDF, reviewer correspondence, experiment result, or venue policy. The identifiers show how six specialist skills can hand work to one another without turning a status manifest into evidence.

| File | Handoff purpose |
| --- | --- |
| [project-brief.md](project-brief.md) | Scope, claimed contribution, and target stage. |
| [claims-evidence.yaml](claims-evidence.yaml) | Claim and evidence identifiers with explicit pending states. |
| [figure-brief.md](figure-brief.md) | A figure contract connected to a claim, not fabricated data. |
| [review-issue.md](review-issue.md) | An author-side review risk and required action. |
| [revision-ledger.md](revision-ledger.md) | A revision record linked to the issue and response. |

## What each skill returns

The `outputs/` directory shows one synthetic output sample per specialist skill, produced from the inputs above. Placeholders and pending states are part of the output format, not gaps to be polished away.

| Skill | Output sample | What it demonstrates |
| --- | --- | --- |
| top-cs-writing | [outputs/writing-claim-outline.md](outputs/writing-claim-outline.md) | claim–evidence outline, paragraph jobs, draft excerpt with placeholders |
| top-cs-evidence | [outputs/evidence-ledger.md](outputs/evidence-ledger.md) | citation metadata ledger and claim-to-source map with `needs-source-text` |
| top-cs-polishing | [outputs/polishing-revision.md](outputs/polishing-revision.md) | before/after paragraph plus a fact-preserving revision ledger |
| top-cs-reviewer | [outputs/reviewer-issue-board.md](outputs/reviewer-issue-board.md) | consequence-based issue board with calibrated confidence |
| top-cs-response | [outputs/response-draft.md](outputs/response-draft.md) | point-by-point reply that promises nothing unverified |
| top-cs-figure | [outputs/figure-handoff.md](outputs/figure-handoff.md) | normalized figure contract and QA record for a conceptual figure |

中文：本目录只展示可追溯的交接格式与各技能的输出样例，不是论文模板、实验结果、审稿意见或会议规则。不要把任何示例 ID 当作真实证据；实际项目必须由作者提供、核验并确认材料。
