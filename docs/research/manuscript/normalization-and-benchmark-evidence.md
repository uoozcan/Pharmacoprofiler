# Normalization and Benchmark Evidence

## Verified benchmark status

The current repository contains a reproducible baseline benchmark for the verified legacy predictor:

- train domain: GDSC
- external test domain: reconstructed CCLE
- model family: Random Forest
- feature schema: 3,747 omics + 1,024 ECFP4

Canonical generated outputs are stored under `models/evaluation/legacy_pic50_baseline/`.

The current baseline metrics are:

- Pearson `0.7556`
- Spearman `0.6273`
- MAE `0.6548`
- RMSE `0.8361`
- R² `0.2633`

Bootstrap `95%` confidence intervals are available in `subgroup_analysis_summary.json`, including:

- Pearson `0.7416` to `0.7685`
- RMSE `0.8199` to `0.8524`

## Tissue-normalization policy

The canonical tissue reporting layer is defined in:

- `configs/datasets/tissue_vocabulary.tsv`
- `docs/datasets/tissue-normalization.md`

This layer is reporting-only in the current phase:

- legacy assets are preserved unchanged
- service responses are preserved unchanged
- normalization applies only to benchmark, manuscript, and figure-facing outputs

Implemented alias merges:

- `Soft Tissue` and `soft_tissue` -> `soft_tissue`
- `Colon` -> `large_intestine`

Labels intentionally kept distinct:

- `pleura`
- `pleural_effusion`
- `pericardial_effusion`

## Normalized subgroup findings

Normalized tissue outputs are the canonical manuscript source:

- `models/evaluation/legacy_pic50_baseline/tissue_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics_normalized.tsv`

Raw tissue outputs are retained as audit artifacts:

- `models/evaluation/legacy_pic50_baseline/tissue_metrics_raw.tsv`

The normalization removed reporting splits and changed subgroup totals in the intended places:

- `large_intestine` now includes former `Colon` rows for a combined `n=223`
- `soft_tissue` now includes former `Soft Tissue` rows for a combined `n=174`

Representative normalized tissue results:

- `Stomach`: Pearson `0.8529`, MAE `0.6177`
- `Central Nervous System`: Pearson `0.8127`, MAE `0.5743`
- `Large Intestine / Colon`: Pearson `0.7254`, MAE `0.6580`
- `Pleura`: Pearson `0.6699`, MAE `0.7322`

## Calibration and limitation summary

The current predictor has a useful ranking signal but clear calibration weaknesses:

- mean signed error (`pred - true`): `-0.4943`
- underprediction share: `85.0%`
- global calibration slope: `0.7404`
- global calibration intercept: `1.0075`

Potency-bin analysis shows deterioration in the strongest-response region:

- `<=5.5`: MAE `0.5193`
- `5.5-6.5`: MAE `0.7676`
- `6.5-7.5`: MAE `0.8442`
- `>7.5`: MAE `1.1134`

Representative failure examples are recorded in `top_error_examples.tsv`.

## Manuscript-safe wording

### Strengths

`PharmacoProfiler currently supports a reproducible cross-domain pIC50 benchmark and a public SMILES-to-cell-line prediction service with metadata-enriched outputs, providing a defensible baseline for harmonization-plus-serving functionality.`

### Limitations

`The current benchmark remains a reconstructed GDSC-to-CCLE transfer baseline and shows systematic underprediction, reduced dynamic range at higher pIC50 values, and subgroup variability that should be stated explicitly rather than abstracted into a single global performance claim.`

## Next required analyses before stronger claims

Before stronger methodological or translational claims, the repository should add:

1. leakage-safe split regimes
2. baseline-model comparisons
3. calibrated vs uncalibrated evaluation
4. uncertainty or applicability-domain outputs
5. broader tissue ontology review beyond the current reporting-layer normalization
