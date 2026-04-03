# Benchmark Reporting Standard

## Purpose

This document defines the minimum reporting bundle required before any benchmark number is cited in manuscript text, figures, reviewer responses, or README claims.

## Required bundle

Every canonical benchmark run must provide:

- artifact provenance and file paths
- split policy
- metric table
- machine-readable benchmark summary
- confidence intervals
- subgroup tables
- calibration note
- compatibility/runtime warning note

## Current Stage Definitions

### Stage 1: reconstructed baseline

Required outputs:

- `models/evaluation/legacy_pic50_baseline/benchmark_summary.json`
- `models/evaluation/legacy_pic50_baseline/metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_response_reconstruction_summary.json`

Interpretation rule:

- cite as a reconstructed GDSC-to-CCLE baseline only

### Stage 2: normalized subgroup reporting

Required outputs:

- `models/evaluation/legacy_pic50_baseline/subgroup_analysis_summary.json`
- `models/evaluation/legacy_pic50_baseline/drug_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics_raw.tsv`
- `models/evaluation/legacy_pic50_baseline/potency_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/top_error_examples.tsv`

Interpretation rule:

- cite normalized tissue outputs for manuscript tables and figures
- preserve raw tissue outputs as audit artifacts

### Stage 3: stronger benchmark design

Must add before stronger generalization claims:

- leakage-safe split regimes
- baseline-model comparisons
- saved split definitions
- confidence intervals on each benchmark regime

### Stage 4: deployment-strengthening metrics

Must add before stronger translational claims:

- uncertainty or applicability-domain outputs
- calibrated vs uncalibrated comparison
- subgroup confidence reporting

## Current required caveats

All current benchmark citations must retain these caveats:

- the CCLE evaluation input is reconstructed from preserved raw files
- the deployed `v4` model artifact emits a scikit-learn compatibility warning at load time
- the current predictor shows systematic underprediction and compressed response range at higher pIC50
