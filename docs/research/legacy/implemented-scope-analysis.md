# PharmacoProfiler Legacy Implemented Scope Analysis

## Purpose

This document records what PharmacoProfiler is verifiably implemented to do today, based on the legacy codebase in `/home/umut/projects/pharmacoprofiler_legacy`, the currently deployed Hugging Face Space, and the current repository's curated research materials.

It is intentionally stricter than the manuscript draft. When manuscript claims and implementation evidence diverge, this document follows code and deployed artifacts.

## Verified Current Scope

### 1. Multi-dataset pharmacogenomic harmonization

The legacy workspace contains dataset-specific notebooks and files for:
- GDSC
- CCLE
- NCI-60
- FIMM
- PRISM
- CTRP
- NCATS
- CellMiner-derived mapping workflows

The overall implemented pipeline is notebook-driven rather than package-driven. The notebooks build harmonized tables for cell lines, compounds, and drug-response data across these public pharmacogenomic resources.

### 2. Cell line and compound normalization

The legacy codebase contains explicit evidence of:
- cell line name editing and mapping tables
- RRID-based cell line metadata mapping
- Cellosaurus-related cross-reference files
- compound SMILES and InChI-key mapping workflows
- merged compound and cell line tables used as integration layers

This confirms that one of PharmacoProfiler's real contributions is curation and normalization across heterogeneous pharmacogenomic sources, not only visualization.

### 3. Cross-domain pIC50 prediction

The prediction subsystem is verifiably implemented as:
- omics features per cell line: 3,747
- chemical features per compound: 1,024-bit ECFP4 fingerprints
- model family: `RandomForestRegressor`
- training setting: GDSC-based training with cross-domain evaluation against CCLE

The decisive training script is:
- `CLRB_MODELLING/GDSC_CCLE_cross_domain_mode_7.py`

That script:
- loads GDSC drug response with fingerprints
- loads CCLE response data for testing
- merges fingerprints with omics matrices
- trains a random forest on GDSC
- evaluates on CCLE using MAE, MSE, RMSE, Spearman, Pearson, and R-squared
- serializes the model with `joblib`

### 4. Public prediction serving

The deployed Hugging Face Space at `ozcanumut/pic50-prediction-server` is publicly accessible and exposes these files:
- `README.md`
- `app.py`
- `requirements.txt`
- `Dockerfile`
- `GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`
- `GDSC_988_cell_line_name_main_fix_RRID_v1.txt`
- `GDSC_CCLE_cross_domain_mode_7_v4.joblib`

The deployed service behavior is therefore verified, not inferred.

## Verified Prediction Service Behavior

### Input

The Hugging Face service accepts one or more SMILES strings through JSON input.

Supported request shapes in the verified Flask app:
- `{"smiles": "..."}` for a single compound
- `{"smiles": ["...", "..."]}` for multiple compounds
- in some legacy variants, `smiles_list` is also accepted

### Output

For each valid SMILES, the service predicts pIC50 across all loaded GDSC cell lines and returns:
- `CELL_LINE_NAME`
- `RRID`
- `TISSUE`
- `pIC50_Prediction`

The deployed service also reports counts for:
- submitted SMILES
- valid SMILES
- invalid SMILES
- total predictions

### Current operational model

The current predictor is not a generalized compound-target model or a foundation model. It is a supervised tabular model that scores compound-cell-line pairs by concatenating:
- a precomputed omics vector for each cell line
- an on-the-fly ECFP4 fingerprint for each input compound

## Verified Scientific Contributions

Based on implementation evidence, the strongest current PharmacoProfiler contributions are:

1. Harmonizing multiple public pharmacogenomic screening resources into a common analysis space.
2. Linking prediction outputs to curated cell line metadata including RRID and tissue context.
3. Exposing a deployable public pIC50 prediction service rather than keeping the model notebook-only.
4. Supporting compound-centric screening across many cell lines from a single SMILES input.

## Important Non-verified or Overstated Claims

The current manuscript draft should not be treated as the implementation source of truth for:
- exact frontend framework in current production
- exact backend framework in current production web deployment
- full preprocessing strategy details such as quantile normalization, KNN imputation, or broad multi-omics feature integration unless separately verified from code
- final benchmarking claims that still contain placeholders or generic narrative text
- any clinical-translation claims beyond exploratory research use

## Frontend and web-application stack status

Current status of stack verification:
- legacy manuscript intent: React frontend and Flask backend
- public external clue: a portfolio description suggests React + D3 + Django/Djongo
- direct scripted verification of `pharmacoprofiler.com` frontend code is currently blocked by ModSecurity (`406`)

Therefore the live website stack must be treated as partially unverifiable from this environment.

## Practical Interpretation

The implemented legacy system is best understood as three coupled layers:

1. Notebook-based pharmacogenomic data assembly and harmonization.
2. A cross-domain Random Forest pIC50 predictor over omics plus ECFP4 features.
3. A deployable Flask/Hugging Face serving layer for batch compound scoring against GDSC cell lines.

That is the baseline that future innovation work should extend.
