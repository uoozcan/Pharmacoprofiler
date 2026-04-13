# Supplementary Benchmark Figure Captions

## Purpose

This file provides compact supplementary-caption text for the benchmark-support figure set. It is intended for manuscript assembly when a short caption reference is needed without the full legend-and-mapping document.

## Figure 2

**Figure 2. Drug-level error variability in the preserved cross-domain overlap set.** Mean absolute error is shown for each overlapping compound evaluated in the reconstructed CCLE benchmark. The panel makes clear that aggregate benchmark metrics hide substantial compound-specific heterogeneity, with some drugs transferring relatively well and others remaining dominated by large error.

## Figure 3

**Figure 3. Bootstrap 95% confidence intervals for the core benchmark metrics.** Bootstrap mean estimates and 95% confidence intervals are shown for Pearson correlation, Spearman correlation, MAE, RMSE, and `R²` over the reconstructed CCLE evaluation set. These intervals provide quantitative bounds around the current code-backed baseline and should be cited alongside the point estimates rather than replaced by them.

## Figure 4

**Figure 4. Largest absolute errors in the reconstructed CCLE benchmark.** The largest signed prediction errors are shown as cell line-drug pairs annotated by tissue context. The panel makes the dominant failure mode explicit: severe underprediction of high-response examples rather than uniformly random error across the benchmark.

## Figure 10

**Figure 10. Mechanism-aware annotation of the preserved benchmark-overlap drugs.** Drug-level error, target breadth, and broad mechanism-class summaries are shown for the overlap set using the verified merged compound-target table. This figure adds biological context for interpretation and prioritization, but it should still be read as an annotation layer rather than as proof of mechanistic learning.
