# Method Schematic Grammar

A schematic is a rendering of explicitly supplied method structure. It is not a mechanism generator.

## Vocabulary

- **lane:** a horizontal responsibility or stage band;
- **group:** a dashed or bounded subsystem region;
- **node:** a declared component with stable ID and manuscript label;
- **port:** a named connection point used for audit, even when v4 drawing uses node bounds;
- **edge:** a declared directed relation;
- **shape label:** tensor, data, or interface shape shown under the node term.

Node kinds are input, process, data, and output. Shapes are box, pill, and circle. Use shape consistently: data objects should not change shape across panels. Coordinates are normalized to the panel in `[0,1]`.

## Edge routing

Use straight edges for simple left-to-right flow. Use orthogonal routing when lanes or groups would otherwise be crossed. Labels name transported data or an explicit operation. Do not label an edge with a causal claim absent from the manuscript.

## Terminology preservation

Every visible component term must come from the spec or terminology ledger. Preserve capitalization, abbreviations, hyphenation, tensor symbols, and stage names. Revisions may move or restyle a node without silently renaming it.

## Layout sequence

1. Place lanes and groups as background structure.
2. Place nodes with enough width for the longest declared term at 6 pt or larger.
3. Route primary data flow first, then controls or skip connections.
4. Add shape labels and edge labels.
5. Check crossings, term wrapping, group containment, and reading order.

Reject missing node IDs, duplicate IDs, undeclared edge endpoints, inferred components, or unexplained terminology changes.
