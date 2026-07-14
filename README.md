# Top CS Paper Skills

[English](README_EN.md) · [安装指南](INSTALL.md) · [技能索引](#技能索引) · [设计与证据](docs/EVIDENCE.md) · [参与贡献](CONTRIBUTING.md)

[![CI](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/zhiming33416/top-cs-paper-skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Skills](https://img.shields.io/badge/skills-5-6f42c1)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB)

面向 WWW、ICLR、ICML 及通用计算机科学会议工作流的五个 Codex skills，覆盖论文写作、语言与 LaTeX 润色、投稿前预审、审稿回复和科研图制作。

这些技能强调证据边界、可复现过程和保守表达。仓库中的会议资料和语料统计不是官方投稿政策；正式投稿前请始终重新核对目标会议官网。

## 快速开始

安装后，直接把论文、段落、实验数据、审稿意见或任务描述交给 Codex：

| 想做什么 | 可以这样说 |
| --- | --- |
| 规划或撰写论文 | `使用 top-cs-writing，根据这些实验结果为 ICLR 论文设计论证和 Introduction。` |
| 润色或中译英 | `使用 top-cs-polishing，把这段中文改写成简洁的学术英文，不增强原有主张。` |
| 投稿前预审 | `使用 top-cs-reviewer，检查这篇 WWW 稿件的主要拒稿风险和复现缺口。` |
| 回复审稿意见 | `使用 top-cs-response，把这些意见整理成逐点回复和可验证的修订清单。` |
| 制作科研图 | `使用 top-cs-figure，根据这份 CSV 和图件说明生成可编辑的 SVG/PDF/PNG。` |

## 技能索引

| Skill | 状态 | 用途 |
| --- | --- | --- |
| [`top-cs-writing`](skills/top-cs-writing/README.md) | Beta | 构建论文论证、章节大纲并起草英文内容。 |
| [`top-cs-polishing`](skills/top-cs-polishing/README.md) | Beta | 在不改变证据的前提下翻译、压缩、重构和检查 LaTeX。 |
| [`top-cs-reviewer`](skills/top-cs-reviewer/README.md) | Beta | 从作者侧模拟投稿前评审，定位技术、实验、复现和 venue 风险。 |
| [`top-cs-response`](skills/top-cs-response/README.md) | Beta | 解析审稿意见，起草回复、cover letter 和修订台账。 |
| [`top-cs-figure`](skills/top-cs-figure/README.md) | Beta | 使用 Python 生成、修订、导出和审计投稿级科研图。 |

`skills/_shared/` 保存五个技能共同使用的证据纪律、会议资料、契约和路由资源，不是独立技能。

## 安装

### 推荐：把仓库链接交给 Codex

将下面的提示词发给 Codex：

```text
请从这个仓库安装全部 Codex skills：
https://github.com/zhiming33416/top-cs-paper-skills.git

请 clone 仓库并运行 python scripts/install_skills.py。
安装后运行 python scripts/install_skills.py --check 验证。
请保留 skills/top-cs-* 的完整目录、skills/_shared 和派生 evidence，
不要只复制 SKILL.md。完成后提醒我开启新的 Codex 会话。
```

### 手动安装

```bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python scripts/install_skills.py
python scripts/install_skills.py --check
```

只安装一个或多个技能：

```bash
python scripts/install_skills.py --skill top-cs-writing
python scripts/install_skills.py --skill top-cs-writing --skill top-cs-figure
```

安装器默认写入 `~/.codex/skills`，自动携带 `_shared` 和派生 evidence，不会删除其他 Codex skills。完整的跨平台安装、更新和排错说明见 [INSTALL.md](INSTALL.md)。

## 工作方式

五个技能保持清晰分工，并通过共享契约协作：

1. `top-cs-writing` 从证据、论证和章节结构开始起草。
2. `top-cs-polishing` 对已有文本做保真修订，不负责补造内容。
3. `top-cs-reviewer` 对作者稿件进行保守的投稿前审计。
4. `top-cs-response` 将评审意见、证据和修订动作绑定到稳定 issue ID。
5. `top-cs-figure` 接收 figure brief、数据或 render spec，负责图件生产与 QA。

路由架构、共享目录和文件加载规则见 [Architecture](docs/ARCHITECTURE.md)。

## 图件示例

下列预览全部由仓库内的确定性合成数据和渲染器生成，不包含论文截图或用户数据。

| 多面板实验图 | 方法与系统图 | 会议感知示例 |
| --- | --- | --- |
| ![Benchmark and ablation](skills/top-cs-figure/assets/gallery/benchmark-ablation.png) | ![Systems scaling tradeoff](skills/top-cs-figure/assets/gallery/systems-scaling-tradeoff.png) | ![ICML heatmap](skills/top-cs-figure/assets/gallery/icml-heatmap-venue.png) |

## 证据与边界

- 官方投稿规则与语料观察严格分层；语料统计只作为软证据。
- 仓库不包含原始论文、评审全文、私有实验数据或用户材料。
- 技能不会把元数据存在性当作主张成立的证据，也不会编造实验、引用或审稿人立场。
- `generic` 模式只提供通用论证和证据检查，不代表任何会议的最新要求。

证据来源、快照范围和隐私边界见 [Evidence and provenance](docs/EVIDENCE.md)。

## 项目结构

```text
skills/                 # 五个可安装技能与共享依赖
evidence/derived/       # 可移植的聚合证据和来源索引
scripts/                # 安装、路由、验证和语料派生工具
tests/                  # 单元、验收和合成图件测试
docs/                   # 架构、证据与开发文档
```

## 开发与贡献

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -p "test_*.py"
python scripts/validate_evidence.py --index evidence/derived/corpus-index.yaml --rules evidence/derived/rules.yaml --strict
python skills/top-cs-figure/scripts/run_figure_evals.py
```

提交新规则、文档或技能前，请阅读 [CONTRIBUTING.md](CONTRIBUTING.md) 和 [Development guide](docs/DEVELOPMENT.md)。Issue 和 Pull Request 都欢迎使用中文或英文。

## License

本项目采用 [MIT License](LICENSE)。

MIT 许可证仅适用于本仓库原创代码、文档和合成资产；链接的会议网站、论文、模板和第三方材料仍适用其各自条款。
