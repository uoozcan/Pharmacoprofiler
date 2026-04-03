# Baseline Benchmark Subgroup Analysis

## Scope

This note extends the canonical baseline outputs in `models/evaluation/legacy_pic50_baseline/` with subgroup diagnostics derived from `ccle_predictions.tsv` and `ccle_response_reconstructed.tsv`.

Generated machine-readable artifacts:

- `models/evaluation/legacy_pic50_baseline/subgroup_analysis_summary.json`
- `models/evaluation/legacy_pic50_baseline/drug_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics_normalized.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics_raw.tsv`
- `models/evaluation/legacy_pic50_baseline/potency_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/top_error_examples.tsv`

Reproduction command:

```bash
python scripts/evaluate/analyze_legacy_benchmark_subgroups.py
```

## Global behavior

- evaluated rows: `6513`
- Pearson: `0.7556`
- Spearman: `0.6273`
- MAE: `0.6548`
- RMSE: `0.8361`
- R²: `0.2633`
- mean signed error (`pred - true`): `-0.4943`
- underprediction share: `85.0%`
- overprediction share: `15.0%`

Interpretation: the model preserves ranking signal but tends to underpredict pIC50 and compresses output variance.

## Bootstrap confidence intervals

Bootstrap (`n=1000`) on the same prediction table:

- Pearson: `0.7416` to `0.7685`
- Spearman: `0.6094` to `0.6444`
- MAE: `0.6417` to `0.6674`
- RMSE: `0.8199` to `0.8524`
- R²: `0.2309` to `0.2928`

## Drug-level variability

Top Pearson drugs:

- `selumetinib`: Pearson `0.3777`, MAE `0.5274`, bias `-0.5092`
- `pd0325901`: Pearson `0.3771`, MAE `0.7962`, bias `+0.1829`
- `irinotecan`: Pearson `0.3697`, MAE `1.6631`, bias `-1.6631`

Lowest Pearson drugs:

- `pha665752`: Pearson `-0.0408`, MAE `0.3707`, bias `-0.3694`
- `crizotinib`: Pearson `0.1062`, MAE `0.6372`, bias `-0.6240`
- `paclitaxel`: Pearson `0.1176`, MAE `1.1410`, bias `-0.5135`

High-error drugs by MAE:

- `irinotecan`: MAE `1.6631`
- `plx4720`: MAE `1.1725`
- `paclitaxel`: MAE `1.1410`

Priority correction targets (combined low-correlation/high-bias/high-MAE heuristic):

- `irinotecan` (highest priority)
- `plx4720`
- `paclitaxel`
- `pha665752`
- `crizotinib`

## Tissue-level variability

The canonical manuscript-facing tissue output is now the normalized table:

- `models/evaluation/legacy_pic50_baseline/tissue_metrics.tsv`

The raw-label audit table is retained in:

- `models/evaluation/legacy_pic50_baseline/tissue_metrics_raw.tsv`

Implemented reporting-layer merges:

- `Colon` -> `Large Intestine / Colon`
- `Soft Tissue` and `soft_tissue` -> `Soft Tissue`

Intentionally distinct labels:

- `Pleura`
- `Pleural Effusion`
- `Pericardial Effusion`

Higher Pearson tissues:

- `stomach`: Pearson `0.8529`, MAE `0.6177`
- `oesophagus`: Pearson `0.8271`, MAE `0.5844`
- `ovary`: Pearson `0.8204`, MAE `0.6003`

Lower Pearson tissues:

- `blood`: Pearson `0.5566`, MAE `0.6694`
- `pleura`: Pearson `0.6699`, MAE `0.7322`
- `haematopoietic_and_lymphoid_tissue`: Pearson `0.6891`, MAE `0.7504`

Highest MAE tissues:

- `haematopoietic_and_lymphoid_tissue`: MAE `0.7504`
- `small_intestine`: MAE `0.7616`
- `bone_marrow`: MAE `0.7598`

## Calibration diagnostics

Global least-squares calibration (`pIC50_Pred ~ pIC50_True`) gives:

- slope: `0.7404`
- intercept: `1.0075`

This confirms regression-to-the-mean behavior.

Examples of weak per-drug calibration slopes:

- `paclitaxel`: slope `0.0326`, Pearson `0.1176`
- `crizotinib`: slope `0.0656`, Pearson `0.1062`
- `plx4720`: slope `0.1732`, Pearson `0.2535`

## Potency-bin behavior

The benchmark weakens as true pIC50 increases:

- `<=5.5`: MAE `0.5193`, mean signed error `-0.3160`
- `5.5-6.5`: MAE `0.7676`, mean signed error `-0.6625`
- `6.5-7.5`: MAE `0.8442`, mean signed error `-0.7204`
- `>7.5`: MAE `1.1134`, mean signed error `-1.1131`

This pattern is consistent with under-calling stronger responses and is a critical manuscript limitation to state explicitly.

## Representative high-error examples

Top absolute-error examples from `top_error_examples.tsv` include:

- `nco2` + `nilotinib` (`Haematopoietic and Lymphoid Tissue`): true `8.1191`, predicted `4.3894`, absolute error `3.7298`
- `sigm5` + `plx4720` (`Bone Marrow`): true `7.4741`, predicted `4.0977`, absolute error `3.3764`
- `ku812` + `nilotinib` (`Haematopoietic and Lymphoid Tissue`): true `7.7741`, predicted `4.4314`, absolute error `3.3428`

These examples are useful for a manuscript limitations table or supplementary failure-case figure.

## Immediate fix targets

1. Add post-hoc calibration on validation folds and report calibrated vs uncalibrated metrics.
2. Add per-drug bias correction analysis for drugs with persistent signed error.
3. Add uncertainty/applicability scoring so low-confidence subgroup predictions are flagged.
4. Extend benchmark phase-two splits (compound/cell-line/source holdouts) before adding model complexity.
5. Extend the current reporting-layer normalization into a broader cross-resource tissue ontology only after source-level review.
