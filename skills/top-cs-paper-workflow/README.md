# Top CS Paper Workflow

[English](README_EN.md)

可选的项目协调技能：把五个专项技能的交接记录在用户选择的论文项目中，而不把它们合并成一个巨型技能。

## 适用任务

适用于完整论文、跨技能修改、投稿前检查或审稿回复等需要恢复项目状态的工作；单次写作、润色、审稿、回复或作图请直接使用对应专项技能。

## 典型请求

“为这个论文项目建立可恢复的 claim–evidence–figure 交接状态，并告诉我下一步该调用哪个技能。”

## 输入

用户明确指定的 `<project-root>`，以及可选的相对路径材料。`inventory` 仅处理显式 `--include` 的文件。

## 输出

`<project-root>/.top-cs-paper/workflow.yaml`、材料的相对路径与 SHA-256 元数据，以及 Markdown 或 JSON 状态报告。

## 工作流与依赖

协调顺序为：写作的贡献与论证 → 图件的证据交接 → 润色 → 预审 → 回复与修订。它依赖并保留 `top-cs-writing`、`top-cs-polishing`、`top-cs-reviewer`、`top-cs-response`、`top-cs-figure` 的独立职责。

## 使用方式

在任意已安装宿主中调用此技能，或运行其脚本：

```text
python <installed-skill>/scripts/paper_workflow.py init --project <project-root>
python <installed-skill>/scripts/paper_workflow.py status --project <project-root> --strict
```

## 边界与依赖

依赖 Python 与 PyYAML。工具不会复制原稿、PDF、数据、审稿文字或引用内容；拒绝绝对路径、路径穿越和逸出项目目录的符号链接。`--strict` 只检查工作流闭环，不证明实验、政策或投稿结果。
