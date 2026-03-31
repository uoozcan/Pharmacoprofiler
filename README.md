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

The application source code is not yet imported into this repository. The current foundation is intended to support that import cleanly.

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
4. Import the web frontend, backend, and prediction service source trees into:
   - `app/frontend/`
   - `app/backend/`
   - `services/prediction-api/`

## Documentation

- User documentation: [docs/user-guide/platform-overview.md](docs/user-guide/platform-overview.md)
- Developer documentation: [docs/developer-guide/local-setup.md](docs/developer-guide/local-setup.md)
- API documentation: [docs/api/prediction-api.md](docs/api/prediction-api.md)
- Dataset documentation: [docs/datasets/data-sources.md](docs/datasets/data-sources.md)
- Operations and release process: [docs/operations/release-and-sustainability.md](docs/operations/release-and-sustainability.md)
- Manuscript hardening and reviewer responses: [docs/research/README.md](docs/research/README.md)

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

The repository includes CI placeholders for:
- documentation build validation
- backend tests
- frontend tests
- prediction service smoke tests

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow, documentation, and review expectations.

## Citation

See [CITATION.cff](CITATION.cff). Update author and DOI metadata before public release.
