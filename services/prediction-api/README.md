# Prediction API Service

Target location for the standalone inference service aligned with the Hugging Face deployment.

Expected responsibilities:
- request validation
- model loading
- prediction serving
- model metadata reporting

## Verified Legacy Baseline

The currently verified legacy service has been preserved under `legacy_verified/`.

That preserved baseline includes:
- the deployed Flask service entrypoint
- the deployment requirements
- the deployment Dockerfile

Do not treat the top-level service directory as implemented until the legacy code is refactored into a maintained package and tested.

## Current Baseline Implementation

This directory now includes a current-repo baseline implementation:
- `app.py`: Flask entrypoint
- `predictor.py`: asset loading, feature construction, and batch prediction logic
- `requirements.txt`: runtime dependencies
- `smoke_test.py`: minimal service check
- `assets/README.md`: asset placement instructions

The top-level implementation preserves the verified legacy API behavior while making asset paths explicit and allowing the service to start in a degraded mode when large runtime artifacts are not yet present locally.

## Hugging Face Space Sync

The GitHub repo is the source of truth for the maintained prediction service. For the public Hugging Face Space:

- sync `app.py`, `predictor.py`, and `requirements.txt` from this directory
- copy `HF_SPACE_Dockerfile` to the Space root as `Dockerfile`
- copy `HF_SPACE_README.md` to the Space root as `README.md`

This keeps the public Space aligned with the maintained Flask/Docker baseline rather than the older `legacy_verified/` snapshot.

## Running the Service

1. Install dependencies from `requirements.txt`.
2. Place the three verified runtime assets in `assets/` or set `PHARMACOPROFILER_ASSET_DIR`.
3. Start the API with:

```bash
python3 app.py
```

The maintained HTTP surface is:

- `POST /api/predict`
- `POST /api/predict/single`
- `GET /api/health`
- `GET /api/info`

## Current Runtime Behavior

- if required Python dependencies are missing, the service imports cleanly but reports degraded status
- if required model assets are missing, `/api/health` and `/api/info` return `503` with asset details
- if assets are present, the service preserves the legacy grouped SMILES prediction flow
- `app.py` owns request parsing, response codes, and route definitions
- `predictor.py` owns asset loading, fingerprint generation, feature assembly, and batch prediction

## Service Tests

Contract and smoke tests:

- `python3 -m unittest tests.api.test_prediction_api_contract`
- `python3 services/prediction-api/smoke_test.py`

The API contract tests are fake-predictor based and are intended to validate response behavior without requiring real model assets. The smoke test is the lightweight real-runtime check.

Uncertainty and applicability analyses live in the repository rather than the live API contract. That now includes an OOB-based split-conformal calibration pass, but the external CCLE benchmark remains under-covered, so uncertainty fields should stay documentation-only until transfer improves materially.
