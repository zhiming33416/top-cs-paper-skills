# Full-section corpus patterns

Use these rules to choose section structure, not to imitate source wording. Evidence comes from the 90-paper primary corpus and is recorded with source IDs in `_shared/evidence/derived/full-section-rules.yaml` after installation.

## Method

Method-family headings were detected in 53/90 sources (ICLR 20, ICML 17, WWW 16). Headings vary across venues and paper types. Require the problem setting, assumptions, mechanism, objective or procedure, and computational implications without forcing a universal heading. Load the selected paper-type overlay before deciding the order.

## Experiments

Experimental or evaluation sections were detected in 73/90 sources (ICLR 28, ICML 21, WWW 24). For empirical claims, organize evidence by research question, protocol, comparator, metric, result, interpretation, and boundary. Do not impose an experiments section on a purely theoretical contribution.

## Discussion

Dedicated discussion headings were detected in only 7/90 sources (ICLR 1, ICML 4, WWW 2). Integrated discussion is acceptable, but observation, explanation, implication, negative evidence, and uncertainty must remain distinguishable.

## Limitations

Dedicated limitations headings were detected in only 8/90 sources (ICLR 4, ICML 4, WWW 0). This does not make limitations optional. State concrete boundaries where the claim, ethics, or venue policy requires them, whether in a standalone section or integrated discussion.

## Conclusion

Conclusion sections were detected in 77/90 sources (ICLR 26, ICML 26, WWW 25). When present, synthesize the supported contribution, decisive evidence, and boundary. Do not introduce new claims, evidence, mechanisms, or citations.

All heading counts are detection-based structural evidence. PDF extraction can miss custom headings; inspect `heading_detection_confidence` before treating absence as meaningful.
