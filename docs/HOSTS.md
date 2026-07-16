# 宿主兼容 / Host Compatibility

[中文首页](../README.md) · [English home](../README_EN.md) · [安装](../INSTALL.md) · [完整工作流](WORKFLOW.md)

## 中文

本仓库以 `skills/` 为唯一权威来源。安装器把同一套完整技能目录安装到 Codex 或 Claude Code；不维护重复的 `src → dist` 发行树，也不修改宿主 settings 文件。

| 宿主 | `--host` | 默认 skills 根目录 | 会话要求 |
| --- | --- | --- | --- |
| Codex | `codex` | `~/.codex/skills` | 安装或更新后开启新会话 |
| Claude Code | `claude` | `~/.claude/skills` | 安装或更新后开启新会话 |

安装示例：

```bash
python scripts/install_skills.py --host codex
python scripts/install_skills.py --workflow --host claude
python scripts/install_skills.py --host codex --target <skills-root> --check
```

`--target` 覆盖默认根目录；使用 `--check` 时应重复同一个 `--host`、`--target`、`--skill` 或 `--workflow` 范围。安装器同步 `_shared` 和 `evidence/derived`，以避免相对引用断裂。

安装器会记录本仓库写入的文件。`--prune` 只可清理安装清单中的陈旧文件，并且不会删除无关技能或用户修改过的已跟踪文件。运行时不安装 Python 包；图件、PDF 或 evidence 工具依赖由用户按需通过 `requirements.txt` 安装。

目前不发布 OpenClaw、Hermes 或其他宿主的适配器。若需要新宿主，请先提交 Issue，说明该宿主如何发现 skills、目录格式、最小 smoke 测试和不破坏现有安装边界的方案。

---

## English

`skills/` is the only canonical source tree. The installer places the same complete skill directories into Codex or Claude Code; it does not maintain a duplicated `src → dist` release tree or modify host settings files.

| Host | `--host` | Default skills root | Session requirement |
| --- | --- | --- | --- |
| Codex | `codex` | `~/.codex/skills` | Start a new session after install or update |
| Claude Code | `claude` | `~/.claude/skills` | Start a new session after install or update |

Installation examples:

```bash
python scripts/install_skills.py --host codex
python scripts/install_skills.py --workflow --host claude
python scripts/install_skills.py --host codex --target <skills-root> --check
```

`--target` overrides a default root. Repeat the same `--host`, `--target`, `--skill`, or `--workflow` scope for `--check`. The installer synchronizes `_shared` and `evidence/derived` so relative references remain valid.

The installer records files written by this repository. `--prune` can clean only stale files in that manifest; it never removes unrelated skills or user-modified tracked files. Runtime packages are not installed automatically; users install figure, PDF, or evidence helper dependencies from `requirements.txt` only when needed.

OpenClaw, Hermes, and other host adapters are not currently published. Propose a new host through an Issue with its skill-discovery mechanism, directory format, a minimal smoke test, and a plan that preserves existing installation boundaries.
