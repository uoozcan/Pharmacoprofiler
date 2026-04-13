# Supplementary Leakage-Safe Figure and Table Captions

## Purpose

This file provides compact caption text for the leakage-safe benchmark figure and table set. It is intended for manuscript assembly when a short caption reference is more useful than the full legend-and-mapping document.

## Figure 11

**Figure 11. Leakage-sensitive performance differences across the staged ridge benchmark regimes.** MAE, RMSE, Pearson correlation, and `R²` are compared across pair-random, cell-line-holdout, compound-holdout, and double-cold-start split policies for the completed `ridge` sweep. The figure shows that the current baseline remains materially stronger for unseen cell lines than for unseen compounds, and that double cold start is the strictest and weakest regime.

## Figure 12

**Figure 12. Leakage-safe multi-model comparison across completed benchmark regimes.** MAE and `R²` are compared across the four saved split regimes for the completed `ridge` and `ols` sweeps. The two lightweight baselines are effectively indistinguishable across all four settings, showing that the main leakage-sensitive generalization pattern is stable across both comparator families.

## Supplementary Table: Leakage-safe ridge regime table

**Supplementary Table. Leakage-safe ridge benchmark across saved split regimes.** The table reports folds, test-row counts, and core performance metrics for the completed `ridge` sweep under pair-random, cell-line-holdout, compound-holdout, and double-cold-start evaluation. It should be cited with Figure 11 when exact regime values are needed.

## Supplementary Table: Leakage-safe multi-model regime table

**Supplementary Table. Leakage-safe ridge-versus-OLS comparison across saved split regimes.** The table reports the same core metrics for the completed `ridge` and `ols` sweeps and shows that the two baselines are numerically near-identical across all four regimes. It should be cited with Figure 12 when exact comparator values are needed.
