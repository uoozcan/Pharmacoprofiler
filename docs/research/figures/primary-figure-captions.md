# Primary Figure Captions

## Purpose

This file provides compact manuscript-ready captions for the current recommended main-text figure set. It is intended for direct use during manuscript assembly after figure selection is finalized.

## Figure 1

**Figure 1. Overview of the verified legacy GDSC-to-CCLE benchmark baseline.** Predicted versus observed pIC50 values are shown for the reconstructed CCLE evaluation set together with potency-dependent error, tissue-level heterogeneity, and signed-error distribution. The current baseline retains cross-domain rank signal but shows incomplete explanatory strength, systematic underprediction, and worsening error in stronger-response regions.

## Figure 5

**Figure 5. Calibration structure of the verified legacy cross-domain baseline.** Predicted versus observed pIC50 values are shown together with the fitted calibration line and decile-level signed error. The baseline compresses dynamic range and increasingly undercalls stronger responses rather than failing uniformly at random.

## Figure 6

**Figure 6. Subgroup variability across tissue context and compound identity.** Tissue-level MAE and drug-level signed-error summaries show that the current baseline has non-uniform behavior across biological context groups and compounds, which should be stated explicitly in the manuscript rather than hidden behind aggregate metrics.

## Figure 11

**Figure 11. Leakage-sensitive performance differences across the staged ridge benchmark regimes.** MAE, RMSE, Pearson correlation, and `R²` are compared across pair-random, cell-line-holdout, compound-holdout, and double-cold-start split policies. The current baseline remains much stronger for unseen cell lines than for unseen compounds, and the strictest double-cold-start regime is the weakest overall result.

## Figure 12

**Figure 12. Leakage-safe multi-model comparison across completed benchmark regimes.** MAE and `R²` are compared across pair-random, cell-line-holdout, compound-holdout, and double-cold-start split policies for the completed `ridge` and `ols` sweeps. The two lightweight baselines are effectively indistinguishable across all four regimes, showing that the main leakage-sensitive generalization pattern is stable across both comparator families.

## Figure 7

**Figure 7. Competitive positioning of PharmacoProfiler relative to representative pharmacogenomics resources.** The current verified project scope is compared with major pharmacogenomics platforms and model-centric studies. PharmacoProfiler’s strongest differentiators are cross-resource harmonization, public inference serving, metadata-rich outputs, and benchmark transparency, while its clearest current gaps remain uncertainty-aware serving, deeper interpretability, and broader model-comparison depth.
