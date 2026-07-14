# Tests / 测试

This directory is versioned on purpose: it is the public, reproducible quality gate used by GitHub Actions and contributors. The Codex installer copies only `skills/` and `evidence/derived/`; it never installs `tests/` into a user's skills directory.

本目录用于公开、可复现的质量验证。GitHub Actions 和贡献者会运行这些测试；Codex 安装器不会将 `tests/` 复制到用户的技能目录。

## Layout

- `test_*.py` — unit, architecture, public-release, and acceptance tests.
- `cases/` — executable public case matrices for skill outputs and figure evaluations.
- `fixtures/` — small synthetic inputs, including figure specs, CSV data, LaTeX samples, and mock public records.

## Privacy boundary

No private manuscript, reviewer correspondence, credential, raw corpus PDF, or user artifact belongs here. The name `synthetic-regression-suite.yaml` is intentional: it contains aggregate-only synthetic checks. Any future private regression material must stay under `tests/private-eval/`, which is ignored by Git, and must not be referenced by public CI.

Run the complete public suite with the commands in the [development guide](../docs/DEVELOPMENT.md).
