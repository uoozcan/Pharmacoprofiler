# Prediction API

## Status

Planned contract. Validate against the Hugging Face deployment before publication.

## Endpoint

`POST /predict`

## Request

```json
{
  "compound_smiles": "CC1=CC...",
  "cell_line_ids": ["ACH-000001", "ACH-000002"],
  "dataset_context": "gdsc",
  "top_k": 10
}
```

## Response

```json
{
  "model_version": "pending",
  "predictions": [
    {
      "cell_line_id": "ACH-000001",
      "predicted_pic50": 6.2,
      "confidence_interval": null
    }
  ]
}
```

## Required Metadata

- model version
- training data provenance
- response timestamp
- validation constraints and warnings
