---
title: pIC50 Prediction Server
emoji: 🧬
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 5000
pinned: false
license: mit
---

# pIC50 Prediction Server

This Hugging Face Space is a Docker-hosted Flask prediction API for PharmacoProfiler. It is not a Gradio application.

## Runtime

- Framework: Flask API served with gunicorn
- Deployment type: Hugging Face Docker Space
- Public endpoints:
  - `GET /api/health`
  - `GET /api/info`
  - `POST /api/predict`
  - `POST /api/predict/single`

## Model Summary

- Dataset: GDSC-trained cross-domain pIC50 predictor
- Cell lines: 988
- Omics features: 3747
- Fingerprints: ECFP4, 1024 bits
- Total features: 4771

## Request Limits

- `MAX_SMILES_PER_REQUEST` defaults to `10`
- Use small batches for public requests to keep latency predictable

## Example Request

```bash
curl -X POST https://ozcanumut-pic50-prediction-server.hf.space/api/predict \
  -H "Content-Type: application/json" \
  -d '{"smiles":"CCO"}'
```

## Expected Output Shape

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
        "TISSUE": "Lung",
        "pIC50_Prediction": 4.27
      }
    ]
  },
  "total_predictions": 988,
  "model_version": "GDSC_CCLE_cross_domain_mode_7_v4.joblib",
  "feature_schema_version": "omics_3747_plus_ecfp4_1024_v1",
  "api_version": "1.0.0",
  "request_timestamp": "2026-04-02T00:00:00+00:00"
}
```

## Sync Rule

The GitHub repository is authoritative. Sync the Space root from the maintained implementation in `services/prediction-api/`:

- `app.py`
- `predictor.py`
- `requirements.txt`
- `HF_SPACE_Dockerfile` copied to `Dockerfile`
- this `HF_SPACE_README.md` copied to `README.md`
- the three runtime asset files

Do not treat `legacy_verified/` as the deployment source of truth. It is a preserved legacy snapshot only.
