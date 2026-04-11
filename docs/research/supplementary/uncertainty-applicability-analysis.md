# Uncertainty and Applicability Analysis

## Purpose

This note records the first uncertainty-focused extension of the canonical legacy GDSC-to-CCLE benchmark. It is intended as a manuscript-support artifact rather than as a final methodological claim. For the current manuscript-safe and product-safe claim boundary, see `uncertainty-boundary.md`.

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
- `uncertainty_bin_metrics.tsv`
- `applicability_bin_metrics.tsv`
- `cell_line_applicability_metrics.tsv`
- `uncertainty_applicability_summary.json`

Generated figure assets are stored under `docs/research/figures/`:

- `legacy_benchmark_uncertainty.(png|svg)`
- `legacy_benchmark_applicability.(png|svg)`
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

`A first-pass uncertainty analysis showed that per-sample ensemble spread from the preserved Random Forest was positively associated with benchmark error, whereas nominal tree-based 90% intervals under-covered the reconstructed CCLE benchmark set, indicating that uncertainty estimates should be calibrated before being used for stronger predictive claims.`

`A simple applicability proxy based on nearest-train cell-line cosine similarity showed only a modest relationship with benchmark error, suggesting that domain-shift effects are present but not yet fully captured by this initial similarity-based analysis.`

## Next recommended uncertainty work

1. calibrate or post-process the tree-based intervals before exposing them as public prediction intervals
2. compare uncertainty performance across compounds, tissues, and high-response subsets
3. test stronger applicability-domain methods, such as conformal prediction or local-density-based scoring
4. decide whether uncertainty fields should be added to the public API as additive metadata only after calibration is improved
