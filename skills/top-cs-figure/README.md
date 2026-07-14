# `top-cs-figure` 技能

[English](README_EN.md) · [返回仓库首页](../../README.md)

状态：**Beta**

使用 Python-first、spec-driven 工作流规划、生成、修订、导出和审计计算机科学论文图件。

## 适合用它做什么

- 制作比较图、趋势图、区间图、热图、散点图、网络图、方法示意图和多面板图。
- 从 figure brief、CSV/YAML 数据或现有 render spec 生成图件。
- 导出 SVG、PDF、PNG 和可选 TIFF，并保留 plotted-data 与 render manifest。
- 检查颜色可访问性、图注/正文 callout、一致性、几何和图件完整性。

## 典型请求

- `根据这份 comparison.csv 生成带置信区间的 ICML 多面板图。`
- `把现有 figure brief 转成严格 render spec，并导出 SVG/PDF/PNG。`
- `审计这组图的面板标签、颜色区分、图注义务和源数据对应关系。`

## 你需要提供

优先提供 figure brief 或 render spec；也可以提供源数据、指标含义、期望结论、面板关系、图注要求、目标 venue 和输出格式。

## 产出

规范化 spec、panel-level plotted-data CSV、render manifest、SVG/PDF/PNG、可选 TIFF，以及 QA 或 revision audit 报告。

## 边界

不会编造数据、改变图片像素以配合结论或把语料风格描述成官方格式。跨 venue 的 `unified-family` 配色只是通用实现选择，不代表任何会议偏好。它不负责交互式 dashboard、Figma/Illustrator-first 排版或 AI 生成 graphical abstract。

## 运行和依赖

运行渲染和 QA 脚本前执行 `python -m pip install -r requirements.txt`。技能还依赖 `_shared` 和派生 visual-style evidence；请使用[安装指南](../../INSTALL.md)中的完整安装方式。

## 相关技能

- [`top-cs-writing`](../top-cs-writing/README.md)：创建 figure brief 和正文 callout。
- [`top-cs-polishing`](../top-cs-polishing/README.md)：检查图注和 LaTeX 布局。
- [`top-cs-response`](../top-cs-response/README.md)：将图件修订映射到评审问题。
