# Omics Feature Provenance Boundary

## Purpose

This note defines the strongest current manuscript-safe statement about the preserved 3747-feature omics matrices used by the PharmacoProfiler predictor. It is intended to tighten the methods boundary without overclaiming unrecovered preprocessing steps.

## Verified artifacts

The current repository and preserved legacy workspace contain the following cross-platform matrix artifacts:

- `CLRB_MODELLING/GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`
- `CLRB_MODELLING/CCLE_extracted_503_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`
- `CLRB_MODELLING/NCI-60_extracted_60_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`

These files support the following verified claims:

1. the predictor consumes fixed-length omics vectors with `3747` numeric features per cell line
2. the same feature-space naming pattern is preserved across GDSC, CCLE, and NCI-60
3. the feature-space description is explicitly tied to `L1000 common genes` and a `selected_common_3_platform` artifact lineage
4. the notebook and script lineage uses these matrices directly during prediction-pair assembly and cross-domain model training

## Verified usage boundary

The notebook `CLRB_MODELLING/Prediction_pairs_vector_matrice_preparation_v1.ipynb` and the script `CLRB_MODELLING/GDSC_CCLE_cross_domain_mode_7.py` show that these matrices are consumed as prepared inputs. They support manuscript wording that:

- GDSC, CCLE, and NCI-60 were aligned in a shared omics feature space before model fitting
- the final model input is built by concatenating the `3747`-feature cell-line vector with a `1024`-bit ECFP4 fingerprint
- the resulting modeling matrix has `4771` numeric features

## Still unresolved

The currently recovered evidence is not sufficient to describe the full upstream derivation of the `3747` features in methods-level detail. In particular, the following remain unreconstructed:

- the exact raw omics input tables used before the shared-feature matrices were produced
- the exact normalization sequence applied upstream of the preserved matrix files
- the exact feature-selection procedure that reduced the space to `3747` features
- whether any imputation or platform-specific scaling was performed before the cross-platform matrices were finalized

Those steps should therefore continue to be described as preserved provenance rather than fully reconstructed preprocessing.

## Manuscript-safe wording

Recommended wording:

> The verified predictor consumes preserved cross-platform cell-line matrices with 3747 numeric features per cell line. The available artifact names, notebook lineage, and training script support the interpretation that these matrices represent an L1000-based shared feature space aligned across GDSC, CCLE, and NCI-60. However, the full upstream normalization and feature-selection derivation of these prepared matrices has not yet been fully reconstructed from the preserved notebook evidence and is therefore not described beyond that verified minimum.

## Implication for project scope

This note narrows a persistent ambiguity in the project. PharmacoProfiler can now make a stronger claim about the role and identity of the preserved omics matrices, but it still should not claim a fully packaged and reproducible end-to-end omics harmonization pipeline until the upstream generation steps are recovered and scripted.
