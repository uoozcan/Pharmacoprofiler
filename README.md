# Pharmacoprofiler

Pharmacoprofiler is a pharmacogenomics platform for harmonizing large-scale cancer drug response datasets, exploring drug-cell line-indication relationships, and serving machine-learning-based pIC50 predictions.

Public endpoints:
- Web application: <https://pharmacoprofiler.com>
- Prediction service: <https://huggingface.co/spaces/ozcanumut/pic50-prediction-server>

## Repository Status

This repository was restructured from a manuscript-first workspace into a monorepo-ready scientific software repository. The current tree now separates:
- product components
- data and model assets
- technical and operational documentation
- manuscript and reviewer materials
- archived legacy drafts

The web application source code is not yet imported into this repository. The maintained prediction service baseline is represented directly under `services/prediction-api/`, while the original Hugging Face-aligned service files remain preserved under `services/prediction-api/legacy_verified/`.

The public Hugging Face Space has now been aligned with the maintained Flask/Docker service contract and repo-side sync templates are tracked in:
- `services/prediction-api/HF_SPACE_README.md`
- `services/prediction-api/HF_SPACE_Dockerfile`

## Repository Layout

```text
.
├── app/                    # Web application code
├── archive/                # Legacy manuscript workspace and non-canonical assets
├── configs/                # Dataset/model/environment configuration
├── data/                   # Raw, interim, processed, and metadata layers
├── deploy/                 # Docker, hosting, and Hugging Face deployment assets
├── docs/                   # User, developer, API, architecture, and research docs
├── models/                 # Model registry, cards, trained artifacts, evaluation
├── notebooks/              # Exploratory, validation, and figure-generation notebooks
├── packages/               # Reusable harmonization, feature, and model packages
├── scripts/                # Setup, ingest, train, evaluate, and release scripts
├── services/               # Standalone services such as prediction API
└── tests/                  # Unit, integration, API, UI, and data validation tests
```

## Quick Start

1. Read the project overview in [docs/index.md](docs/index.md).
2. Review the architecture in [docs/architecture/overview.md](docs/architecture/overview.md).
3. Review manuscript and reviewer materials in [docs/research/README.md](docs/research/README.md).
4. Review the prediction API contract in [docs/api/prediction-api.md](docs/api/prediction-api.md).
5. Run the maintained service checks:
   - `python3 -m unittest tests.api.test_prediction_api_contract tests.unit.test_benchmark_common tests.unit.test_prediction_predictor`
   - `python3 services/prediction-api/smoke_test.py`
6. Run the benchmark foundation steps:
   - `python3 scripts/evaluate/benchmark_reproducibility_check.py`
   - `python3 scripts/evaluate/run_legacy_benchmark_baseline.py`

## Documentation

- User documentation: [docs/user-guide/platform-overview.md](docs/user-guide/platform-overview.md)
- Developer documentation: [docs/developer-guide/local-setup.md](docs/developer-guide/local-setup.md)
- API documentation: [docs/api/prediction-api.md](docs/api/prediction-api.md)
- Verified legacy API baseline: [docs/api/legacy-pic50-service.md](docs/api/legacy-pic50-service.md)
- Hugging Face parity note: [docs/research/supplementary/huggingface-space-parity.md](docs/research/supplementary/huggingface-space-parity.md)
- Benchmark reproducibility baseline: [docs/research/supplementary/benchmark-reproducibility-baseline.md](docs/research/supplementary/benchmark-reproducibility-baseline.md)
- Dataset documentation: [docs/datasets/data-sources.md](docs/datasets/data-sources.md)
- Operations and release process: [docs/operations/release-and-sustainability.md](docs/operations/release-and-sustainability.md)
- Manuscript hardening and reviewer responses: [docs/research/README.md](docs/research/README.md)
- Legacy implementation analysis: [docs/research/legacy/implemented-scope-analysis.md](docs/research/legacy/implemented-scope-analysis.md)

## Data Provenance

The current documentation assumes harmonization across GDSC1, GDSC2, CCLE/DepMap, NCI-60/CellMiner, gCSI, and FIMM, with external registry support from Cellosaurus, ChEMBL, PubChem, and an indication source such as RepurposeDB.

Large raw datasets, private exports, and trained model binaries should not be committed directly into Git. Use external object storage and store only lightweight schemas, manifests, and example slices in this repository.

## Branch Strategy

- `main`: production-ready, release-tagged state
- `develop`: integration branch for the next release
- `feature/<topic>`: scoped feature work
- `fix/<topic>`: bug fixes
- `docs/<topic>`: documentation-only work
- `release/<version>`: optional stabilization branch

## Testing

The repository includes CI coverage for:
- documentation build validation
- backend/frontend placeholders while app code is still absent
- prediction service smoke tests

The prediction service contract tests and helper-unit tests can be run with Python and the maintained test files under `tests/`. Benchmark execution additionally requires runtime dependencies such as `joblib`, `scikit-learn`, and `rdkit`.

## Legacy Predictor Import

The verified legacy Hugging Face prediction service has been preserved as an import target under `services/prediction-api/legacy_verified/`. The large model artifacts remain external for now and are documented in the service notes rather than copied into the repository.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow, documentation, and review expectations.

## Citation

See [CITATION.cff](CITATION.cff). Update author and DOI metadata before public release.
