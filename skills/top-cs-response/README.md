# `top-cs-response` 技能

[English](README_EN.md) · [返回仓库首页](../../README.md)

状态：**Beta**

解析编辑和审稿意见，把问题、证据、回复文本与稿件修订绑定成可验证的 response package。

## 适合用它做什么

- 整理 decision email、review、discussion 或 revision request。
- 合并重复问题并建立稳定 issue ID 与状态。
- 起草 point-by-point response、rebuttal、cover letter 和修订台账。
- 核对回复中声称的实验、文本和图表修改是否真实完成。

## 典型请求

- `把这三份 review 合并成按优先级排序的问题板，并起草逐点回复。`
- `检查这份 rebuttal 是否承诺了尚未完成的实验。`
- `根据修改稿和审稿意见生成 response letter 与 revision ledger。`

## 你需要提供

完整的编辑或审稿文本、目标会议、当前回复阶段，以及已有证据、修改稿、实验结果和不能承诺的事项。

## 产出

问题板、逐点回复、证据映射、修改位置、未解决事项、cover letter 和 LaTeX response 模板。

## 边界

不会编造实验结果、稿件改动、审稿人态度、会议政策或未来承诺。缺少证据时会保留占位和明确的作者行动项。

## 运行和依赖

模板和基础流程无需额外 Python 包。引用核验等辅助脚本的依赖见仓库 `requirements.txt`；完整安装说明见[安装指南](../../INSTALL.md)。

## 相关技能

- [`top-cs-reviewer`](../top-cs-reviewer/README.md)：在真实评审前发现问题。
- [`top-cs-polishing`](../top-cs-polishing/README.md)：执行承诺的文本修订。
- [`top-cs-figure`](../top-cs-figure/README.md)：修订被审稿意见指出的图件。
