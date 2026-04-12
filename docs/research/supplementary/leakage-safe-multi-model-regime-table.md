# Leakage-Safe Multi-Model Regime Table

## Purpose

This table is the manuscript-ready supplementary tabular counterpart to the completed multi-model leakage-safe comparison figure. It compares the finished `ridge` and `ols` sweeps across the four saved GDSC split regimes.

## Supplementary Table

| Model | Regime | Folds | Test rows | MAE | RMSE | Pearson r | Spearman r | R^2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `ridge` | `pair_random` | 5 | 337,761 | 0.4056 | 0.5428 | 0.8818 | 0.8564 | 0.7775 |
| `ols` | `pair_random` | 5 | 337,761 | 0.4056 | 0.5428 | 0.8818 | 0.8564 | 0.7775 |
| `ridge` | `cell_line_holdout` | 5 | 337,761 | 0.4767 | 0.6267 | 0.8402 | 0.8022 | 0.7033 |
| `ols` | `cell_line_holdout` | 5 | 337,761 | 0.4770 | 0.6272 | 0.8400 | 0.8019 | 0.7028 |
| `ridge` | `compound_holdout` | 5 | 337,761 | 0.9037 | 1.1523 | 0.4115 | 0.3778 | -0.0353 |
| `ols` | `compound_holdout` | 5 | 337,761 | 0.9038 | 1.1524 | 0.4115 | 0.3778 | -0.0355 |
| `ridge` | `double_cold_start` | 5 | 67,675 | 0.9363 | 1.1923 | 0.3682 | 0.3319 | -0.1093 |
| `ols` | `double_cold_start` | 5 | 67,675 | 0.9364 | 1.1925 | 0.3680 | 0.3318 | -0.1095 |

## Interpretation note

This table shows that the completed `ridge` and `ols` leakage-safe sweeps are effectively indistinguishable across all four saved regimes. That strengthens the current benchmark interpretation because the main leakage-sensitive pattern is no longer tied to one lightweight baseline choice.

## Canonical source

- `models/evaluation/leakage_safe_regimes/multi_model_regime_comparison.tsv`
