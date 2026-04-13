# Benchmark Results Index

## Purpose

This page is the single entry point for the current PharmacoProfiler benchmark evidence package. It organizes the verified outputs by question so the manuscript and reviewer-response files can cite canonical artifacts instead of scattered notes.

## Core cross-domain baseline

Use these artifacts for the reconstructed GDSC-to-CCLE baseline:

- `models/evaluation/legacy_pic50_baseline/benchmark_summary.json`
- `models/evaluation/legacy_pic50_baseline/metrics.tsv`
- `docs/research/supplementary/benchmark-reproducibility-baseline.md`
- `docs/research/supplementary/benchmark-baseline-interpretation.md`

Current code-backed baseline:

- rows: `6513`
- drugs: `16`
- cell lines: `434`
- Pearson `r`: `0.7556`
- Spearman `r`: `0.6273`
- MAE: `0.6548`
- RMSE: `0.8361`
- `R²`: `0.2633`

## Calibration, subgroup, and failure analysis

Use these artifacts when the manuscript needs limitation framing:

- `docs/research/supplementary/benchmark-subgroup-analysis.md`
- `models/evaluation/legacy_pic50_baseline/subgroup_analysis_summary.json`
- `models/evaluation/legacy_pic50_baseline/potency_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/top_error_examples.tsv`

Key messages:

- strong underprediction bias
- compressed calibration slope
- worsening error in higher-pIC50 regions
- non-uniform tissue and compound behavior

## Uncertainty and applicability

Use these artifacts for supplementary reliability framing:

- `docs/research/supplementary/uncertainty-applicability-analysis.md`
- `models/evaluation/legacy_pic50_baseline/uncertainty_applicability_summary.json`
- `models/evaluation/legacy_pic50_baseline/uncertainty_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/applicability_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/interval_calibration_metrics.tsv`

Current message:

- uncertainty signal exists but is under-calibrated
- interval under-coverage is visible across nominal coverage levels, not only at the 90% interval
- first-pass applicability proxy is weaker than the uncertainty signal

## Mechanism-aware annotation

Use these artifacts when the manuscript needs biological context without overclaiming mechanistic learning:

- `docs/research/supplementary/mechanism-aware-analysis.md`
- `models/evaluation/legacy_pic50_baseline/mechanism_annotated_drug_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/mechanism_class_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/mechanism_analysis_summary.json`

Current message:

- the preserved overlap set spans multiple broad mechanism classes
- this is an interpretation layer, not proof of mechanistic learning

## Leakage-safe staged ridge comparison

Use these artifacts for the split-policy generalization story:

- `models/evaluation/leakage_safe_regimes/ridge_regime_comparison.tsv`
- `docs/research/supplementary/leakage-safe-benchmark-results.md`
- `docs/research/supplementary/leakage-safe-ridge-regime-table.md`
- `docs/research/supplementary/leakage-safe-model-comparison-shell.md`
- `docs/research/supplementary/leakage-safe-multi-model-regime-table.md`
- `models/evaluation/leakage_safe_regimes/multi_model_regime_comparison.tsv`
- `models/evaluation/leakage_safe_regimes/multi_model_regime_status.json`

Current staged `ridge` results:

| Regime | MAE | RMSE | Pearson r | Spearman r | R^2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `pair_random` | 0.4056 | 0.5428 | 0.8818 | 0.8564 | 0.7775 |
| `cell_line_holdout` | 0.4767 | 0.6267 | 0.8402 | 0.8022 | 0.7033 |
| `compound_holdout` | 0.9037 | 1.1523 | 0.4115 | 0.3778 | -0.0353 |
| `double_cold_start` | 0.9363 | 1.1923 | 0.3682 | 0.3319 | -0.1093 |

Current message:

- unseen-cell-line generalization is materially stronger than unseen-compound generalization
- row-random performance should not be presented as a strong unseen-drug result
- the completed `ridge` and `ols` sweeps are effectively indistinguishable across the four saved regimes
- the current canonical leakage-safe evidence now supports a completed two-model comparison
- the legacy RF comparator remains pending because the attempted `rf_pair_random` run produced no result files

## Figure entry points

Use these files for manuscript-ready figures and captions:

- `docs/research/figures/figure_legends_and_mapping.md`
- `docs/research/figures/primary-figure-captions.md`
- `docs/research/figures/benchmark_figure_set_note.md`

Primary current figure set:

1. Figure 1: legacy benchmark overview
2. Figure 5: calibration detail
3. Figure 6: subgroup variability
4. Figure 11: leakage-safe regime comparison
5. Figure 12: leakage-safe multi-model comparison
6. Figure 7: competitive positioning comparison

## Recommended manuscript-use rule

When a benchmark number is used in the manuscript, cite it from the smallest canonical layer that supports the claim:

1. generated metric file or comparison TSV
2. benchmark-support note that interprets it
3. figure legend or caption file that places it in manuscript context
