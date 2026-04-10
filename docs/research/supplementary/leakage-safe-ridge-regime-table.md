# Leakage-Safe Ridge Regime Table

## Purpose

This table is the manuscript-ready supplementary tabular counterpart to Figure 11. It provides a compact comparison of the completed staged `ridge` runs across the saved leakage-sensitive GDSC split regimes.

## Supplementary Table

| Regime | Meaning | Folds | Test rows | MAE | RMSE | Pearson r | Spearman r | R^2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `pair_random` | permissive row-random comparator | 5 | 337,761 | 0.4056 | 0.5428 | 0.8818 | 0.8564 | 0.7775 |
| `cell_line_holdout` | unseen-cell-line generalization | 5 | 337,761 | 0.4767 | 0.6267 | 0.8402 | 0.8022 | 0.7033 |
| `compound_holdout` | unseen-drug generalization | 5 | 337,761 | 0.9037 | 1.1523 | 0.4115 | 0.3778 | -0.0353 |
| `double_cold_start` | unseen drug and unseen cell line in same fold | 5 | 67,675 | 0.9363 | 1.1923 | 0.3682 | 0.3319 | -0.1093 |

## Interpretation note

This table should be cited together with Figure 11 when the manuscript needs an explicit leakage-sensitive comparison across split regimes. The main scientific message is that the preserved baseline retains strong performance under permissive row-random and unseen-cell-line splits, but degrades sharply when compounds are held out and remains weakest under the double-cold-start design.

## Canonical source

- `models/evaluation/leakage_safe_regimes/ridge_regime_comparison.tsv`
