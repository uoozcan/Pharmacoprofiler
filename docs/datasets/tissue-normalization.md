# Tissue Normalization

## Purpose

This document defines the canonical tissue reporting layer used for benchmark summaries, manuscript tables, and future figure generation.

The normalization layer is intentionally non-destructive:

- legacy source assets are not rewritten
- public prediction-service responses are not changed in this phase
- normalization is applied only to benchmark, reporting, and manuscript-facing artifacts

## Canonical vocabulary

The versioned source of truth is:

- `configs/datasets/tissue_vocabulary.tsv`

Each row defines:

- `raw_label`: label as preserved in the reconstructed benchmark input
- `normalized_code`: machine-safe reporting bucket
- `display_label`: human-readable manuscript/figure label
- `merge_into_code`: explicit alias merge target when the raw label is not the canonical reporting bucket
- `note`: rationale for merge or retention

## Implemented merges

The current benchmark normalization makes these immediate alias merges:

- `Soft Tissue` and `soft_tissue` -> `soft_tissue`
- `Colon` -> `large_intestine`

These merges remove formatting- and vocabulary-driven subgroup splits without changing the underlying benchmark rows.

## Labels intentionally kept distinct

The following labels remain distinct in the canonical vocabulary:

- `pleura`
- `pleural_effusion`
- `pericardial_effusion`

Reason: the current evidence does not justify collapsing anatomical site labels with fluid-based or effusion-derived labels into a single reporting class.

## Residual curation needs

The normalization layer fixes obvious reporting duplication, but it does not yet resolve deeper ontology questions such as:

- whether fluid-derived labels should be grouped with source organs
- whether blood and haematopoietic tissues should be merged in any downstream biological analysis
- whether legacy tissue strings from other datasets require a larger cross-resource tissue ontology

Those decisions should be made only with source-level review and documented separately from this reporting-layer cleanup.
