# 完整论文工作流 / Full-paper Workflow

[中文首页](../README.md) · [English home](../README_EN.md) · [安装](../INSTALL.md) · [宿主兼容](HOSTS.md) · [合成示例](../examples/synthetic-paper/README.md)

## 中文

`top-cs-paper-workflow` 是可选协调包，用于一篇论文需要跨越写作、图件、预审、回复和修订多个阶段的情况。单个段落润色、一张图或一次预审，仍应直接使用对应的五个专项技能。

它在用户明确选择的 `<project-root>/.top-cs-paper/workflow.yaml` 中保存可恢复的状态。manifest 只记录 venue/year、论文类型、投稿阶段、相对路径、可选哈希与交接 ID；不会复制、上传或推断稿件、数据、PDF、review 内容或凭证。

### 快速使用

在本仓库 clone 中：

```bash
python skills/top-cs-paper-workflow/scripts/paper_workflow.py init --project <project-root>
python skills/top-cs-paper-workflow/scripts/paper_workflow.py inventory --project <project-root> --include manuscript/main.tex
python skills/top-cs-paper-workflow/scripts/paper_workflow.py status --project <project-root> --format markdown
```

安装后，将脚本位置替换为 `<skills-root>/top-cs-paper-workflow/scripts/paper_workflow.py`。`<skills-root>` 是通过安装器选择的 Codex 或 Claude Code skills 根目录，不是仓库路径。

默认状态检查只报告缺口；只有准备将阶段标记为 ready 并需要 CI 式约束时才使用严格模式：

```bash
python skills/top-cs-paper-workflow/scripts/paper_workflow.py status --project <project-root> --strict
```

严格模式会因“已声明 ready、但交接链未闭环”返回非零状态。它不会替作者确认实验、结论、引用、审稿立场或会议政策。

### 六个检查点与交接

| 检查点 | 目标 | 典型交接内容 |
| --- | --- | --- |
| `brief` | 锁定研究范围与投稿场景 | venue/year、论文类型、阶段 |
| `claims` | 将贡献拆成可核查主张 | claim ID、论证与证据状态 |
| `evidence-and-figures` | 连接证据、数据与图件 | evidence ID、figure brief、figure ID |
| `manuscript` | 将已确认信息落入稿件 | 章节位置、未决输入、修订记录 |
| `review` | 记录作者侧风险和可行动项 | risk/issue ID、证据缺口、优先级 |
| `response` | 把承诺落实为回复和修改 | response ID、revision ID、最终位置 |

工作顺序为：

```text
贡献与论证 → 证据与主图 → 稿件与润色 → 投稿前预审 → 回复与修订
 top-cs-writing    top-cs-figure    top-cs-polishing     top-cs-reviewer   top-cs-response
```

`top-cs-figure` 可在写作阶段产出主图，在预审阶段检查可读性和证据一致性，并在回复阶段制作补充或修订图。协调包只验证交接是否可追溯；各专项技能仍拥有各自的工作流和边界。

### 隐私与安全边界

- `inventory` 只接受用户给出的、相对于项目根目录的 `--include` 路径；不会递归扫描 home 目录、云盘或磁盘。
- 路径越出 `<project-root>`、绝对路径和不安全的链接目标都会被拒绝。
- 合成示例仅演示 ID 与交接格式，见 [examples/synthetic-paper](../examples/synthetic-paper/README.md)；它不是论文模板，也不应替换真实作者判断。
- 会议政策仍必须由专项技能的官方来源快照和提交前复核支持，不能从本 manifest 推导。

---

## English

`top-cs-paper-workflow` is an optional coordinator for a paper that crosses drafting, figures, review, response, and revision. For one paragraph, one figure, or one audit, invoke the relevant specialist skill directly.

It keeps resumable state in `<project-root>/.top-cs-paper/workflow.yaml`, under a project root explicitly selected by the user. The manifest records venue/year, paper type, submission stage, relative paths, optional hashes, and handoff IDs only. It does not copy, upload, or infer manuscript text, data, PDFs, review content, or credentials.

### Quick use

From a repository clone:

```bash
python skills/top-cs-paper-workflow/scripts/paper_workflow.py init --project <project-root>
python skills/top-cs-paper-workflow/scripts/paper_workflow.py inventory --project <project-root> --include manuscript/main.tex
python skills/top-cs-paper-workflow/scripts/paper_workflow.py status --project <project-root> --format markdown
```

After installation, replace the script path with `<skills-root>/top-cs-paper-workflow/scripts/paper_workflow.py`. `<skills-root>` is the Codex or Claude Code skills root selected by the installer, not a repository path.

Status is advisory by default. Use strict mode only when a stage is being declared ready and a CI-style constraint is useful:

```bash
python skills/top-cs-paper-workflow/scripts/paper_workflow.py status --project <project-root> --strict
```

Strict mode returns nonzero when a stage is declared ready but its handoff chain is incomplete. It never confirms experiments, conclusions, citations, reviewer positions, or venue policy for the author.

### Six checkpoints and handoffs

| Checkpoint | Purpose | Typical handoff |
| --- | --- | --- |
| `brief` | Fix the research scope and submission context | venue/year, paper type, stage |
| `claims` | Turn contributions into auditable claims | claim ID, argument, evidence state |
| `evidence-and-figures` | Connect evidence, data, and figures | evidence ID, figure brief, figure ID |
| `manuscript` | Place confirmed content in the manuscript | section location, unresolved input, revision record |
| `review` | Track author-side risks and actionable work | risk/issue ID, evidence gap, priority |
| `response` | Turn commitments into responses and edits | response ID, revision ID, final location |

The intended sequence is:

```text
Contribution and argument → Evidence and principal figures → Manuscript and polish → Pre-submission review → Response and revision
     top-cs-writing            top-cs-figure              top-cs-polishing        top-cs-reviewer       top-cs-response
```

`top-cs-figure` can produce principal figures during drafting, check readability and evidence consistency during review, and create supplemental or revision figures during response. The coordinator validates traceable handoffs only; each specialist keeps its own workflow and boundaries.

### Privacy and safety boundary

- `inventory` accepts only user-provided `--include` paths relative to the project root; it never recursively crawls a home directory, cloud drive, or disk.
- Paths outside `<project-root>`, absolute paths, and unsafe link targets are rejected.
- The [synthetic example](../examples/synthetic-paper/README.md) demonstrates IDs and handoffs only. It is not a paper template and cannot replace author judgement.
- Venue policy must still be supported by the specialist skills' official-source snapshots and a pre-submission recheck; it cannot be inferred from a manifest.
