# Top CS Paper Skills

[English](README_EN.md) · [安装指南](INSTALL.md) · [技能索引](#技能索引) · [文档导航](docs/README.md) · [参与贡献](CONTRIBUTING.md)

[![CI](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-5-6f42c1)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)

![Top CS Paper Skills：面向顶级计算机科学会议的证据驱动 Codex skills](assets/top-cs-paper-skills-banner.png)

面向计算机科学论文工作流的五个 Codex skills：从论证与写作，到保真润色、投稿前预审、审稿回复和可复现科研图件。它们以证据边界、可追溯的输入输出和保守表述为共同原则。

## 适用范围与边界

- 当前会议证据快照覆盖 WWW Research、ICLR 和 ICML 2026；提交前始终应重新核对目标会议的官方页面。
- <code>generic</code> 模式提供通用写作、审查和证据检查，不把经验规则包装为任何会议的最新政策。
- 仓库仅发布原创代码、文档、合成图件与聚合证据；不包含论文全文、审稿全文、私有实验数据、用户材料或凭证。
- 证据来源、快照范围、已知局限和隐私边界详见 [Evidence and provenance](docs/EVIDENCE.md)。

## 快速开始

最省事的方式是把下面提示词发送给 Codex：

~~~text
请从 https://github.com/zhiming33416/top-cs-paper-skills.git 安装全部 Codex skills。
请 clone 仓库并运行 python scripts/install_skills.py，随后运行
python scripts/install_skills.py --check。请保留完整的 skills/top-cs-*、
skills/_shared 和派生 evidence 目录；不要只复制 SKILL.md。完成后提醒我开启新的 Codex 会话。
~~~

也可以手动安装：

~~~bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python scripts/install_skills.py
python scripts/install_skills.py --check
~~~

默认目标是 <code>~/.codex/skills</code>。选择单个或多个技能、更新、Windows/macOS/Linux 说明与排错步骤见 [INSTALL.md](INSTALL.md)。

## 选择技能

| 你的目标 | 优先使用 | 典型输入 | 主要交付 |
| --- | --- | --- | --- |
| 从结果与想法开始搭建论文 | [top-cs-writing](skills/top-cs-writing/README.md) | 研究问题、实验结论、目标章节 | 论证结构、章节大纲、英文草稿 |
| 保真翻译、压缩或调整 LaTeX | [top-cs-polishing](skills/top-cs-polishing/README.md) | 原文、修改范围、格式约束 | 修订文本与可核查修改台账 |
| 投稿前发现技术与实验风险 | [top-cs-reviewer](skills/top-cs-reviewer/README.md) | 稿件、附录、目标会议与审查模式 | 按优先级排序的作者侧风险审计 |
| 回复评审并跟踪修订 | [top-cs-response](skills/top-cs-response/README.md) | review、已有证据、修订状态 | issue 矩阵、逐点回复、修订台账 |
| 制作或审计投稿级图件 | [top-cs-figure](skills/top-cs-figure/README.md) | figure brief、CSV 或 render spec | 可编辑图件、导出包、视觉 QA 报告 |

## 技能索引

| 技能 | 阶段 | 你提供什么 | 得到什么 | 可直接这样请求 |
| --- | --- | --- | --- | --- |
| [top-cs-writing](skills/top-cs-writing/README.md) | 规划与起草 | 贡献、证据、论文类型、章节、会议 | 论证图、提纲、草稿与待补证据 | “使用 top-cs-writing，根据这些实验结果规划 ICLR Introduction。” |
| [top-cs-polishing](skills/top-cs-polishing/README.md) | 保真修订 | 中文/英文段落或 LaTeX、修改目标 | 修订版本、修改台账、未决输入 | “使用 top-cs-polishing，把这段中文改成简洁学术英语，不加强主张。” |
| [top-cs-reviewer](skills/top-cs-reviewer/README.md) | 投稿前审计 | 稿件、实验、附录、目标会议 | 技术、实验、复现与范围风险 | “使用 top-cs-reviewer，审查这篇 WWW 稿件的主要拒稿风险。” |
| [top-cs-response](skills/top-cs-response/README.md) | 评审讨论与修订 | 审稿意见、已有结果、修订证据 | 回复草稿、证据映射、revision ledger | “使用 top-cs-response，把这些意见整理为逐点回复和修订清单。” |
| [top-cs-figure](skills/top-cs-figure/README.md) | 图件生产与 QA | 数据、图件任务书、输出格式 | SVG/PDF/PNG、渲染记录、质量检查 | “使用 top-cs-figure，根据 CSV 生成可编辑的 benchmark 与 ablation 图。” |

每个详情页都说明适用任务、输入、输出、边界、依赖与相关技能。<code>skills/_shared</code> 是五项技能的共享依赖，不是第六个独立技能。

## 协作流程

~~~text
研究证据与贡献
        ↓
top-cs-writing ──────────→ top-cs-figure
        ↓                       ↕
top-cs-polishing       图件 QA / 修订 / 导出
        ↓                       ↕
top-cs-reviewer ─────────→ top-cs-response
~~~

图件技能可在写作阶段生成主图、在预审阶段检查可读性与证据一致性、在回复阶段生成补充实验或修订图。各技能不会凭空补造实验、引用、审稿立场或会议规则。

## 图件示例

以下预览均由仓库内的确定性合成数据和渲染器生成，不含论文截图或用户数据。

| Benchmark 与消融 | 系统扩展权衡 | 会议感知示例 |
| --- | --- | --- |
| ![Benchmark and ablation](skills/top-cs-figure/assets/gallery/benchmark-ablation.png) | ![Systems scaling tradeoff](skills/top-cs-figure/assets/gallery/systems-scaling-tradeoff.png) | ![ICML heatmap](skills/top-cs-figure/assets/gallery/icml-heatmap-venue.png) |

<code>unified-family</code> 是可跨场景复用的通用配色与层级方案，不是任何期刊或会议的官方视觉规范。会议感知配置、通用回退和配色证据见 [palette profiles](skills/top-cs-figure/references/palette-profiles.md)。

## 项目结构

~~~text
.
├── .github/                 # CI、Issue 与 PR 模板
├── assets/                  # README 宣传图等仓库展示资产；不会安装
├── config/evidence/         # 维护者的来源与政策配置；不会安装
├── docs/                    # 架构、证据、开发文档
├── evidence/derived/        # 可公开的聚合证据；安装时随共享资源提供
├── scripts/                 # 安装、路由、采集和验证工具
├── skills/
│   ├── _shared/             # 五项技能共享的契约、会议材料与资源
│   └── top-cs-*/            # 五个可安装的技能包
├── tests/
│   ├── cases/               # 可执行的公开验收与 figure 评测矩阵
│   └── fixtures/            # 小型合成输入与公开 mock 记录
├── README.md
├── README_EN.md
├── INSTALL.md
├── CONTRIBUTING.md
├── requirements.txt
└── LICENSE
~~~

安装器只复制选定的 <code>skills/top-cs-*</code>、<code>skills/_shared</code> 和 <code>evidence/derived</code>。<code>assets/</code>、<code>config/</code>、<code>docs/</code>、<code>scripts/</code> 与 <code>tests/</code> 服务于展示、维护和贡献，不会进入用户的 Codex skills 目录；测试范围说明见 [tests/README.md](tests/README.md)。

## 文档导航

| 文档 | 何时阅读 |
| --- | --- |
| [安装指南](INSTALL.md) | 首次安装、选择技能、更新或排错时。 |
| [技能索引与详情页](#技能索引) | 判断任务归属并查看每个技能的输入输出时。 |
| [Architecture](docs/ARCHITECTURE.md) | 需要理解共享目录、路由和兼容性边界时。 |
| [Evidence and provenance](docs/EVIDENCE.md) | 需要核查来源、快照、许可与隐私边界时。 |
| [Development guide](docs/DEVELOPMENT.md) | 运行测试、更新证据或维护脚本时。 |
| [完整文档目录](docs/README.md) | 浏览所有维护者文档时。 |

## 开发与贡献

贡献新规则、技能、脚本或文档前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 与 [Development guide](docs/DEVELOPMENT.md)。公开 CI 会在 Ubuntu 和 Windows、Python 3.10 与 3.12 上运行单元测试、证据验证和 figure 评测。

~~~bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_evidence.py --index evidence/derived/corpus-index.yaml --rules evidence/derived/rules.yaml --strict
python skills/top-cs-figure/scripts/run_figure_evals.py
~~~

Issue 和 Pull Request 欢迎使用中文或英文；请勿提交私有稿件、审稿往来、凭证、原始语料或无法再分发的第三方材料。

## 许可证

本项目采用 [MIT License](LICENSE)。MIT 仅适用于本仓库原创的代码、文档和合成资产；链接到的会议网站、论文、模板和其他第三方材料仍分别适用其自身条款。
