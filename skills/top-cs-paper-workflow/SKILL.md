---
name: top-cs-paper-workflow
description: Coordinate a complete evidence-grounded CS paper project across the five Top CS skills. Use when work spans contribution planning, evidence and figure handoff, manuscript revision, pre-submission review, or reviewer response and needs resumable project status. Do not use for a single writing, polishing, review, response, or figure task.
---

# Top CS Paper Workflow

Coordinate work; do not replace the five specialist skills. Use this skill only when the user wants a project-level view or to resume a multi-stage paper workflow.

## Start safely

1. Ask for the paper project root. Never search the home directory, cloud folders, or other projects.
2. Initialize the project-local state only after the user has chosen that root:

   ```text
   python scripts/paper_workflow.py init --project <project-root>
   ```

3. The tool writes only `<project-root>/.top-cs-paper/workflow.yaml`. It stores structured IDs, relative file paths, file metadata, and SHA-256 hashes; it never copies manuscript, PDF, data, reviewer text, or citation content.
4. Use `inventory` only with explicit relative `--include` paths. Do not infer that every file in a project is in scope.

## Coordinate the five skills

Follow this order when the relevant stage applies. A stage may be marked `not-applicable`; do not invent missing work to make it pass.

| Stage | Owner | Required handoff |
| --- | --- | --- |
| Contribution and argument | `top-cs-writing` | claim IDs, evidence needs, manuscript plan |
| Evidence and figures | `top-cs-figure` | figure briefs linked to claims and evidence |
| Manuscript refinement | `top-cs-polishing` | terminology and revision notes |
| Pre-submission risk audit | `top-cs-reviewer` | review issues, threatened claims, proposed actions |
| Response and verified change | `top-cs-response` | revision IDs linked back to review issues |

`top-cs-figure` is the only renderer. This workflow may request or validate a figure handoff, but never renders a figure itself.

## Record only traceability

Use `workflow-manifest.schema.yaml` and `references/handoff-and-checkpoints.md` as the project contract. Maintain stable IDs and links:

```text
claim -> evidence -> figure
claim -> review issue -> revision
```

Expected observations, planned figures, and unresolved reviewer issues are not completed results. Preserve those states explicitly.

## Check status

```text
python scripts/paper_workflow.py inventory --project <project-root> --include paper/main.tex
python scripts/paper_workflow.py status --project <project-root>
python scripts/paper_workflow.py status --project <project-root> --format json --strict
```

Normal status output is advisory and exits successfully when the manifest is structurally valid. `--strict` exits non-zero for incomplete checkpoints, missing links, unverified evidence, or pending author confirmation. It does not claim that a paper is accepted or technically correct.

## Boundaries

- Do not fabricate experiments, figures, citations, reviewer comments, venue rules, or completion evidence.
- Keep all tracked paths project-relative and inside the chosen project root. Reject absolute paths, traversal, missing files, and escaping symlinks.
- Use current official venue sources through the specialist skills; a workflow status is not a policy source.
- Do not overwrite an existing manifest without the user's explicit `--force` request.

## Resources

- `scripts/paper_workflow.py`: initialize, inventory explicitly selected files, and inspect project traceability.
- `references/handoff-and-checkpoints.md`: checkpoint meanings and cross-skill handoff rules.
- `../_shared/contracts/workflow-manifest.schema.yaml`: public schema for the project state file.
