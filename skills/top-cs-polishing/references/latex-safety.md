# LaTeX-safe revision

Protect commands, braces, environments, citation keys, cross-references, labels, math delimiters, comments, and custom macros. Edit prose inside arguments only when their syntax is understood. Do not rename labels or citation keys. After large edits, check balanced braces, environment pairs, escaped characters, and references to moved figures or sections.

For a supplied multi-file project, run `scripts/check_latex_project.py --project <dir> --root <main.tex> --format json`. The checker compiles twice in a temporary output directory, disables shell escape, leaves the project unchanged, and reports undefined citations/references, LaTeX errors, overfull boxes, and engine availability. Report `compiled` only when the checker succeeds; otherwise use `not-compiled` or `compile-failed` with the returned reason.
