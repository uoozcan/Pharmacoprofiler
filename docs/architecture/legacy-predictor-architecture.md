# Legacy Predictor Architecture

## Overview

The verified legacy predictor is a three-stage system:

1. Notebook-driven data harmonization across public pharmacogenomic resources.
2. A trained Random Forest regression model over concatenated omics and chemical fingerprint features.
3. A Flask-based deployment layer exposed publicly through Hugging Face.

## Training layer

Verified core training pattern:
- train on GDSC compound-cell-line response pairs
- represent compounds as 1,024-bit ECFP4 fingerprints
- represent cell lines as 3,747-feature omics vectors
- evaluate transfer performance on CCLE in the core cross-domain script

## Serving layer

The verified public service:
- loads the feature matrix and cell-line metadata at startup
- converts user-submitted SMILES to Morgan fingerprints with RDKit
- concatenates each compound fingerprint with every loaded cell-line omics vector
- predicts pIC50 for every generated compound-cell-line pair
- returns predictions with canonical cell line name, RRID, and tissue

## Architecture constraints

- current implementation is optimized for inference simplicity, not modularity
- notebook provenance is high, package modularity is low
- model artifacts are file-based and loaded directly from the working directory
- current public deployment verifies the prediction layer only, not the full website architecture

## Refactor target

The current repository should preserve this architecture as the baseline import target before introducing:
- uncertainty outputs
- explainability endpoints
- tissue-aware ranking
- formal benchmark packaging
