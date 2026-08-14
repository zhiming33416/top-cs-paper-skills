# Top CS Paper Skills

[English](README_EN.md) · [安装](INSTALL.md) · [完整工作流](docs/WORKFLOW.md) · [质量说明](docs/QUALITY.md) · [宿主兼容](docs/HOSTS.md) · [文档导航](docs/README.md)

[![CI](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![专项技能](https://img.shields.io/badge/专项技能-6-6f42c1)
![宿主](https://img.shields.io/badge/宿主-Codex%20%2B%20Claude%20Code-3776AB)

![Top CS Paper Skills：面向顶级计算机科学会议的证据驱动 skills](assets/top-cs-paper-skills-banner.png)

> 把你手里的研究材料，变成可追溯的顶会投稿产物——写作、文献证据、图件、润色、预审、审稿回复，全程不编造实验、引用或会议规则。

给 Codex 和 Claude Code 安装六个专项技能，覆盖从"一堆实验笔记"到"点对点审稿回复"的完整论文生命周期。当前官方 profile 覆盖 WWW、ICLR、ICML、NeurIPS、CVPR、ACL 2026。

## 30 秒看效果

所有示例均为合成材料，占位符是输出格式的一部分——缺失的证据被显式标记，而不是被流畅文字掩盖。

<details>
<summary><b>润色前后对比</b>（事实、引用锚点、数字全部保留）</summary>

**修改前：**

> It is generally the case that, in many situations, evaluation reports might potentially conflate things that have actually been measured with things that are merely planned to be measured at some point, which is a problem that could possibly be addressed by having some kind of explicit separation between different states of evidence [syn2026provenance], as illustrated conceptually in the workflow shown in FIG-001.

**修改后：**

> Evaluation reports often conflate measured results with planned measurements. Separating evidence into explicit states — measured, pending, and author-decided — makes this distinction auditable [syn2026provenance], as illustrated in the conceptual workflow of FIG-001.

附带修订账本：每处修改标注类型与事实影响，引用与图件锚点逐一核对。完整样例见 [polishing-revision.md](examples/synthetic-paper/outputs/polishing-revision.md)。

</details>

<details>
<summary><b>审稿回复草稿</b>（不承诺未验证的修改，不虚构实验）</summary>

> We thank the reviewer for identifying this ambiguity. Figure `FIG-001` is a conceptual workflow illustration, not an empirical result. We have updated the caption and the surrounding prose in Section [X] to state "conceptual workflow; no empirical result shown" (revision `REV-001`, status: `pending-author-confirmation`). We do not claim any measured outcome for this figure.

回复明确列出"这个回复刻意不做什么"：不承诺新实验、不宣称修订已完成。完整样例见 [response-draft.md](examples/synthetic-paper/outputs/response-draft.md)。

</details>

<details>
<summary><b>引言大纲 + claim–evidence 边界表</b>（缺失的引用保持为显式占位符）</summary>

| Claim | Evidence | Status | Boundary |
| --- | --- | --- | --- |
| `CLM-001` 证据状态分离 | `EVD-001` 计划中的评估记录 | `pending-author-input` | 工作流主张，不是性能结果 |

段落职责大纲逐段标注 `[CITATION NEEDED: ...]`，草稿摘录保留 `PENDING-AUTHOR-INPUT` 状态。完整样例见 [writing-claim-outline.md](examples/synthetic-paper/outputs/writing-claim-outline.md)。

</details>

六个技能的完整输入 → 输出样例（含证据账本、预审问题板、图件契约）在 [examples/synthetic-paper](examples/synthetic-paper/README.md)。

## 10 分钟开始

```bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python scripts/install_skills.py --host codex     # 或 --host claude
python scripts/install_skills.py --host codex --check
```

从你已经掌握的材料开始：

```text
使用 $top-cs-writing，基于这些结果为 ICLR 引言建立 claim–evidence 大纲。
使用 $top-cs-evidence，把这些贡献主张映射到我提供的 BibTeX 和来源笔记。
使用 $top-cs-figure，基于这份 CSV 和 figure brief 制作可编辑的消融实验图。
```

只有完整、跨阶段论文项目才安装 `--workflow`。Claude Code、按技能安装、更新与安全 `--prune` 见 [INSTALL.md](INSTALL.md)。

## 选择技能

| 你的问题 | 专项技能 | 你提供 | 你得到 | 内置检查 |
| --- | --- | --- | --- | --- |
| 把结果和想法组织成论文论证 | [writing](skills/top-cs-writing/README.md) | 贡献、结果、章节、会议 | claim map、大纲、初稿、缺口 | claim–evidence 边界 |
| 定位工作并核验已有文献 | [evidence](skills/top-cs-evidence/README.md) | claim、BibTeX/DOI、可选摘录 | 来源计划、元数据账本、claim map | 元数据不等于蕴含 |
| 忠实修改英文、中文或 LaTeX | [polishing](skills/top-cs-polishing/README.md) | 原文/LaTeX 与约束 | 修订稿和 ledger | 事实与 LaTeX 保留 |
| 投稿前找出实质风险 | [reviewer](skills/top-cs-reviewer/README.md) | 稿件、图件、附录、会议 | 优先级作者侧审计 | claim、实验、匿名性审计 |
| 真实回应审稿意见 | [response](skills/top-cs-response/README.md) | 评审、证据、修订状态 | 问题板、回复、修订账本 | 不虚构实验或承诺 |
| 制作并审计论文图 | [figure](skills/top-cs-figure/README.md) | CSV、figure brief、render spec | SVG/PDF/PNG 和 QA | 数据/spec/provenance 检查 |

`top-cs-paper-workflow` 是可选协调器，不是第七个专项技能；在需要恢复项目状态时覆盖下列链路：

```text
贡献与主张 → 来源与证据 → 图件 → 写作与修订 → 投稿前预审 → 审稿回复
top-cs-writing  top-cs-evidence  top-cs-figure  top-cs-polishing  top-cs-reviewer  top-cs-response
                              └──── top-cs-paper-workflow（可选）────┘
```

## 为什么不直接用裸提示？

通用 LLM 会话在论文场景下的三个系统性风险，恰好是这套技能的设计核心：

| 裸提示的风险 | 这套技能的做法 |
| --- | --- |
| 编造引用、把书目匹配当成来源支持 | 引用元数据核验与 claim 蕴含是两个独立状态；无作者摘录时强制 `needs-source-text` |
| 凭记忆复述过期的会议规则 | venue 政策来自带日期与哈希快照的官方来源，profile 随届次过期并自动回退 `generic` |
| 用流畅文字掩盖缺失的实验与证据 | 占位符（`[CITATION NEEDED]`、`PENDING-AUTHOR-INPUT`）是输出契约的一部分，由确定性检查保证保留 |

## 为什么可信

| 原则 | 在仓库中的实际含义 |
| --- | --- |
| 证据谱系 | claim、图件、引用、审稿问题与修订都有稳定 ID 和显式缺口；书目信息匹配绝不被表述为来源支持。 |
| 保守表达 | 缺失的结果、来源摘录、会议规则与作者决定保留为占位符，而不是被流畅文字掩盖。 |
| 可复现检查 | 图件使用可编辑 Python 渲染包和 QA；LaTeX、引用元数据、工作流交接和安装都有确定性检查。 |

当前官方 profile 覆盖 WWW、ICLR、ICML、NeurIPS、CVPR、ACL 2026。profile 随届次过期；未覆盖会议自动使用 `generic` 并提醒作者复核官方指南。`unified-family` 是通用实现风格，不是任何会议的官方配色。

## Golden Task Board

公开看板只使用合成材料。它证明契约、路由、确定性辅助脚本和跨技能交接可用，不把任何模型的文笔宣传成科学质量排名。每个任务在 `verified_by` 字段中指明验证它的公开测试模块。

| 合成任务 | 可检查产物 | CI 断言 |
| --- | --- | --- |
| Evidence | source plan、metadata ledger、claim map | 不推断来源支持 |
| Writing | 贡献与 claim map | 缺失证据保持显式 |
| Polishing | revision ledger | 数字和引用锚点保留 |
| Figure | render spec 与 export bundle | 可编辑 SVG/PDF/PNG 和 QA |
| Reviewer | consequence-based issue board | 不确定性得到校准 |
| Response | 回复与 revision ledger | 不虚构实验或承诺 |
| Workflow | 项目本地交接图 | advisory 与 strict 状态一致 |

查看 [Golden Task Board](examples/golden-tasks/README.md) 与[质量边界](docs/QUALITY.md)。当前 CI 在 Windows、Ubuntu 运行完整单元、验收、evidence、figure 与安装检查，并在 macOS 运行宿主 smoke。

## 图件能力

图件技能不仅是"换一套配色"：15 个视觉家族、YAML/CSV render spec、Python-first 渲染、SVG/PDF/PNG 导出、配色 provenance、caption/callout 对齐和视觉 QA。下面每一张图都由仓库内的渲染管线从合成输入确定性生成：

![由渲染管线生成的多面板科研图拼图](assets/figure-gallery-collage.png)

| Benchmark and ablation | Systems scaling | Venue-aware example |
| --- | --- | --- |
| ![Benchmark and ablation](skills/top-cs-figure/assets/gallery/benchmark-ablation.png) | ![Systems scaling tradeoff](skills/top-cs-figure/assets/gallery/systems-scaling-tradeoff.png) | ![ICML heatmap](skills/top-cs-figure/assets/gallery/icml-heatmap-venue.png) |

## 隐私、证据与安装边界

- 仓库只发布原创代码、文档、合成资产与聚合证据；绝不包含用户稿件、审稿文本、原始实验数据或凭据。
- 在线证据核验需作者显式授权，仅查询 Crossref、arXiv、DBLP 的公开元数据，不下载全文。
- 安装器只复制选中的技能、`skills/_shared` 和派生 evidence；不复制 docs、tests、examples 或展示资产，也不写入宿主 settings 文件。
- 将输出用于投稿前，请先阅读[证据与来源](docs/EVIDENCE.md)、[质量与 Golden Tasks](docs/QUALITY.md)和[宿主兼容](docs/HOSTS.md)。

## 仓库结构

```text
skills/                 # 六个专项包、可选协调器与共享契约
evidence/derived/       # 仅公开聚合证据
examples/golden-tasks/  # 合成的契约演示
examples/synthetic-paper/ # 输入与输出成品的完整合成示例
docs/                   # 工作流、质量、证据、架构与维护文档
tests/                  # 合成单元、验收与 figure 回归夹具
```

## 贡献与许可证

贡献前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 的证据、隐私与测试要求。欢迎中英文 Issue 和 PR。本仓库采用 MIT；第三方会议网站与链接来源仍遵循其各自条款。
