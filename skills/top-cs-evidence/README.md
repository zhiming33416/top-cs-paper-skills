# Top CS Evidence

[English](README_EN.md)

为顶会论文建立由作者控制的 claim–source 证据链：规划文献定位、核验 BibTeX/DOI 元数据、记录来源与主张的关系，并把未解决项明确交接给写作、预审或回复技能。

## 适用任务

- 为贡献、相关工作或审稿回复建立引用与来源计划。
- 核验作者提供的 BibTeX、DOI 或 arXiv 标识。
- 将作者提供的摘录或笔记映射到具体 claim。

## 输入与交付

输入为 claim 列表、BibTeX/DOI，以及可选的作者摘录或笔记。输出为 source plan、citation ledger、claim–source map 和缺口清单；不会生成未经授权的引用或论文正文。

## 快速使用

```bash
python scripts/paper_evidence.py plan --claims claims.yaml --output evidence-plan.yaml
python scripts/paper_evidence.py verify --bib references.bib --output citation-ledger.yaml
python scripts/paper_evidence.py verify --bib references.bib --output citation-ledger.yaml --online
```

默认离线。只有显式使用 `--online` 才会查询 Crossref、arXiv 和 DBLP 的公开元数据；不会下载全文。

## 边界与协作

“元数据已验证”不等于“该论文支持当前主张”。只有作者提供相关来源摘录或笔记时，才可将 claim entailment 标为支持状态。随后将 ledger 交给 `top-cs-writing`、`top-cs-reviewer` 或 `top-cs-response`；用 `top-cs-paper-workflow` 记录项目级 ID 与状态。
