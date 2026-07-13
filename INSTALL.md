# Top CS Paper Skills Installation Guide

[中文](#中文安装) · [English](#english-installation)

## 中文安装

`top-cs-paper-skills` 不是 Python 包。每个 `skills/top-cs-*` 目录都是一个完整技能，运行时还会读取相邻的 `skills/_shared/` 和派生 evidence。请安装完整目录，不要只复制 `SKILL.md`。

### 推荐：让 Codex 安装

把下面的提示词发给 Codex：

```text
请从这个仓库安装全部 Codex skills：
https://github.com/zhiming33416/top-cs-paper-skills.git

请 clone 仓库并运行 python scripts/install_skills.py。
安装后运行 python scripts/install_skills.py --check 验证。
请保留 skills/top-cs-* 的完整目录、skills/_shared 和派生 evidence，
不要只复制 SKILL.md。完成后提醒我开启新的 Codex 会话。
```

Codex 可能会请求网络访问和写入 `~/.codex/skills` 的权限。安装完成后开启新的会话，以便重新发现技能。

### Windows 手动安装

```powershell
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
Set-Location top-cs-paper-skills
py scripts/install_skills.py
py scripts/install_skills.py --check
```

如果 `py` 不可用，请将命令替换为 `python`。

### macOS / Linux 手动安装

```bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python3 scripts/install_skills.py
python3 scripts/install_skills.py --check
```

### 选择技能

查看可安装技能：

```bash
python scripts/install_skills.py --list
```

只安装一个技能：

```bash
python scripts/install_skills.py --skill top-cs-writing
```

安装多个技能：

```bash
python scripts/install_skills.py --skill top-cs-writing --skill top-cs-figure
```

无论选择几个技能，安装器都会同步 `_shared` 和 `evidence/derived`，以保持相对引用有效。

### 自定义安装位置

默认目标是 `~/.codex/skills`。如需其他位置：

```bash
python scripts/install_skills.py --target <codex-skills-dir>
python scripts/install_skills.py --target <codex-skills-dir> --check
```

### 更新

在本地 clone 中执行：

```bash
git pull --ff-only
python scripts/install_skills.py
python scripts/install_skills.py --check
```

安装器会更新本仓库拥有的技能文件，但不会删除目标目录中的其他 Codex skills。

### 可选 Python 依赖

仅安装技能不需要第三方 Python 包。运行图件、PDF、语料或 evidence 辅助脚本前安装：

```bash
python -m pip install -r requirements.txt
```

### 验证与排错

如果 Codex 没有触发技能：

1. 开启新的 Codex 会话。
2. 运行 `python scripts/install_skills.py --check`。
3. 确认目标目录同时包含所选 `top-cs-*`、`_shared` 和 `_shared/evidence/derived`。
4. 使用明确任务，或在提示词中直接写出技能名。

如果 `--check` 报告 `missing` 或 `different`，重新运行同一选择范围的安装命令。例如，单技能安装后应使用相同的 `--skill` 参数验证。

---

## English Installation

`top-cs-paper-skills` is not a Python package. Each `skills/top-cs-*` directory is a complete skill that also reads sibling resources from `skills/_shared/` and derived evidence. Install complete directories rather than copying only `SKILL.md`.

### Recommended: ask Codex to install

Send Codex this prompt:

```text
Install all Codex skills from this repository:
https://github.com/zhiming33416/top-cs-paper-skills.git

Clone the repository and run python scripts/install_skills.py.
Then run python scripts/install_skills.py --check to verify the installation.
Preserve the complete skills/top-cs-* folders, skills/_shared, and derived evidence;
do not copy only SKILL.md. Remind me to start a new Codex session when finished.
```

Codex may request network access and permission to write to `~/.codex/skills`. Start a fresh session after installation so the skills are discovered again.

### Windows manual installation

```powershell
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
Set-Location top-cs-paper-skills
py scripts/install_skills.py
py scripts/install_skills.py --check
```

Replace `py` with `python` if the Python launcher is unavailable.

### macOS / Linux manual installation

```bash
git clone https://github.com/zhiming33416/top-cs-paper-skills.git
cd top-cs-paper-skills
python3 scripts/install_skills.py
python3 scripts/install_skills.py --check
```

### Select skills

List available skills:

```bash
python scripts/install_skills.py --list
```

Install one skill:

```bash
python scripts/install_skills.py --skill top-cs-writing
```

Install several skills:

```bash
python scripts/install_skills.py --skill top-cs-writing --skill top-cs-figure
```

The installer always synchronizes `_shared` and `evidence/derived`, regardless of how many skills are selected.

### Custom target

The default target is `~/.codex/skills`. To use another directory:

```bash
python scripts/install_skills.py --target <codex-skills-dir>
python scripts/install_skills.py --target <codex-skills-dir> --check
```

### Update

From the local clone:

```bash
git pull --ff-only
python scripts/install_skills.py
python scripts/install_skills.py --check
```

The installer updates files owned by this repository without deleting unrelated Codex skills in the target directory.

### Optional Python dependencies

Installing the skills requires only the Python standard library. Before running figure, PDF, corpus, or evidence helper scripts, install:

```bash
python -m pip install -r requirements.txt
```

### Verification and troubleshooting

If Codex does not trigger an installed skill:

1. Start a fresh Codex session.
2. Run `python scripts/install_skills.py --check`.
3. Confirm that the target contains the selected `top-cs-*` folders, `_shared`, and `_shared/evidence/derived`.
4. Use a clearly matching task or name the skill explicitly in the prompt.

If `--check` reports `missing` or `different`, rerun the installer with the same selection. A single-skill installation should be checked with the same `--skill` argument.
