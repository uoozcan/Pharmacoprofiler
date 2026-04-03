# PharmacoProfiler: Verified Methods and Results Baseline

This file replaces the earlier generic draft sections with a code-grounded baseline. It is intentionally limited to what is currently verified from the legacy codebase and the deployed Hugging Face service.

For the full implementation evidence, see:
- [methods-verified-baseline.md](methods-verified-baseline.md)
- [preprocessing-methods-from-notebooks.md](preprocessing-methods-from-notebooks.md)
- [../legacy/implemented-scope-analysis.md](../legacy/implemented-scope-analysis.md)
- [../legacy/modeling-inventory.md](../legacy/modeling-inventory.md)

## 3. Methods

### 3.2 Machine Learning Model for Drug Response Prediction

The currently verified PharmacoProfiler predictor is a supervised tabular regression model for pIC50 prediction. The core training script is `GDSC_CCLE_cross_domain_mode_7.py` from the legacy modeling workspace. That script trains a `RandomForestRegressor` on GDSC drug-response examples and evaluates transfer performance on CCLE.

The deployed model artifact used by the public Hugging Face service is `GDSC_CCLE_cross_domain_mode_7_v4.joblib`.

### 3.3 Feature Representation

The verified feature representation contains:
- a 3,747-feature omics vector for each cell line
- a 1,024-bit ECFP4 fingerprint for each submitted compound

The omics matrix is stored in `GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`. The first column is `CELL_LINE_NAME`, and the remaining columns are numeric features. The chemical descriptor is generated on demand from SMILES using RDKit Morgan fingerprints with radius 2 and 1,024 bits.

For each compound-cell-line pair, the service concatenates these two components into a 4,771-feature input vector.

### 3.4 Cell Line Metadata and Mapping

The deployed service uses `GDSC_988_cell_line_name_main_fix_RRID_v1.txt` to map internal cell line identifiers to:
- canonical display names
- RRIDs
- tissue labels

This file contains 988 rows and 29 distinct tissue labels in the verified local copy.

### 3.5 Service Implementation

The currently verified public deployment is the Hugging Face Space `ozcanumut/pic50-prediction-server`. The public file tree exposes:
- `app.py`
- `requirements.txt`
- `Dockerfile`
- the omics matrix
- the cell line metadata table
- the trained model artifact

The prediction service is implemented in Flask. It accepts one or more SMILES strings, computes ECFP4 fingerprints, pairs each compound with all loaded GDSC cell lines, and returns pIC50 predictions together with canonical cell line name, RRID, and tissue.

### 3.6 Data Harmonization Scope

The broader legacy workspace contains dataset-specific notebooks for GDSC, CCLE, NCI-60, FIMM, PRISM, CTRP, NCATS, and CellMiner-derived workflows. This verifies that PharmacoProfiler's historical scope extended beyond the deployed predictor and included notebook-driven harmonization across multiple public pharmacogenomic resources.

At present, that harmonization layer is preserved as notebook provenance and supporting tables rather than a packaged pipeline.

The current repository also includes a notebook-grounded preprocessing note that can be used to rewrite the dataset and harmonization methods sections without inventing unsupported steps:

- [preprocessing-methods-from-notebooks.md](preprocessing-methods-from-notebooks.md)

## 4. Results Baseline

### 4.1 Verified Claims

The current repository supports these defensible claims:
- PharmacoProfiler implements cross-domain pIC50 prediction with a Random Forest baseline trained on GDSC and evaluated on CCLE.
- The deployed service publicly serves per-cell-line predictions from SMILES input.
- Prediction outputs are enriched with canonical cell line names, RRIDs, and tissue labels.
- The current-repo packaged baseline run over the reconstructed CCLE evaluation set achieved Pearson `0.7556`, Spearman `0.6273`, MAE `0.6548`, RMSE `0.8361`, and R² `0.2633`.
- Bootstrap `95%` confidence intervals for the current baseline are now available, including Pearson `0.7416-0.7685` and RMSE `0.8199-0.8524`.
- The current subgroup outputs now use a canonical tissue-normalization layer for manuscript-facing reporting while preserving raw-label audit tables.

### 4.2 Claims that still require rerun evidence

The following should not be presented as final benchmark results:
- baseline-model comparisons
- leakage-safe benchmark claims across multiple split policies

Use [../supplementary/benchmark-reproducibility-baseline.md](../supplementary/benchmark-reproducibility-baseline.md) as the current benchmark baseline and rerun checklist.
Use [normalization-and-benchmark-evidence.md](normalization-and-benchmark-evidence.md) as the canonical manuscript note for normalized subgroup evidence, calibration caveats, and manuscript-safe wording.
Use [preprocessing-methods-from-notebooks.md](preprocessing-methods-from-notebooks.md) for notebook-grounded dataset preprocessing and harmonization wording.

When the current-repo benchmark is executed, quantitative results should be cited from:
- `models/evaluation/legacy_pic50_baseline/benchmark_summary.json`
- `models/evaluation/legacy_pic50_baseline/metrics.tsv`

The current benchmark should be described with two explicit caveats:
- the CCLE evaluation input is reconstructed from preserved raw files
- the deployed `v4` model artifact emits a scikit-learn version compatibility warning during load

For publishable wording on strengths, weaknesses, and next-step analyses, see [normalization-and-benchmark-evidence.md](normalization-and-benchmark-evidence.md) and [../supplementary/publication-readiness-analysis.md](../supplementary/publication-readiness-analysis.md).
