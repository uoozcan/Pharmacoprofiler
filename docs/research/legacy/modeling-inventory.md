# Legacy Modeling Inventory

## Purpose

This inventory tracks the core legacy modeling artifacts that define the current PharmacoProfiler predictor and the evidence around it.

## Canonical deployed artifact set

These files are the most important verified artifacts because they are both present in the legacy workspace and exposed by the public Hugging Face Space:

### Omics feature matrix
- file: `GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`
- role: per-cell-line feature matrix used for prediction
- verified dimensions in naming: 988 cell lines, 3,747 omics features

### Cell line metadata and mapping table
- file: `GDSC_988_cell_line_name_main_fix_RRID_v1.txt`
- role: maps edited cell line names to canonical display names, RRIDs, and tissue labels

### Trained model
- file: `GDSC_CCLE_cross_domain_mode_7_v4.joblib`
- role: deployed pIC50 prediction model used by the Hugging Face Space

## Training-script lineage

### Training and cross-domain evaluation
- `CLRB_MODELLING/GDSC_CCLE_cross_domain_mode_7.py`
- `CLRB_MODELLING/GDSC_CCLE_cross_domain_mode_7_for_CLRB_v1.py`

Verified behavior:
- trains `RandomForestRegressor`
- uses GDSC for training
- evaluates on CCLE
- writes regression metrics and prediction tables

### Local prediction prototypes
- `CLRB_MODELLING/pred_model.py`
- `CLRB_MODELLING/pred_model_main.py`

Role:
- early local scripts for joining omics vectors with generated ECFP4 fingerprints and producing per-cell-line predictions

### Deployment-oriented service code
- `CLRB_MODELLING/pharmacoprofiler_docker/api.py`
- `CLRB_MODELLING/pharmacoprofiler_docker/pharmacoprofiler/app.py`
- `CLRB_MODELLING/pharmacoprofiler_docker/pharmacoprofiler/huggingface_profile/app.py`

Role:
- Flask-serving variants leading to the public Hugging Face deployment

## Supporting modeling files

### CCLE omics feature matrix
- `CCLE_extracted_503_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`
- used as the cross-domain evaluation feature space

### Response and fingerprint tables
- `GDSC_drug_response_drugs_w_smiles_988cl_404dr_337K_v4_w_fps.txt`
- GDSC response table with chemical fingerprints

### Prediction outputs
- files beginning with `Predictions_for_GDSC_trained_GCN_omics_`
- despite the file prefix, the verified deployed model is a random forest, so these outputs should be interpreted cautiously until lineage is fully reconciled

## Known gaps and inconsistencies

1. The manuscript draft contains generic ML text that is not reliable implementation evidence.
2. Some filenames use `GCN` terminology, but the verified training script and deployed artifact use a random forest.
3. The deployment code has multiple variants, so only the Hugging Face-exposed `app.py` should be treated as the current public service baseline.
4. The website frontend source is not directly verified from this environment.
5. The notebook pipeline is valuable but not yet packaged into reproducible modules.

## Current best-supported interpretation

The strongest defensible statement is:

PharmacoProfiler currently includes a notebook-based harmonization workflow and a deployed Random Forest pIC50 predictor that combines a 3,747-feature cell line omics representation with 1,024-bit ECFP4 compound fingerprints and serves per-cell-line predictions from SMILES input.
