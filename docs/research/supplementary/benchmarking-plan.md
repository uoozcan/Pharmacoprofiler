# Benchmarking Plan

## Current baseline package

The current repository baseline is the GDSC-train to CCLE-test Random Forest workflow implemented in:
- `scripts/evaluate/run_legacy_benchmark_baseline.py`
- `scripts/evaluate/prepare_ccle_cross_domain_response.py`
- `configs/models/legacy-pic50-benchmark-config.json`
- `models/evaluation/legacy_pic50_baseline/`

This baseline uses the verified legacy artifact manifest and reconstructs the missing CCLE cross-domain input from the preserved raw CCLE response table when the original prepared file is absent.

The current reconstruction summary from preserved files is:
- 6,513 usable CCLE response rows
- 16 overlapping drugs with available GDSC fingerprints
- 434 overlapping cell lines present in the preserved CCLE omics matrix

## Required Metrics

- Pearson correlation
- RMSE
- MAE
- R-squared
- confidence intervals for core correlations

## Required Comparisons

- intra-platform validation
- cross-platform validation
- baseline predictors
- comparison against relevant published methods where feasible

## Required Deliverables

- reproducible evaluation script or notebook
- metric table with dataset split definitions
- figure-generation pipeline for manuscript-ready panels
- versioned report stored in this directory

## Canonical output location

Generated benchmark outputs should be treated as canonical only when they are written to:
- `models/evaluation/legacy_pic50_baseline/benchmark_summary.json`
- `models/evaluation/legacy_pic50_baseline/metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_predictions.tsv`
