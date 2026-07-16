# Top CS Paper Skills Installation Guide

[中文](#中文安装) · [English](#english-installation) · [完整工作流](docs/WORKFLOW.md) · [宿主兼容](docs/HOSTS.md)

## 中文安装

`top-cs-paper-skills` 不是 Python 包。五个 `skills/top-cs-*` 专项目录、可选的 `skills/top-cs-paper-workflow/`、共享目录 `skills/_shared/` 和派生 evidence 一起构成可安装内容。请安装完整目录，不要只复制 `SKILL.md`。

安装器支持 Codex 和 Claude Code，默认只安装五个专项技能；`--workflow` 才会额外安装协调包。它不会静默安装 Python 依赖、不会修改宿主的设置文件，也不会删除无关技能。

### 推荐：让 Codex 安装

把下面的提示词发给 Codex：

```text
请从这个仓库安装全部 Top CS Paper Skills 到 Codex：
https://github.com/zhiming33416/top-cs-paper-skills.git

请 clone 仓库，然后运行：
python scripts/install_skills.py --host codex
python scripts/install_skills.py --host codex --check
请保留完整的 skills/top-cs-*、skills/_shared 和 evidence/derived；不要只复制 SKILL.md。
完成后提醒我启动新的 Codex 会话。
```

Codex 可能会请求网络访问和写入 skills 目录的权限。安装完成后开启新会话，以便重新发现技能。

### 手动安装：Codex

Windows：

```powershell
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
Set-Location top-cs-paper-skills
py scripts/install_skills.py --host codex
py scripts/install_skills.py --host codex --check
```

macOS / Linux：

```bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python3 scripts/install_skills.py --host codex
python3 scripts/install_skills.py --host codex --check
```

如果 `py` 或 `python3` 不可用，请改用系统可用的 `python`。Codex 默认目标为 `~/.codex/skills`。

### 手动安装：Claude Code

在同一个 clone 中执行：

```bash
python scripts/install_skills.py --host claude
python scripts/install_skills.py --host claude --check
```

Claude Code 默认目标为 `~/.claude/skills`。安装后开启一个新会话；不会写入 Claude 或 Codex 的 settings 文件。关于宿主结构与限制见 [宿主兼容](docs/HOSTS.md)。

### 选择技能与完整工作流

查看可安装的专项技能：

```bash
python scripts/install_skills.py --list
```

只安装一个或多个专项技能：

```bash
python scripts/install_skills.py --skill top-cs-writing --host codex
python scripts/install_skills.py --skill top-cs-writing --skill top-cs-figure --host claude
```

无论选择几个专项技能，安装器都会同步 `_shared` 和 `evidence/derived`，以保持相对引用有效。默认安装不会加入协调包；完整论文项目使用：

```bash
python scripts/install_skills.py --workflow --host codex
python scripts/install_skills.py --workflow --host claude
```

协调包仅适用于跨技能、可恢复的完整论文项目；五个专项技能仍是单阶段任务的优先入口。安装后，协调脚本位于 `<skills-root>/top-cs-paper-workflow/scripts/paper_workflow.py`；`<skills-root>` 是所选宿主的技能根目录。

### 自定义安装位置与验证

通过 `--target` 覆盖默认宿主位置；验证时使用同一个 host、target 和选择范围：

```bash
python scripts/install_skills.py --host codex --target <skills-root>
python scripts/install_skills.py --host codex --target <skills-root> --check
python scripts/install_skills.py --workflow --host claude --target <skills-root> --check
```

如果 `--check` 显示 `missing`、`different` 或陈旧的已跟踪文件，重新运行相同选择范围的安装命令。`--check` 只检查，不复制文件。

### 更新与清理

在本地 clone 中执行：

```bash
git pull --ff-only
python scripts/install_skills.py --host codex
python scripts/install_skills.py --host codex --check
```

需要删除旧版本中、安装清单明确标记为本仓库所有且未被用户修改的文件时，显式添加 `--prune`：

```bash
python scripts/install_skills.py --host codex --prune
python scripts/install_skills.py --workflow --host codex --prune
```

`--prune` 不会删除无关技能，也不会删除已被用户修改的已跟踪文件；检查输出后再决定是否使用它。

### 可选 Python 依赖与排错

仅安装技能不需要第三方 Python 包。运行图件、PDF、语料或 evidence 辅助脚本前，才按需安装：

```bash
python -m pip install -r requirements.txt
```

贡献者可另外安装 lint 依赖：

```bash
python -m pip install -r requirements-dev.txt
```

如果宿主没有触发技能：开启新的会话，运行相同 host 与选择范围的 `--check`，确认目标目录包含选择的 `top-cs-*`、`_shared` 和 `_shared/evidence/derived`，然后使用明确匹配的任务或直接在提示词中写出技能名。

---

## English Installation

`top-cs-paper-skills` is not a Python package. The five specialist `skills/top-cs-*` directories, the optional `skills/top-cs-paper-workflow/`, `skills/_shared/`, and derived evidence make up the installable content. Install complete directories rather than copying only `SKILL.md`.

The installer supports Codex and Claude Code. By default it installs the five specialist skills; `--workflow` additionally installs the coordinator. It never silently installs Python dependencies, modifies host settings files, or removes unrelated skills.

### Recommended: ask Codex to install

Send Codex this prompt:

```text
Install all Top CS Paper Skills from this repository into Codex:
https://github.com/zhiming33416/top-cs-paper-skills.git

Clone the repository, then run:
python scripts/install_skills.py --host codex
python scripts/install_skills.py --host codex --check
Preserve the complete skills/top-cs-* folders, skills/_shared, and evidence/derived;
do not copy only SKILL.md. Remind me to start a new Codex session when finished.
```

Codex may request network access and permission to write to its skills directory. Start a fresh session after installation so skills can be discovered again.

### Manual installation: Codex

Windows:

```powershell
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
Set-Location top-cs-paper-skills
py scripts/install_skills.py --host codex
py scripts/install_skills.py --host codex --check
```

macOS / Linux:

```bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python3 scripts/install_skills.py --host codex
python3 scripts/install_skills.py --host codex --check
```

Replace `py` or `python3` with the available `python` command when needed. Codex defaults to `~/.codex/skills`.

### Manual installation: Claude Code

From the same clone, run:

```bash
python scripts/install_skills.py --host claude
python scripts/install_skills.py --host claude --check
```

Claude Code defaults to `~/.claude/skills`. Start a fresh session after installation; the installer does not write Claude or Codex settings files. See [Host compatibility](docs/HOSTS.md) for the directory layout and constraints.

### Select skills and the full-paper workflow

List installable specialist skills:

```bash
python scripts/install_skills.py --list
```

Install one or several specialist skills:

```bash
python scripts/install_skills.py --skill top-cs-writing --host codex
python scripts/install_skills.py --skill top-cs-writing --skill top-cs-figure --host claude
```

The installer always synchronizes `_shared` and `evidence/derived`, no matter how many specialist skills are selected. The coordinator is not installed by default; use it for a full paper project:

```bash
python scripts/install_skills.py --workflow --host codex
python scripts/install_skills.py --workflow --host claude
```

The coordinator is for resumable, cross-skill paper projects only; the five specialist skills remain the preferred entry points for a single-stage task. After installation, its script lives at `<skills-root>/top-cs-paper-workflow/scripts/paper_workflow.py`, where `<skills-root>` means the selected host's skills root.

### Custom target and verification

Override a host default with `--target`; use the same host, target, and selection when verifying:

```bash
python scripts/install_skills.py --host codex --target <skills-root>
python scripts/install_skills.py --host codex --target <skills-root> --check
python scripts/install_skills.py --workflow --host claude --target <skills-root> --check
```

If `--check` reports `missing`, `different`, or stale tracked files, rerun the installer with the same selection. `--check` only inspects files; it does not copy them.

### Update and cleanup

From a local clone:

```bash
git pull --ff-only
python scripts/install_skills.py --host codex
python scripts/install_skills.py --host codex --check
```

To remove only old files that the install manifest identifies as owned by this repository and that have not been modified by the user, explicitly add `--prune`:

```bash
python scripts/install_skills.py --host codex --prune
python scripts/install_skills.py --workflow --host codex --prune
```

`--prune` never removes unrelated skills or user-modified tracked files. Review its output before choosing it.

### Optional Python dependencies and troubleshooting

Installing skills needs no third-party Python packages. Install runtime dependencies only before using figure, PDF, corpus, or evidence helper scripts:

```bash
python -m pip install -r requirements.txt
```

Contributors can install the separate lint dependency:

```bash
python -m pip install -r requirements-dev.txt
```

If a host does not trigger an installed skill, start a fresh session, run `--check` with the same host and selection, confirm that the target contains the chosen `top-cs-*`, `_shared`, and `_shared/evidence/derived` folders, then use a clearly matching task or name the skill explicitly.
