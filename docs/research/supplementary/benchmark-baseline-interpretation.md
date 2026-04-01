# Baseline Benchmark Interpretation

## Run summary

Canonical outputs for the current-repo baseline benchmark are now available in:

- `models/evaluation/legacy_pic50_baseline/benchmark_summary.json`
- `models/evaluation/legacy_pic50_baseline/metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_predictions.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_response_reconstruction_summary.json`

The executed benchmark preserved the verified legacy design:
- train domain: GDSC
- test domain: CCLE
- model family: Random Forest
- feature schema: 3,747 omics + 1,024 ECFP4

## Observed baseline metrics

The current packaged baseline run produced:

- Pearson `0.7556`
- Spearman `0.6273`
- MAE `0.6548`
- MSE `0.6991`
- RMSE `0.8361`
- R² `0.2633`

## Evaluated dataset footprint

The evaluated current-repo baseline covered:

- `337,761` GDSC training rows from the preserved response table
- `6,513` reconstructed CCLE evaluation rows
- `16` overlapping drugs with preserved GDSC fingerprints
- `434` overlapping CCLE cell lines present in the preserved omics matrix

## Scientific interpretation

This run establishes a reproducible, code-backed baseline for the current repository. It is sufficient to replace placeholder benchmark language in the manuscript with actual generated results.

The baseline remains limited in important ways:

- the CCLE evaluation input is reconstructed from preserved raw files, not recovered byte-for-byte from the missing legacy prepared file
- the run does not yet include confidence intervals
- the run does not yet include baseline-model comparisons
- the run does not yet include leakage-safe multi-split evaluation regimes

## Compatibility warning

The deployed `GDSC_CCLE_cross_domain_mode_7_v4.joblib` artifact emitted a scikit-learn version warning during execution. The model appears to have been serialized under scikit-learn `1.6.1`, while the current benchmark environment used scikit-learn `1.3.0`.

This did not block execution, but it should be treated as a reproducibility risk and documented in any manuscript or release note that cites the current benchmark outputs.
