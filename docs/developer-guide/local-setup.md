# Local Setup

## Current State

This repository currently provides the structural foundation and documentation layer. The main application and prediction-service codebases still need to be imported.

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

## Required Environment Files

- dataset manifest config
- backend service config
- prediction service config
- optional local `.env` files that are not committed to Git
