# Top CS Paper Skills

面向 WWW、ICLR、ICML 论文写作全流程的 Codex skills 仓库。首版以 2026 年官方投稿规则为硬约束，并将论文样例中观察到的写作惯例标记为软规则。

## Skills

Current installable skills:

- `top-cs-writing`: plan and draft evidence-grounded CS conference papers.
- `top-cs-polishing`: revise prose and LaTeX while preserving evidence.
- `top-cs-reviewer`: run confidential author-side manuscript audits.
- `top-cs-response`: draft and verify reviewer-response packages.
- `top-cs-figure`: create, revise, export, and QA Python-rendered paper figures from figure briefs and source data.

- `top-cs-writing`：构建论证、章节大纲和英文草稿。
- `top-cs-polishing`：在不改变证据的前提下重构和润色。
- `top-cs-reviewer`：按技术、实验/复现、venue/scope 三个视角预审。
- `top-cs-response`：整理审稿意见、起草逐点回复和修订清单。

默认用中文说明问题，论文正文和 rebuttal 使用英文。支持 `.tex`、Markdown、纯文本、中文笔记和 PDF。

## Architecture

四个技能共享证据纪律、匿名性、论文类型和会议来源，但不再强制使用同一套路由：

- `top-cs-writing`：`venue × paper_type × section × language` 多轴路由；按需加载章节片段。
- `top-cs-polishing`：同样使用四轴路由，并增加 failure modes、claim-strength 与 LaTeX QA。
- `top-cs-reviewer`：只把 `venue` 作为内容轴；手稿范围和评审模式是运行时参数。
- `top-cs-response`：不使用内容轴；按 venue、task mode、response phase、decision type 和 language 运行线性状态机。

每个技能的 `manifest.yaml` 声明 `always_load`、路由轴或运行时参数，以及 `references.on_demand`。`static/core/` 保存每次必须执行的立场、工作流和输出格式；`static/fragments/` 保存按路由加载的内容；`references/` 仅在具体条件满足时加载。

## Evidence basis

仓库使用外部只读语料生成可移植证据，不复制论文或评审全文：

- 100个PDF文件、99个唯一SHA；重复的 `Agent0-VL` 只计一次。
- 主要写作证据为 ICLR 30、ICML 30、WWW Research 30，共90篇。
- WWW Industry、Short、Web4Good仅索引，不进入Research风格规则。
- 全文均标记为“接收题名核验的公开版本”，不能作为官方格式、页数或匿名要求来源。
- 25篇历史ICLR公开流程提供94份review和32个discussion threads，仅用于review/response行为模式。

派生索引、统计和人工晋级规则位于 `evidence/derived/`。安装时这些文件会复制到 `_shared/evidence/derived/`。

## Install

```powershell
python scripts/install_skills.py --target "$HOME/.codex/skills"
python scripts/install_skills.py --target "$HOME/.codex/skills" --check
```

安装会复制四个 skill 及其 `_shared` 依赖，不删除目标目录中的其他内容。使用前开启新的 Codex 会话。

## Tools

```powershell
python scripts/build_corpus_manifest.py --input .. --output corpus-sources.generated.yaml
python scripts/audit_submission.py --venue iclr --year 2026 --source paper.tex --pdf paper.pdf
python scripts/collect_public_sources.py --config public-sources.yaml --cache-root "C:\path\to\external-corpus" --dry-run
python scripts/collect_visual_style_corpus.py --corpus-root "D:\桌面\www" --year 2026 --target-per-venue 30 --venues www,iclr,icml
python scripts/collect_visual_style_corpus.py --corpus-root "D:\桌面\www" --year 2026 --target-per-venue 30 --venues iclr --candidate-seed "D:\桌面\www\sources\iclr2026-accepted-title-expansion.yaml"
python scripts/derive_corpus_evidence.py --corpus-root "C:\path\to\corpus" --output-dir evidence\derived --schema-version 2
python scripts/derive_visual_style_evidence.py --corpus-root .. --output-dir evidence\derived --local-only
python scripts/derive_visual_style_evidence.py --corpus-root "D:\桌面\www" --source-manifest evidence\derived\visual-style-source-manifest.yaml --output-dir evidence\derived
python scripts/validate_evidence.py --index evidence\derived\corpus-index.yaml --rules evidence\derived\rules.yaml --strict
python scripts/route_skill.py --skill top-cs-writing --venue iclr --paper-type empirical --section abstract --language zh-to-en --format json
python scripts/route_skill.py --skill top-cs-figure --venue icml --visual-family comparison --need visual-style --format json
python scripts/route_skill.py --skill top-cs-writing --venue icml --section experiments --need full-section-corpus --format json
python scripts/evaluate_skill_output.py --case tests\acceptance-cases.yaml --case-id iclr-abstract-from-chinese-notes --source notes.md --output draft.md
python scripts/verify_citations.py --bib references.bib --output citation-report.json --format json --cache-dir .citation-cache
python skills\top-cs-polishing\scripts\check_latex_project.py --project paper --root main.tex --format json
python skills\top-cs-figure\scripts\render_from_figure_spec.py --spec tests\fixtures\figure-specs\comparison.yaml --outdir "C:\tmp\figures"
python skills\top-cs-figure\scripts\check_figure_bundle.py --base "C:\tmp\figures\comparison" --format json
python skills\top-cs-figure\scripts\audit_figure_spec.py --spec tests\fixtures\figure-specs\multipanel-ablation.yaml --base "C:\tmp\figures\multipanel-ablation"
python skills\top-cs-figure\scripts\run_figure_evals.py
python skills\top-cs-figure\scripts\run_private_figure_regressions.py --suite "D:\private-figure-evals\suite.yaml" --output "D:\private-figure-evals\aggregate-report.json"
python skills\top-cs-figure\scripts\build_figure_atlas.py --output-root skills\top-cs-figure\assets
```

