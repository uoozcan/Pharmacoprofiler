# Benchmark Figure Set

## Included figures

- `legacy_benchmark_overview.(png|svg)`: four-panel summary of the canonical GDSC-to-CCLE legacy baseline
- `legacy_benchmark_drug_mae.(png|svg)`: compound-level MAE ranking across the preserved overlap set
- `legacy_benchmark_confidence_intervals.(png|svg)`: bootstrap 95% confidence intervals for the core benchmark metrics
- `legacy_benchmark_top_errors.(png|svg)`: largest failure cases across the preserved CCLE overlap set
- `legacy_benchmark_calibration.(png|svg)`: detailed calibration view with observed-decile residual structure
- `legacy_benchmark_subgroup_variability.(png|svg)`: tissue-level error and drug-level bias summary
- `legacy_benchmark_leakage_safe_regimes.(png|svg)`: staged ridge comparison across pair-random, cell-line-holdout, compound-holdout, and double-cold-start regimes
- `legacy_benchmark_leakage_safe_multi_model.(png|svg)`: completed ridge-versus-OLS comparison across the four saved leakage-safe regimes
- `platform_positioning_comparison.(png|svg)`: strategic positioning heatmap derived from the verified competitive analysis

## Figure-safe messages

- The legacy baseline shows strong correlation but incomplete explanatory strength: Pearson `r = 0.756`, Spearman `r = 0.627`, and `R² = 0.263`.
- Errors are systematically left-shifted, with mean signed error `-0.494` and underprediction in `85.0%` of benchmark rows.
- Calibration is compressed rather than ideal, with fitted slope `0.740` and intercept `1.007`.
- Error worsens at higher observed pIC50 values, which should be framed as a key limitation rather than hidden in aggregate metrics.
- The completed `ridge` and `ols` leakage-safe sweeps are effectively indistinguishable, which strengthens the split-policy interpretation by showing that it is not tied to one lightweight baseline family.

## Canonical artifact source

All values and plots in this figure set are generated directly from `models/evaluation/legacy_pic50_baseline/`.
