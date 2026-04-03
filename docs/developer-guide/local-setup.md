# Local Setup

## Current State

This repository currently provides:
- a maintained prediction service under `services/prediction-api/`
- benchmark and reproducibility scripts under `scripts/evaluate/`
- manuscript and reviewer evidence under `docs/research/`

The main web application source code still needs to be imported.

## Expected Future Setup

### Frontend
- install dependencies in `app/frontend/`
- run local development server

### Backend
- create Python environment
- install `app/backend/requirements.txt`
- load dataset and API configuration from `configs/`

### Prediction Service
- create isolated Python environment
- install `services/prediction-api/requirements.txt`
- run local inference server or containerized service
- run:
  - `python3 -m unittest tests.api.test_prediction_api_contract tests.unit.test_benchmark_common tests.unit.test_prediction_predictor`
  - `python3 services/prediction-api/smoke_test.py`

## Required Environment Files

- dataset manifest config
- backend service config
- prediction service config
- optional local `.env` files that are not committed to Git

## Hugging Face Deployment Notes

The public Hugging Face Space is a Docker-hosted Flask deployment synced from the maintained service baseline.

Repo-side sync templates:
- `services/prediction-api/HF_SPACE_README.md`
- `services/prediction-api/HF_SPACE_Dockerfile`
