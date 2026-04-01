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
- `predictor.py`: asset loading and prediction logic
- `requirements.txt`: runtime dependencies
- `smoke_test.py`: minimal service check
- `assets/README.md`: asset placement instructions

The top-level implementation preserves the verified legacy API behavior while making asset paths explicit and allowing the service to start in a degraded mode when large runtime artifacts are not yet present locally.

## Running the Service

1. Install dependencies from `requirements.txt`.
2. Place the three verified runtime assets in `assets/` or set `PHARMACOPROFILER_ASSET_DIR`.
3. Start the API with:

```bash
python3 app.py
```

## Current Runtime Behavior

- if required Python dependencies are missing, the service imports cleanly but reports degraded status
- if required model assets are missing, `/api/health` and `/api/info` return `503` with asset details
- if assets are present, the service preserves the legacy grouped SMILES prediction flow

## Service Tests

The current service contract tests live in `tests/api/test_prediction_api_contract.py`.
