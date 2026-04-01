# Prediction API

## Status

Current maintained baseline for the prediction service in this repository. The public compatibility target is the verified Hugging Face deployment documented in [legacy-pic50-service.md](legacy-pic50-service.md).

The current repository implementation lives in `services/prediction-api/` and preserves backward compatibility with the legacy SMILES-based prediction flow.

## Endpoints

- `POST /api/predict`
- `POST /api/predict/single`
- `GET /api/health`
- `GET /api/info`

## Request

```json
{
  "smiles": "CCO"
}
```

or:

```json
{
  "smiles_list": ["CCO", "CCN"]
}
```

## Response

```json
{
  "total_smiles_submitted": 1,
  "valid_smiles_count": 1,
  "invalid_smiles_count": 0,
  "predictions": {
    "CCO": [
      {
        "CELL_LINE_NAME": "A549",
        "RRID": "CVCL_0023",
        "TISSUE": "lung",
        "pIC50_Prediction": 6.1
      }
    ]
  },
  "total_predictions": 988,
  "model_version": "GDSC_CCLE_cross_domain_mode_7_v4.joblib",
  "feature_schema_version": "omics_3747_plus_ecfp4_1024_v1",
  "api_version": "1.0.0",
  "request_timestamp": "2026-04-01T12:00:00"
}
```

## Compatibility Rules

- Keep the SMILES-based request contract backward-compatible with the legacy service.
- Preserve grouped prediction outputs keyed by submitted SMILES.
- Additive metadata is allowed.
- Future fields such as applicability scores or prediction intervals must be introduced without breaking the current response shape.
