# Qualitative Image Integrity

Qualitative panels can be persuasive while hiding selection, crop, or scale decisions. Make those decisions explicit and machine-checkable.

## Required row fields

- stable image ID;
- source path outside the installed skill;
- crop provenance such as uncropped or declared coordinates;
- expected aspect ratio;
- method/case label;
- scale-bar metadata when physical size is interpreted.

Validate that every file exists, is decodable, and matches the declared aspect ratio within tolerance. Preserve row order from the source table. Do not silently rotate, stretch, recolor, denoise, or substitute images. If uniform crops are necessary, record the operation before rendering.

The caption states case-selection policy, whether examples are typical or selected failures, image IDs, methods, crop policy, and scale. A layout mockup must use clearly synthetic placeholders and cannot be delivered as experimental evidence.
