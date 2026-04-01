# Legacy pIC50 Prediction Service

## Status

This document captures the verified current public prediction-service contract derived from the legacy codebase and the publicly deployed Hugging Face Space.

## Verified deployment baseline

Verified public deployment:
- Hugging Face Space: `ozcanumut/pic50-prediction-server`

Verified public files:
- `app.py`
- `requirements.txt`
- `Dockerfile`
- `GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`
- `GDSC_988_cell_line_name_main_fix_RRID_v1.txt`
- `GDSC_CCLE_cross_domain_mode_7_v4.joblib`

## Current endpoints

### `POST /predict`

Primary prediction endpoint.

Accepted input:
```json
{
  "smiles": "CCO"
}
```

or:

```json
{
  "smiles": ["CCO", "CCN"]
}
```

Some legacy service variants also support:

```json
{
  "smiles_list": ["CCO", "CCN"]
}
```

### `GET /health`

Reports service health and whether the model and metadata were loaded.

### `GET /info`

Reports summary metadata about the loaded model, feature counts, and cell line coverage.

## Current response behavior

The service predicts across all loaded GDSC cell lines for each valid SMILES and returns grouped results by SMILES.

Representative response fields:
- `total_smiles_submitted`
- `valid_smiles_count`
- `invalid_smiles_count`
- `predictions`
- `total_predictions`
- `invalid_smiles`

Each prediction row contains:
- `CELL_LINE_NAME`
- `RRID`
- `TISSUE`
- `pIC50_Prediction`

## Feature schema

- cell line omics features: 3,747
- compound fingerprint: Morgan / ECFP4, 1,024 bits
- total concatenated features per prediction row: 4,771

## Runtime dependencies

Verified deployment dependencies:
- Flask
- flask-cors
- pandas
- numpy
- scikit-learn
- joblib
- RDKit

## Known deployment-file discrepancies

The legacy workspace and the currently fetched Hugging Face Space are closely aligned but not perfectly identical at the deployment-file level.

Important example:
- the locally archived Docker setup includes an `8000`-port Python-run variant
- the fetched public Hugging Face `Dockerfile` uses port `5000` and a `gunicorn` launch command

The service contract and model inputs are stable enough to treat the prediction API as verified, but exact runtime packaging should be treated as deployment-variant specific.

## Compatibility policy for future work

Any refactor in `services/prediction-api/` should preserve backward compatibility with the current `POST /predict` SMILES-based request shape unless a versioned API is introduced.
