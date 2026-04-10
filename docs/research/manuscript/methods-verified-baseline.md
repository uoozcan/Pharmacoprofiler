# Methods and Results Baseline From Verified Implementation

## Status

This is the corrected baseline text for the manuscript methods and initial model-results description. It is derived from verified code and deployed artifacts, not from generic narrative text.

For notebook-grounded dataset preprocessing and harmonization language, see `preprocessing-methods-from-notebooks.md`.

## 3.2 Machine Learning Model for Drug Response Prediction

The currently verified PharmacoProfiler prediction engine is a tabular regression model that predicts pIC50 values for compound-cell-line pairs. The model combines a precomputed cell line omics representation with an on-the-fly chemical fingerprint derived from the submitted compound structure.

The verified training script is `GDSC_CCLE_cross_domain_mode_7.py` in the legacy modeling workspace. That script trains a `RandomForestRegressor` on GDSC drug-response examples and evaluates transfer performance on CCLE. The model hyperparameters visible in the script are `max_depth=81`, `n_estimators=100`, and `random_state=2`.

The deployed model artifact used by the public Hugging Face service is `GDSC_CCLE_cross_domain_mode_7_v4.joblib`.

## 3.3 Feature Representation

The verified feature representation contains two parts.

For cell lines, PharmacoProfiler uses a fixed-length omics vector stored in `GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`. The file contains `CELL_LINE_NAME` plus 3,747 numeric features.

For compounds, PharmacoProfiler computes a 1,024-bit ECFP4 fingerprint from each submitted SMILES string using RDKit (`GetMorganFingerprintAsBitVect` with radius 2 and 1,024 bits).

At inference time, the model concatenates:
- 3,747 omics features
- 1,024 ECFP4 bits

This yields a 4,771-feature vector for each compound-cell-line pair.

Notebook-derived preprocessing provenance for response preparation, Cellosaurus enrichment, and model-input assembly is summarized in:

- `docs/research/manuscript/preprocessing-methods-from-notebooks.md`
- `docs/research/notebooks/notebook-methods-evidence-matrix.md`

## 3.4 Cell Line Mapping and Metadata

The verified metadata table used by the deployed service is `GDSC_988_cell_line_name_main_fix_RRID_v1.txt`. This table contains:
- canonical display name (`main`)
- edited/internal cell line identifier (`edited`)
- RRID
- tissue label

The public service uses this table to map internal cell line identifiers to user-facing names and to return RRID and tissue metadata with each prediction.

## 3.5 Prediction Service Implementation

The verified public prediction service is the Hugging Face Space `ozcanumut/pic50-prediction-server`. The currently accessible service files are:
- `app.py`
- `requirements.txt`
- `Dockerfile`
- the three runtime model/data artifacts above

The service is implemented in Flask and exposes JSON endpoints for health, model information, and pIC50 prediction. The prediction endpoint accepts one or more SMILES strings, generates ECFP4 fingerprints, pairs them with all loaded GDSC cell lines, and returns grouped pIC50 predictions together with canonical cell line name, RRID, and tissue.

## 4.1 Verified Baseline Results Statement

The current codebase supports a defensible statement that PharmacoProfiler implements cross-domain pIC50 prediction with GDSC-based training and CCLE-based evaluation. The current repository now contains a canonical generated baseline benchmark report under `models/evaluation/legacy_pic50_baseline/`.

The benchmark input lineage is now partially recoverable from preserved files even though the exact legacy prepared CCLE file is absent. A current-repo reconstruction step recovers 6,513 evaluable CCLE response rows spanning 16 overlapping drugs and 434 overlapping cell lines from the preserved raw CCLE response table plus GDSC fingerprint mappings. This supports the benchmark preparation path, but it should still be described as a reconstructed current-repo input rather than the original prepared benchmark file.

The current packaged baseline run produced:
- Pearson correlation: `0.7556`
- Spearman correlation: `0.6273`
- MAE: `0.6548`
- RMSE: `0.8361`
- R²: `0.2633`

Bootstrap confidence intervals, calibration findings, and normalized subgroup evidence are now recorded in:

- `models/evaluation/legacy_pic50_baseline/subgroup_analysis_summary.json`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/potency_bin_metrics.tsv`
- `docs/research/manuscript/normalization-and-benchmark-evidence.md`

The current repository also contains a first-pass uncertainty and applicability analysis for the preserved Random Forest baseline. These outputs are recorded in:

- `models/evaluation/legacy_pic50_baseline/uncertainty_applicability_summary.json`
- `models/evaluation/legacy_pic50_baseline/uncertainty_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/applicability_bin_metrics.tsv`
- `docs/research/supplementary/uncertainty-applicability-analysis.md`

These values should be cited as the current repository baseline only together with the explicit caveat that the benchmark uses a reconstructed CCLE evaluation input and a deployed `v4` model artifact that emits a scikit-learn version compatibility warning at load time.

At this stage, the correct manuscript framing is:
- the predictor architecture and feature schema are verified
- the cross-domain training/evaluation design is verified
- the public serving layer is verified
- a reproducible current-repo benchmark baseline is available for inclusion in figures or claims, with normalized tissue reporting now defined for manuscript tables and figures

## 4.2 Figure-Linked Reporting Guidance

The current manuscript revision should anchor the benchmark narrative to the generated figure set under `docs/research/figures/` rather than to standalone summary prose.

Use the following figure pairings for quantitative reporting:
- Figure 1 (`legacy_benchmark_overview`) for the main benchmark overview and the claim that the baseline preserves useful cross-domain ranking signal while remaining biased and only partially explanatory
- Supplementary Figure 3 (`legacy_benchmark_confidence_intervals`) for bootstrap confidence intervals around Pearson, Spearman, MAE, RMSE, and R²
- Figure 5 (`legacy_benchmark_calibration`) for the calibration limitation statement covering mean signed error, underprediction frequency, and compressed dynamic range
- Figure 6 (`legacy_benchmark_subgroup_variability`) for normalized tissue-level heterogeneity and drug-level bias variation
- Supplementary Figure 2 (`legacy_benchmark_drug_mae`) for compound-specific error spread
- Supplementary Figure 4 (`legacy_benchmark_top_errors`) for representative failure cases in the strongest-response regime
- Figure 7 (`platform_positioning_comparison`) for Introduction or Discussion text about current differentiation versus competing resources and predictive-model papers
- Supplementary Figure 8 (`legacy_benchmark_uncertainty`) for first-pass uncertainty behavior and interval under-coverage
- Supplementary Figure 9 (`legacy_benchmark_applicability`) for first-pass applicability-domain behavior based on nearest-train cell-line similarity

For manuscript-ready legends and paragraph mapping, use `docs/research/figures/figure_legends_and_mapping.md`. For manuscript-safe wording on normalized subgroup evidence and calibration caveats, use `docs/research/manuscript/normalization-and-benchmark-evidence.md`. For uncertainty/applicability wording, use `docs/research/supplementary/uncertainty-applicability-analysis.md`.

## What should not be claimed from current evidence

The following points remain insufficiently verified from the current codebase and should not appear as fixed implementation facts without additional evidence:
- exact preprocessing steps such as quantile normalization or KNN imputation
- exact multi-omics composition beyond the verified numeric feature matrix
- calibrated prediction intervals, conformal uncertainty estimates, or finalized applicability-domain methods
- completed multi-model leakage-safe benchmark comparisons beyond the staged ridge sweep
- current production frontend stack for `pharmacoprofiler.com`
