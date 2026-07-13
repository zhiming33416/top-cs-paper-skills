# `top-cs-polishing` 技能

[English](README_EN.md) · [返回仓库首页](../../README.md)

状态：**Beta**

在保留证据、技术含义和作者意图的前提下，翻译、压缩、重构或诊断计算机科学论文文本与 LaTeX。

## 适合用它做什么

- 中文到学术英文的保真改写。
- 段落流、章节结构、术语和 claim strength 调整。
- 降低冗余、空泛表达和模板化 AI 文风。
- 检查 LaTeX 多文件项目、浮动体、溢出和版面问题。

## 典型请求

- `把这段中文改成简洁英文，所有数字、数据集和限定词必须保留。`
- `压缩 Related Work 20%，不要删掉引用或对比关系。`
- `诊断这个 LaTeX 项目的 overfull box 和图表位置问题。`

## 你需要提供

原始文本或 LaTeX 项目、目标章节与会议，以及不可改变的术语、事实、数值、引用和格式约束。

## 产出

修订文本或安全的 LaTeX 修改、关键变化说明、保留项检查、风险提示，以及必要时的修订台账。

## 边界

不会从零补写缺失研究内容，也不会把弱证据改成强结论。需要构建论文论证时使用 `top-cs-writing`；需要模拟评审时使用 `top-cs-reviewer`。

## 运行和依赖

基础文本修订无需额外 Python 包。LaTeX QA 脚本会使用本机已有的 TeX 工具，并在隔离临时目录中运行。完整安装方式见[安装指南](../../INSTALL.md)。

## 相关技能

- [`top-cs-writing`](../top-cs-writing/README.md)：规划与起草内容。
- [`top-cs-reviewer`](../top-cs-reviewer/README.md)：发现稿件级风险。
- [`top-cs-response`](../top-cs-response/README.md)：将修订绑定到审稿意见。
