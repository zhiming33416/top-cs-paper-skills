# Figure brief and source data

figure_id: Figure 3
claim_ids: [C2]
research_question: Does GraphTune improve graph ranking accuracy on the supplied benchmark tasks?
purpose: comparison
data_sources: [results.csv]
manuscript_callout: "Figure 3 summarizes the main comparison. \\label{fig:graphtune-main}"

Panel map:
- a: grouped comparison across datasets
- b: ablation against the graph-aware loss

CSV:

dataset,method,accuracy
WebGraph-24,BaseRank,71.2
WebGraph-24,GraphTune,79.3
NewsGraph,BaseRank,68.4
NewsGraph,GraphTune,74.1

Caption draft: Figure 3. GraphTune comparison on WebGraph-24 and NewsGraph.
Evidence status: available; no p-values, confidence intervals, or seed counts supplied.
