# Architecture Overview

## Purpose

Pharmacoprofiler should operate as a multi-component platform with clear separation between the public web application, backend orchestration layer, data harmonization pipeline, and ML inference service.

## Target Components

### Frontend
- location: `app/frontend/`
- role: researcher-facing interface for filtering, network exploration, export, and prediction submission
- expected inputs: user filters, cell line selections, compound identifiers or SMILES
- expected outputs: visualizations, tables, export files, prediction requests

### Backend
- location: `app/backend/`
- role: request handling, query orchestration, export generation, dataset metadata, API gateway behavior
- expected dependencies: harmonized data layer, prediction service, authentication/session layer if later introduced

### Prediction Service
- location: `services/prediction-api/`
- role: serves pIC50 predictions and model metadata
- deployment alignment: Hugging Face Space contract or equivalent container deployment

### Shared Packages
- `packages/data-harmonization/`: identifier normalization, source ingestion, QC
- `packages/feature-engineering/`: compound and cell-line feature generation
- `packages/model-training/`: train/evaluate/baseline comparison code
- `packages/shared-types/`: shared schemas and payload definitions

## Data Flow

1. Source datasets are retrieved and versioned in manifests.
2. Harmonization jobs map compounds, cell lines, targets, and indications to canonical identifiers.
3. Processed datasets are exposed to the backend for search, filtering, and visualization.
4. Prediction requests are forwarded to the inference service with validated payloads.
5. Outputs are returned with explicit metadata and version references.

## Current Gap

The current repository does not yet contain the actual frontend, backend, or inference code. This documentation defines the intended boundaries so that imported code can be placed without ambiguity.
