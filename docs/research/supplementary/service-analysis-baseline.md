# Prediction Service Analysis Baseline

## Real-asset validation

The maintained service under `services/prediction-api/` was validated against the verified legacy runtime assets using a temporary asset directory assembled from preserved legacy files.

Validated assets:
- GDSC omics matrix
- GDSC cell-line metadata table
- deployed `GDSC_CCLE_cross_domain_mode_7_v4.joblib` model artifact

## Observed behavior

The service successfully:

- started in healthy mode with all dependencies and assets present
- reported `model_loaded: true` from `/api/health` and `/api/info`
- returned `988` predictions for a single valid SMILES input (`CCO`)
- returned grouped prediction rows with:
  - `CELL_LINE_NAME`
  - `RRID`
  - `TISSUE`
  - `pIC50_Prediction`
- handled mixed valid and invalid SMILES batches while preserving valid predictions and surfacing invalid entries explicitly

## Example observed output

For a valid `CCO` request, the first returned prediction row was:

- `CELL_LINE_NAME`: `22RV1`
- `RRID`: `CVCL_1045`
- `TISSUE`: `Prostate`
- `pIC50_Prediction`: `4.200940810736789`

For a mixed batch `['CCO', '']`, the service returned:

- `invalid_smiles_count: 1`
- invalid entry: `{"smiles": "", "error": "Invalid or empty SMILES string"}`

## Compatibility warning

Like the benchmark run, the real-asset service validation emitted a scikit-learn version warning when loading the `v4` model artifact. This warning should be treated as a current reproducibility risk rather than ignored.
