# LaTeX layout diagnosis and repair

Provenance: safe compilation rules are `conservative-implementation`; venue limits are `official-policy` only through the selected profile.

## Diagnosis workflow

1. Locate the root document, engine, class, column mode, and relevant packages.
2. Run `scripts/check_latex_project.py` and compile into an isolated temporary directory without shell escape.
3. Read overfull/underfull box warnings, oversized floats, unresolved references, and float-placement warnings.
4. Render affected pages and make a contact sheet when several pages interact.
5. Classify the defect before editing: source geometry, float backlog, forced placement, page break, caption/panel size, or text overflow.
6. Apply the smallest local change, rebuild, and compare the same pages.
7. Report affected pages, source edits, warnings changed, and remaining uncertainty.

## Repair priority

Prefer: source figure geometry -> panel arrangement -> normal float placement -> local barriers -> forced breaks -> small local spacing. Avoid global negative spacing and class-level changes as first-line fixes.

## Wide and shallow figures

A very wide, shallow raster or PDF cannot fill a portrait page without excessive whitespace. Regenerate at a taller aspect ratio when possible; do not merely scale beyond the text width. For a two-column paper, compare:

```tex
\begin{figure}[t]
  \centering
  \includegraphics[width=\columnwidth]{figure}
  \caption{...}
  \label{fig:...}
\end{figure}
```

with a genuine two-column composition:

```tex
\begin{figure*}[t]
  \centering
  \includegraphics[width=\textwidth]{figure}
  \caption{...}
  \label{fig:...}
\end{figure*}
```

Use `figure*` only when the information density and legibility require it.

## Float backlog and stranded headings

Repeated floats can push a section heading to the bottom of a page while its text moves forward. First reduce or reorder the backlog and verify float sizes. Use a local barrier only at a genuine semantic boundary:

```tex
\usepackage[section]{placeins} % only when compatible with the template
% or a local \FloatBarrier at a verified boundary
```

Do not scatter `\FloatBarrier` after every figure; it can create sparse pages and violate intended float behavior.

## Forced placement

`[H]` removes most of LaTeX's ability to compose the page. Replace it with `[t]`, `[tbp]`, or template defaults unless exact placement is required and verified. Remove unnecessary `\clearpage` and `\newpage` before tuning spacing.

## Multi-panel figures

Preserve reading order, common scales, panel labels, and caption mapping. Stack panels when side-by-side placement makes text illegible. Crop excess whitespace at the source rather than with undocumented clipping. Keep important labels readable at final print size.

## Tables

Before shrinking text, reduce redundant columns, shorten headers with defined abbreviations, use `tabularx` or `p{}` widths carefully, and consider moving secondary detail when venue policy permits. Never scale a table until numbers or labels become unreadable.

## Overfull text

Find the exact token: URL, equation, inline code, compound identifier, or unbreakable table cell. Prefer semantic breaks, display equations, `\url{}`, or local formatting. Do not solve global overflow by reducing all font sizes or margins.

## Safety boundaries

- Preserve the official class and margins.
- Do not hide text or decisive evidence.
- Do not move central evidence into optional material solely for appearance.
- Do not enable shell escape.
- Do not write build artifacts into the source project.
- Never claim success without compiling and visually inspecting affected pages.

## Verification report

Record root file, engine, compile command, output directory, affected pages, warnings before/after, rendered-page observation, source change, and unresolved layout risk.