`derive_corpus_evidence.py` 只读取 corpus root，输出SHA去重索引和聚合统计，不写回语料库，也不保存论文/评审正文。统计候选不会自动成为skill规则；软规则必须经过阈值和人工语义审查。

`generic` 只执行通用论证和证据检查，不代表任何会议的最新政策。投稿前始终重新核对目标会议官网。

## Phase-2 readiness

Schema v2 records structural features, paper-type/topic candidates, version-pair status, policy validity, and explicit readiness gaps. The current baseline is 100 files, 99 unique hashes, and 90 eligible main-track papers. All 90 topic and paper-type labels remain assistant-reviewed candidates pending human confirmation; structural statistics may be used now, but label-dependent rules may not be promoted yet.

The machine-readable preparation backlog is in `data-preparation.yaml`. Raw public downloads must remain in the external corpus. Private regression suites, specs, data, and rendered artifacts remain outside the repository; the aggregate-only runner reports anonymized IDs, hashes, geometry, perceptual distance, scores, and error categories.

Full-section structural evidence for method, experiments, discussion, limitations, and conclusion is generated in `evidence/derived/full-section-rules.yaml`. Reference selection supports deterministic explicit needs and route-derived automatic needs. The output evaluator can enforce structured semantic contracts and source-artifact preservation. Multi-file LaTeX compilation is isolated, disables shell escape, and leaves the source project unchanged.

## Version 4.1 figure production boundary

The paper-writing, polishing, reviewer, and response skills share machine-readable citation, figure-handoff, and response-issue contracts. Functional rhetorical moves and topic-sentence scaffolds guide full-section work without becoming venue rules. Citation verification queries public Crossref, arXiv, and DBLP metadata with cache/offline support; it never treats metadata existence as claim entailment or downloads full text. Response work uses stable issue IDs, explicit state transitions, and an optional three-round adversarial self-check.

Figure planning still begins with the shared `figure-brief` contract. The `top-cs-figure` skill is the only skill that owns rendering backend, allow-listed data transforms, descriptive statistics, visual grammar, palette, export bundles, and image QA; the other four skills continue to hand off or audit figures without rendering them. Strict v3 render specs produce panel-level plotted-data CSVs, including declared schematic geometry, a normalized spec, render manifest, SVG/PDF/PNG, and an optional revision audit. V1/v2 specs remain supported through an explicit recorded migration.

Visual-style evidence is derived as aggregate-only statistics in `evidence/derived/visual-style-*`; it is never official venue policy. The 2026-07-13 snapshot contains 30 verified independent sources for each of WWW Research, ICLR, and ICML. All three report promoted style evidence plus usable anchors and co-occurrence profiles. Runtime styling resolves six task-specific families: semantic, categorical, ordered, sequential, diverging, and dark-overlay. Every color is labeled as an observed anchor, an accessibility-constrained constructed token, or a generic fallback; the live rules file remains authoritative for future runs.

Figure-style corpus expansion uses `visual-style-source-manifest.yaml` as the stable provenance layer. Raw public PDFs must stay under the external corpus root, normally `D:\桌面\www\papers\{WWW2026,ICLR2026,ICML2026}\verified_fulltext\`; the skill repo stores only source metadata, hashes, aggregate color/layout statistics, and confidence labels. WWW Research rows require title-exact public fulltext and must not use ACM-restricted PDFs or non-Research tracks to fill style gaps.

The visual collector resolves title-exact public arXiv PDFs for WWW, ICLR, and ICML only after each title is admitted by the accepted-title corpus index. Resolver cache files remain under the external corpus root. Public preprints may contribute aggregate visual-style evidence after verification, but never establish official venue formatting policy.

The lightweight atlas under `skills/top-cs-figure/assets/` contains 13 chart-atlas PNGs and 14 composite CS gallery PNGs, totaling 222 rendered panels. It includes one six-family palette atlas and two venue-aware scenario galleries per conference. Every asset is generated through the strict v3 production renderer from deterministic synthetic CSV/YAML/image inputs; `generated-manifest.yaml` records generator, renderer, style dependency, venue, input, output, panel-count, and size hashes. No paper screenshots, user images, raw corpus files, or external visual assets are included.
