# Project Notebook

## Purpose

This file is the running project notebook for repository restructuring, benchmark hardening, manuscript correction, and publishability work. It should be updated as substantive project changes are made so the current state does not depend on chat history.

## 2026-04-02

### Publishability and benchmark foundation

- preserved the verified legacy predictor as the current baseline
- added canonical benchmark outputs under `models/evaluation/legacy_pic50_baseline/`
- documented reconstructed CCLE benchmark lineage and baseline metrics
- added subgroup, calibration, potency-bin, and failure-case analyses

### Tissue normalization

- introduced a reporting-layer tissue vocabulary in `configs/datasets/tissue_vocabulary.tsv`
- normalized obvious reporting duplicates:
  - `Colon` -> `large_intestine`
  - `Soft Tissue` -> `soft_tissue`
- kept `pleura`, `pleural_effusion`, and `pericardial_effusion` distinct pending source-level review
- documented the policy in `docs/datasets/tissue-normalization.md`

### Manuscript evidence package

- added `docs/research/manuscript/normalization-and-benchmark-evidence.md`
- added `docs/research/supplementary/benchmark-reporting-standard.md`
- updated manuscript and reviewer-facing docs to cite normalized subgroup outputs and calibration caveats

### Notebook-grounded methods work

- reviewed decisive legacy notebooks for:
  - GDSC1 and GDSC2 response preparation
  - CCLE NP24 and GNF preprocessing
  - FIMM IC50 recovery and pIC50 conversion
  - NCI-60 pGI50 handling
  - NCATS wide-to-long reshaping
  - Cellosaurus-based harmonization
  - fingerprint generation and predictor input assembly
- added `docs/research/notebooks/notebook-methods-evidence-matrix.md`
- added `docs/research/manuscript/preprocessing-methods-from-notebooks.md`

### Current methods boundaries

- source-specific response preprocessing is now notebook-grounded
- cell-line and compound harmonization are notebook-grounded but still partly manual and dictionary-based
- predictor input assembly is notebook- and script-grounded
- upstream omics normalization and feature-selection steps remain only partially reconstructed and should continue to be described as preserved provenance rather than verified preprocessing

### Next recommended steps

1. turn the notebook-derived preprocessing note into final manuscript section text
2. generate manuscript-ready figures from the canonical benchmark outputs
3. add leakage-safe benchmark regimes and baseline-model comparisons
4. decide whether to expose normalized tissue fields in downstream service or export layers as additive metadata

### Script cleanup and utility hardening

- added a shared evaluation helper layer in `scripts/evaluate/_common.py` for config loading, output-dir resolution, token normalization, and artifact resolution
- aligned the maintained benchmark scripts around a clearer CLI pattern with explicit config and output-dir overrides where applicable
- tightened script boundaries:
  - artifact verification remains isolated in `benchmark_reproducibility_check.py`
  - CCLE reconstruction remains isolated in `prepare_ccle_cross_domain_response.py`
  - baseline execution remains isolated in `run_legacy_benchmark_baseline.py`
  - subgroup analysis remains isolated in `analyze_legacy_benchmark_subgroups.py`
- cleaned `services/prediction-api/app.py` so request parsing and response metadata are centralized at the HTTP layer
- cleaned `services/prediction-api/predictor.py` so asset loading, metadata construction, valid-compound filtering, and feature assembly are more explicit
- expanded API contract coverage for degraded info, `smiles_list`, single-SMILES prediction, max-request enforcement, and invalid-SMILES reporting
- added lightweight unit coverage for the shared benchmark helper module

### Current script maturity

- canonical maintained scripts:
  - `scripts/evaluate/*`
  - `services/prediction-api/app.py`
  - `services/prediction-api/predictor.py`
  - `tests/api/test_prediction_api_contract.py`
- preserved legacy reference:
  - `services/prediction-api/legacy_verified/`
- scaffolding only:
  - `scripts/setup/`
  - `scripts/ingest/`
  - `scripts/train/`
  - `scripts/release/`

### Hugging Face alignment

- reviewed the live Space page and public app endpoints on `2026-04-02`
- confirmed the live public service is healthy and returns `988` predictions for a valid single-SMILES request
- confirmed the live Space metadata is inaccurate:
  - `sdk: gradio` even though the deployment is Flask + Docker
  - request-limit docs drift from the actual `MAX_SMILES_PER_REQUEST=10` runtime assumption
- confirmed live public JSON can expose missing tissue metadata as raw `NaN`
- updated the maintained predictor to sanitize missing tissue metadata to empty string at the canonical service layer
- added repo-side Hugging Face sync templates:
  - `services/prediction-api/HF_SPACE_README.md`
  - `services/prediction-api/HF_SPACE_Dockerfile`
- added `docs/research/supplementary/huggingface-space-parity.md` as the operational parity note
