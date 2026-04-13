# Uncertainty and Applicability Analysis

## Purpose

This note records the uncertainty-focused extension of the canonical legacy GDSC-to-CCLE benchmark. It now includes both the original ensemble-spread diagnostics and a stricter OOB-based split-conformal calibration pass. It is intended as a manuscript-support artifact rather than as a final deployment claim. For the current manuscript-safe and product-safe claim boundary, see `uncertainty-boundary.md`.

## Analysis scope

The current analysis reuses the verified legacy Random Forest baseline and the reconstructed CCLE benchmark set:

- train domain: GDSC
- external test domain: reconstructed CCLE
- rows evaluated: `6513`
- overlapping drugs: `16`
- overlapping cell lines: `434`

The analysis adds two first-pass quantities:

1. `prediction_std`: per-sample standard deviation across the fitted decision trees in the deployed Random Forest.
2. `nearest_train_cosine`: the maximum cosine similarity between each CCLE cell-line omics vector and the GDSC training cell-line omics matrix.

These should be framed as internal uncertainty and applicability proxies, not yet as clinically calibrated uncertainty estimates.

## Canonical outputs

Generated outputs are stored under `models/evaluation/legacy_pic50_baseline/`:

- `ccle_predictions_with_uncertainty.tsv`
- `ccle_predictions_with_calibrated_uncertainty.tsv`
- `uncertainty_bin_metrics.tsv`
- `applicability_bin_metrics.tsv`
- `cell_line_applicability_metrics.tsv`
- `interval_calibration_metrics.tsv`
- `conformal_interval_calibration_metrics.tsv`
- `conformal_subgroup_interval_metrics.tsv`
- `uncertainty_applicability_summary.json`
- `uncertainty_calibration_summary.json`

Generated figure assets are stored under `docs/research/figures/`:

- `legacy_benchmark_uncertainty.(png|svg)`
- `legacy_benchmark_applicability.(png|svg)`
- `legacy_benchmark_uncertainty_calibration.(png|svg)`
- `uncertainty_figure_set_note.md`

## Current findings

### Ensemble-spread uncertainty

The preserved Random Forest exposes a usable internal uncertainty proxy through per-tree prediction spread:

- mean prediction standard deviation: `0.6032`
- median prediction standard deviation: `0.5793`
- Pearson correlation between prediction standard deviation and absolute error: `0.2273`

Uncertainty bins are informative but imperfect. The highest-uncertainty quintile shows:

- mean prediction standard deviation: `0.9312`
- MAE: `0.8744`
- RMSE: `1.0696`
- mean signed error: `-0.5744`

This supports the manuscript-safe statement that larger ensemble spread is associated with larger benchmark error, while still leaving substantial unexplained error variation.

### Interval behavior

The current nominal 90% tree interval covers only `73.7%` of benchmark rows.

This means the raw tree-quantile interval is not yet suitable for strong probabilistic claims. In manuscript language, it should be described as an internal uncertainty heuristic that reveals miscalibration rather than as a calibrated predictive interval.

The broader interval-calibration curve shows that under-coverage is not confined to the 90% interval. Across nominal central coverage levels from `0.50` to `0.95`, empirical coverage remains systematically lower than nominal coverage, with gaps ranging from `-0.2293` at the 50% level to `-0.1358` at the 95% level. The mean nominal 90% interval width is `1.8878`.

A descriptive post hoc width-inflation calculation shows that the current 90% tree interval would need a global inflation factor of `1.5677` to achieve about `0.8999` empirical coverage on the same benchmark set. This is useful as a miscalibration diagnostic, but it should not be presented as a deployment-ready calibration method because it is estimated on the evaluated benchmark itself.

### Held-out split-conformal calibration

A stricter calibration pass was then added using a deterministic `10,000`-row GDSC reference partition and out-of-bag estimator membership reconstructed from the stored Random Forest bootstrap states. This produces a benchmark-backed split-conformal layer without calibrating on the evaluated CCLE rows themselves.

Key results from `uncertainty_calibration_summary.json`:

- raw nominal 90% coverage on CCLE: `0.7371`
- OOB split-conformal nominal 90% coverage on CCLE: `0.4849`
- raw mean 90% interval width: `1.8878`
- OOB split-conformal mean 90% interval width: `1.1182`
- mean out-of-bag estimators per calibration row: `36.747`

This is an important negative result. The held-out calibration workflow is real and reproducible, but it does not transfer adequately from the GDSC-side reference rows to the external CCLE benchmark. In practice, this means the current conformal layer sharpens the methodological story more than it solves the uncertainty problem.

### Applicability proxy

The current applicability proxy is weaker than the uncertainty signal but still directionally informative:

- Pearson correlation between nearest-train cosine similarity and cell-line MAE: `-0.0916`

The lowest-applicability quintile shows:

- mean nearest-train cosine similarity: `0.9296`
- MAE: `0.6766`
- mean prediction standard deviation: `0.6156`
- mean signed error: `-0.5233`

The effect is modest, so this proxy should currently be framed as a first-pass domain-shift indicator rather than as a strong standalone explanation of model failure.

## Manuscript-safe wording

`A first-pass uncertainty analysis showed that per-sample ensemble spread from the preserved Random Forest was positively associated with benchmark error, whereas nominal tree-based 90% intervals under-covered the reconstructed CCLE benchmark set. A stricter OOB-based split-conformal layer could also be built from a deterministic GDSC reference partition, but it still under-covered the external CCLE benchmark, indicating that cross-domain reliability remains a real limitation even after held-out calibration.`

`A calibration-focused follow-up showed that tree-quantile intervals under-covered the benchmark set across all evaluated nominal coverage levels, and that even the nominal 90% interval would require substantial post hoc width inflation to recover target coverage on the same benchmark set.`

`A simple applicability proxy based on nearest-train cell-line cosine similarity showed only a modest relationship with benchmark error, suggesting that domain-shift effects are present but not yet fully captured by this initial similarity-based analysis.`

## Next recommended uncertainty work

1. find a calibration strategy that improves external CCLE coverage, not only formal held-out calibration on GDSC-side rows
2. compare uncertainty performance across compounds, tissues, and high-response subsets
3. strengthen applicability-domain methods beyond nearest-neighbor cosine similarity alone
4. decide whether uncertainty fields should be added to the public API as additive metadata only after calibration is improved
