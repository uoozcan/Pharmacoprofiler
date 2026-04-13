# Uncertainty and Applicability Boundary

## Purpose

This note defines the current manuscript-safe and product-safe boundary for PharmacoProfiler's uncertainty and applicability layer. It separates three things that should not be conflated:

1. uncertainty-related signals that are directly supported by the current benchmark outputs
2. exploratory reliability analyses, including a held-out split-conformal calibration workflow, that are useful for manuscript interpretation
3. stronger predictive-interval or applicability-domain claims that are not yet justified

## Verified current layer

The current uncertainty/applicability layer is built on top of the verified legacy Random Forest baseline and the reconstructed CCLE benchmark set.

The implemented quantities are:

- `prediction_std`: per-sample standard deviation across the fitted trees in the preserved Random Forest
- `nearest_train_cosine`: maximum cosine similarity between each CCLE cell-line vector and the GDSC training-cell omics matrix

The generated canonical outputs are:

- `models/evaluation/legacy_pic50_baseline/ccle_predictions_with_uncertainty.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_predictions_with_calibrated_uncertainty.tsv`
- `models/evaluation/legacy_pic50_baseline/uncertainty_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/applicability_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/cell_line_applicability_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/uncertainty_applicability_summary.json`
- `models/evaluation/legacy_pic50_baseline/conformal_interval_calibration_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/conformal_subgroup_interval_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/uncertainty_calibration_summary.json`

## What is supported

The current evidence supports the following statements:

1. the preserved Random Forest exposes an internal ensemble-spread signal that is positively associated with benchmark error
2. higher uncertainty bins show worse benchmark performance on average
3. the nominal tree-based 90% interval is under-calibrated on the reconstructed CCLE benchmark
4. the broader tree-quantile calibration curve also shows systematic under-coverage across evaluated nominal interval levels
5. an OOB-based split-conformal layer can be constructed from a deterministic GDSC reference partition, but it still under-covers the external CCLE benchmark
6. a simple nearest-train cell-line similarity proxy is directionally informative but weaker than the uncertainty signal

Current benchmark-backed values:

- mean prediction standard deviation: `0.6032`
- uncertainty versus absolute error Pearson correlation: `0.2273`
- nominal 90% interval coverage: `0.7371`
- nominal 90% interval coverage gap: `-0.1629`
- OOB split-conformal 90% interval coverage on CCLE: `0.4849`
- OOB split-conformal 90% interval coverage gap on CCLE: `-0.4151`
- post hoc 90% interval inflation factor on the same benchmark: `1.5677`
- nearest-train similarity versus cell-line MAE Pearson correlation: `-0.0916`

## What is not yet supported

The current layer should **not** yet be described as:

- deployment-ready calibrated predictive uncertainty
- valid prediction intervals for deployment or clinical decision support
- a finalized applicability-domain method
- sufficient on its own to justify public reliability claims at the API level

The current interval behavior is explicitly under-calibrated, and the similarity-based applicability proxy is only modestly informative. The repository now contains both the raw tree-spread layer and a stricter OOB-based split-conformal calibration workflow, but the calibrated intervals still do not transfer adequately to the external CCLE benchmark. These outputs should therefore still be treated as exploratory reliability analyses rather than as finished uncertainty methods.

## Product boundary

The current public service should remain conservative. Uncertainty-related fields such as:

- `prediction_interval`
- `prediction_interval_level`
- `uncertainty_method`
- `applicability_score`

should remain planned additive metadata rather than default public outputs until calibration is improved and the reliability layer is tested more rigorously.

## Manuscript-safe wording

Recommended wording:

> A first-pass uncertainty analysis showed that per-sample ensemble spread from the preserved Random Forest was positively associated with benchmark error, whereas nominal tree-based 90% intervals under-covered the reconstructed CCLE benchmark set. A stricter OOB-based split-conformal layer could also be built from a deterministic GDSC reference partition, but it still under-covered the external CCLE benchmark, indicating that benchmark-backed calibration alone does not yet close the present cross-domain reliability gap. A simple applicability proxy based on nearest-train cell-line cosine similarity was directionally informative but modest in effect size, supporting its use as an initial domain-shift indicator rather than as a final applicability-domain method.

## Next required upgrades

Before uncertainty or applicability should be promoted beyond manuscript-support status, the project needs:

1. a calibration strategy that materially improves external CCLE coverage rather than only formal held-out calibration on GDSC-side rows
2. subgroup-aware reliability checks across compounds, tissues, and high-response regions
3. stronger applicability-domain methods than nearest-neighbor cosine similarity alone
4. explicit validation of any API-level uncertainty fields under a locked benchmark protocol
