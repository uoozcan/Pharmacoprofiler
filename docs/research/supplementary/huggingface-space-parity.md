# Hugging Face Space Parity Note

## Reviewed deployment

- Space page: `https://huggingface.co/spaces/ozcanumut/pic50-prediction-server`
- App base URL: `https://ozcanumut-pic50-prediction-server.hf.space`
- Review date: `2026-04-02`

## Confirmed live behavior

- `GET /api/health` returned healthy with `cell_lines_count: 988`
- `GET /api/info` returned model metadata for the deployed predictor
- `POST /api/predict` returned grouped SMILES-keyed predictions for a valid request
- the live public service is active and functionally serving the expected predictor

## Confirmed mismatches versus repo baseline

1. Hugging Face metadata mismatch
   - live `README.md` declares `sdk: gradio`
   - live prose describes a Gradio web interface
   - the actual deployment is a Docker-hosted Flask API

2. Request-limit mismatch
   - live documentation says there is no hard limit
   - live Dockerfile sets `MAX_SMILES_PER_REQUEST=10`
   - the maintained repo baseline also enforces a request limit

3. `/api/info` contract drift
   - live `/api/info` exposes model details but not the fuller dependency/asset-status framing from the maintained repo baseline

4. Response-quality issue
   - live prediction responses can expose missing tissue values as raw `NaN`
   - the maintained repo baseline now treats missing tissue metadata as empty string at the predictor layer

5. Deployment bundle drift
   - live Space files and `legacy_verified/` preserve older deployment wording and behavior
   - the maintained `services/prediction-api/` package is the intended canonical implementation

## Authority rule

- GitHub repo is canonical
- Hugging Face Space should be updated as a synced deployment target
- `services/prediction-api/HF_SPACE_README.md` and `services/prediction-api/HF_SPACE_Dockerfile` are the repo-side sync templates for the next Space update

## Immediate sync targets

- `services/prediction-api/app.py`
- `services/prediction-api/predictor.py`
- `services/prediction-api/requirements.txt`
- `services/prediction-api/HF_SPACE_Dockerfile`
- `services/prediction-api/HF_SPACE_README.md`

These should replace the truthfulness/parity-sensitive files in the Hugging Face Space root on the next deployment pass.
