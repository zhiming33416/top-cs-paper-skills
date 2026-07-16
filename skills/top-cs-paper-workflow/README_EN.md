# Top CS Paper Workflow

[中文说明](README.md)

An optional project coordinator that records handoffs among the five specialist skills in a user-selected paper project without collapsing them into one large skill.

## Tasks

Use it for a full paper, cross-skill revision, pre-submission checking, or reviewer response that needs resumable project state. Use the specialist skill directly for one-off writing, polishing, reviewing, response, or figure work.

## Example Request

“Create resumable claim–evidence–figure handoff state for this paper project and tell me which specialist skill should run next.”

## Inputs

A user-selected `<project-root>` and optional relative material paths. `inventory` processes only explicitly supplied `--include` files.

## Outputs

`<project-root>/.top-cs-paper/workflow.yaml`, relative-path and SHA-256 metadata for selected materials, and a Markdown or JSON status report.

## Workflow and Dependencies

The coordinator orders contribution and argument work → figure evidence handoff → polishing → pre-submission review → response and revision. It depends on, and preserves the independent responsibilities of, `top-cs-writing`, `top-cs-polishing`, `top-cs-reviewer`, `top-cs-response`, and `top-cs-figure`.

## Invocation

Invoke the installed skill in any supported host, or run its script:

```text
python <installed-skill>/scripts/paper_workflow.py init --project <project-root>
python <installed-skill>/scripts/paper_workflow.py status --project <project-root> --strict
```

## Boundaries and Dependency

Requires Python and PyYAML. The tool never copies manuscript, PDF, data, reviewer, or citation content; it rejects absolute paths, traversal, and symlinks that escape the project root. `--strict` checks workflow closure only—it does not validate experiments, policy, or submission outcomes.
