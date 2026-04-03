# Pharmacoprofiler Documentation

This documentation set turns the project into a maintainable scientific software repository and records the evidence needed for publication-quality reporting.

## Documentation Map

- `architecture/`: system boundaries, data flow, deployment assumptions
- `user-guide/`: platform features and intended researcher workflows
- `developer-guide/`: repository conventions and local setup
- `api/`: REST contracts for prediction and data query services
- `datasets/`: provenance, harmonization, and known limitations
- `operations/`: release, maintenance, and sustainability procedures
- `research/`: manuscript status, reviewer responses, and benchmark support
- `research/legacy/`: verified implementation-scope analysis, legacy model inventory, and innovation recommendations
- `research/notebooks/`: decisive notebook provenance summaries

## Current State

The current repository contains documentation, archived manuscript materials, benchmark evidence, and a maintained baseline for the legacy prediction service under `services/prediction-api/`.

The web application source code still needs to be imported into the designated component directories.

The verified legacy Hugging Face prediction service is preserved in `services/prediction-api/legacy_verified/`, while the current maintained service and Hugging Face sync templates live in `services/prediction-api/`.

The canonical current-repo benchmark output target is `models/evaluation/legacy_pic50_baseline/`.

The public Hugging Face deployment has been reviewed and aligned with the maintained Flask/Docker baseline; see `docs/research/supplementary/huggingface-space-parity.md`.
