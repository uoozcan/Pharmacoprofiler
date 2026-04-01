# Notebook Provenance Summary

## Purpose

This page identifies the decisive notebooks in the legacy codebase and summarizes what each one contributes to the implemented PharmacoProfiler system.

## Core modeling notebooks

### `GDSC_trained_model_predictions_for_all_platforms_v1.ipynb`
- role: generates model predictions across platforms using the GDSC-derived model and cell line mappings
- evidence seen:
  - loads the 988-cell-line omics matrix
  - maps cell lines to canonical names
  - joins Cellosaurus-derived metadata
  - prepares prediction outputs across platform contexts
- importance: strong evidence that prediction was intended as a cross-platform application, not only a local training exercise

### `Prediction_pairs_vector_matrice_preparation_v1.ipynb`
- role: constructs the combined prediction matrix from omics vectors, drug lists, approved-compound subsets, and harmonized identifiers
- evidence seen:
  - loads GDSC, CCLE, and NCI-60 vector and mapping tables
  - intersects datasets across shared feature space
  - builds the pairing logic used for downstream prediction
- importance: key provenance source for how compound-cell-line prediction tables were assembled

### `Prediction_filtering_v1.ipynb`
- role: filters the broad prediction outputs into subsets such as GDSC-overlapping cell lines
- evidence seen:
  - loads the large prediction table
  - filters by RRIDs and GDSC cell line membership
- importance: shows that the prediction outputs were post-processed into scoped deliverables for reporting and downstream use

## Dataset harmonization notebook groups

### GDSC
- examples:
  - `GDSC1_drug_response_v2_337K_V1.ipynb`
  - `GDSC2_drug_response_v2_337K_V1.ipynb`
  - `GDSC1_cell_line_file_v1.ipynb`
  - `GDSC2_cell_line_file_v1.ipynb`
- role: source-specific response extraction, cell line tables, and compound handling

### CCLE
- examples:
  - `CCLE_drug_response_v2.ipynb`
  - `CCLE_GNF_drug_response_dataset_v1.ipynb`
  - `CCLE_NP24_drug_response_dataset_v1.ipynb`
- role: response extraction and harmonization for the CCLE evaluation domain

### FIMM
- examples:
  - `FIMM_drug_response_dataset_v1.ipynb`
  - `FIMM_cell_line_file_v1.ipynb`
  - `FIMM_compound_file_v1.ipynb`
- role: smaller external pharmacogenomic dataset integration

### NCI-60
- examples:
  - `NCI-60_compound_file_v1.ipynb`
  - additional CellMiner/NCI-60 notebooks and tables in `Cellminer/` and `NCI-60/`
- role: alternative assay-source integration and compound mapping support

### PRISM, CTRP, NCATS
- examples:
  - `PRISM_drug_file_v1.ipynb`
  - `CTRP_drug_response_dataset_v1.ipynb`
  - `NCATS_drug_response_v1.ipynb`
- role: evidence that the broader PharmacoProfiler scope extended beyond the three-platform prediction service to a larger harmonized knowledge base

## Supporting chemical and annotation notebooks

### SMILES and InChI mapping
- examples:
  - `Finding_SMILES_for_all_comp_v1.ipynb`
  - `Finding_Inchi_keys_for_all_comp_v1.ipynb`
  - `All_drugs_SMILES_Inchi_keys_mapping_v1.ipynb`
- role: compound normalization and identifier repair

### Fingerprint generation
- examples:
  - `Fingerprint_production_for_compound_v1.ipynb`
  - `Fingerprint_production_for_approved_compounds_v1.ipynb`
- role: Morgan fingerprint generation supporting the prediction pipeline

### Class and visualization notebooks
- examples:
  - `compound_class_heatmap_v1.ipynb`
  - `upset_graph_v1.ipynb`
- role: class-level summaries and exploratory presentation outputs

## Provenance conclusion

The notebook layer is not incidental. It is the real historical implementation substrate of PharmacoProfiler:
- source extraction
- identifier harmonization
- feature construction
- prediction pair generation
- filtered reporting

Any future refactor should preserve this provenance by turning decisive notebook logic into scripts or packages rather than discarding it.
