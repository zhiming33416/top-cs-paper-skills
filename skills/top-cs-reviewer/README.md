# `top-cs-reviewer` 技能

[English](README_EN.md) · [返回仓库首页](../../README.md)

状态：**Beta**

从作者侧对 WWW、ICLR、ICML 或通用计算机科学稿件执行保守的投稿前审计，提前暴露拒稿风险和证据缺口。

## 适合用它做什么

- 检查主张是否被方法、实验、图表和引用支持。
- 审计实验设计、基线、公平性、统计报告和复现信息。
- 检查匿名性、scope、track 和 venue fit。
- 对完整稿件或部分章节给出按严重程度排序的修改建议。

## 典型请求

- `按 ICLR 投稿前预审这篇完整稿件，优先列出可能导致拒稿的问题。`
- `只审查 Experiments，检查基线公平性和复现缺口。`
- `判断这篇系统论文更适合 WWW Research 还是 generic 模式，并说明不确定性。`

## 你需要提供

稿件或明确的章节范围、目标会议或 track，以及可用的附录、代码说明、实验协议和匿名性背景。

## 产出

范围声明、关键问题、严重程度、证据定位、可执行修订建议、缺失信息和投稿准备度总结。

## 边界

这是作者侧模拟，不是官方同行评审，也不能替代领域专家。不会冒充审稿人、推测身份或依据未经核验的会议政策给出确定结论。

## 运行和依赖

基础审计无需额外 Python 包，但依赖完整的 `_shared`、venue policy 和派生 evidence。安装方法见[安装指南](../../INSTALL.md)。

## 相关技能

- [`top-cs-writing`](../top-cs-writing/README.md)：根据审计结果重建论证。
- [`top-cs-polishing`](../top-cs-polishing/README.md)：执行文本和 LaTeX 修订。
- [`top-cs-response`](../top-cs-response/README.md)：处理真实审稿意见。
