# Evidence and Provenance

The repository separates official venue policy, corpus-derived observations, author-provided artifacts, and conservative implementation choices. A corpus pattern is never promoted into an official requirement.

## Current public snapshot

- 100 indexed public PDF files with 99 unique hashes.
- 90 eligible main-track papers: 30 each from ICLR, ICML, and WWW Research.
- 25 historical public ICLR processes providing 94 reviews and 32 discussion threads for review and response behavior patterns.
- 30 verified independent visual-style sources for each of WWW Research, ICLR, and ICML in the 2026-07-13 snapshot.

These counts describe the checked-in snapshot. They do not promise that a future venue edition uses the same policy, format, or style.

## What is stored

`evidence/derived/` contains portable source metadata, hashes, aggregate statistics, policy matrices, structural rules, and confidence labels. The installer copies these files into `_shared/evidence/derived` so installed skills can resolve them without access to the original corpus.

The repository does not store:

- raw paper or review full text;
- paper screenshots, figure crops, or page images;
- private manuscript content, user data, or experiment results;
- resolver caches or downloaded corpus PDFs;
- private regression specifications or rendered private artifacts.

The optional full-paper workflow writes a local manifest only beneath a user-selected project's `.top-cs-paper/` directory. That manifest may contain relative paths, file metadata, hashes, stable IDs, and checkpoint states, but it is not evidence by itself and must not be committed as a user artifact.

The repository's MIT license covers its original code, documentation, and deterministic synthetic assets. It does not relicense linked conference websites, papers, templates, or third-party material.

## Rule labels

- `official-policy`: a dated venue rule backed by an official source;
- `corpus-derived`: an aggregate observation from eligible public material;
- `author-artifact`: a fact supplied by the user and preserved as evidence;
- `conservative-implementation`: a repository behavior chosen to avoid overclaiming;
- `synthetic-example`: deterministic test or demonstration data;
- `workflow-inspiration`: an external workflow used only as design inspiration.

Official policy must be revalidated against the current venue website before submission. Corpus-derived guidance must remain qualified and cannot establish page limits, anonymity requirements, or acceptance advice.

## Figure evidence

Visual-style evidence records aggregate color, layout, and co-occurrence statistics. Observed anchors, accessibility-constrained constructed tokens, and generic fallbacks remain distinguishable in render manifests. The checked-in atlas and gallery use deterministic synthetic CSV, YAML, and image inputs; their manifest records generators, hashes, venues, panel counts, and outputs.

## Privacy and integrity

Citation verification checks public metadata but does not treat metadata existence as proof that a source entails a manuscript claim. Review and response workflows do not invent reviewer identities, experiments, results, edits, or promises. Workflow status does not establish that an experiment ran, a figure is valid, a citation entails a claim, or a venue policy is current. Private regression runs emit only aggregate identifiers, hashes, geometry, perceptual distance, scores, and error categories.
