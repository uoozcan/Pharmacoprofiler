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

Bootstrap `95%` confidence intervals (1,000 resamples) on the same run:

- Pearson `0.7416` to `0.7685`
- Spearman `0.6094` to `0.6444`
- MAE `0.6417` to `0.6674`
- RMSE `0.8199` to `0.8524`
- R² `0.2309` to `0.2928`

## Evaluated dataset footprint

The evaluated current-repo baseline covered:

- `337,761` GDSC training rows from the preserved response table
- `6,513` reconstructed CCLE evaluation rows
- `16` overlapping drugs with preserved GDSC fingerprints
- `434` overlapping CCLE cell lines present in the preserved omics matrix

## Scientific interpretation

This run establishes a reproducible, code-backed baseline for the current repository. It is sufficient to replace placeholder benchmark language in the manuscript with actual generated results.

Additional diagnostics from `ccle_predictions.tsv` show the current baseline is directionally useful but systematically under-calibrated:

- mean signed error (`pred - true`): `-0.4943`
- underprediction share: `85.0%`
- overprediction share: `15.0%`
- global calibration fit (`pred ~ true`): slope `0.7404`, intercept `1.0075`

This indicates compression toward mid-range pIC50 values with a net negative bias on the reconstructed CCLE transfer set.

## Subgroup behavior snapshot

Drug-level spread shows non-uniform transfer quality:

- strongest Pearson values include `selumetinib` (`0.3777`) and `pd0325901` (`0.3771`)
- weakest Pearson values include `pha665752` (`-0.0408`) and `crizotinib` (`0.1062`)
- largest MAE values include `irinotecan` (`1.6631`) and `plx4720` (`1.1725`)

Tissue-level behavior is more stable but still heterogeneous:

- higher Pearson examples: `stomach` (`0.8529`), `oesophagus` (`0.8271`), `ovary` (`0.8204`)
- lower Pearson examples: `blood` (`0.5566`), `pleura` (`0.6699`), `haematopoietic_and_lymphoid_tissue` (`0.6891`)
- normalized reporting now merges `Colon` into `Large Intestine / Colon` and collapses `Soft Tissue` with `soft_tissue`
- worst MAE examples in normalized reporting include `small_intestine` (`0.7616`) and `bone_marrow` (`0.7598`)

Representative failure mode from high-error drugs:

- `paclitaxel` fit slope `0.0326` with Pearson `0.1176`, indicating very weak dynamic response tracking despite moderate global correlation.

The baseline remains limited in important ways:

- the CCLE evaluation input is reconstructed from preserved raw files, not recovered byte-for-byte from the missing legacy prepared file
- the deployed legacy Random Forest baseline is still a dataset-transfer benchmark rather than a full leakage-safe model-family comparison
- the repository now includes bootstrap confidence intervals, calibration summaries, subgroup diagnostics, a staged ridge leakage-safe sweep, and a completed `ridge` versus `ols` leakage-safe comparison
- the attempted legacy RF comparator still did not produce result files and is not included in the current manuscript evidence package

## Compatibility warning

The deployed `GDSC_CCLE_cross_domain_mode_7_v4.joblib` artifact emitted a scikit-learn version warning during execution. The model appears to have been serialized under scikit-learn `1.6.1`, while the current benchmark environment used scikit-learn `1.3.0`.

This did not block execution, but it should be treated as a reproducibility risk and documented in any manuscript or release note that cites the current benchmark outputs.
