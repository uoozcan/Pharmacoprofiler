# Repository Conventions

## Canonical vs Legacy Material

- `docs/research/`: canonical tracked manuscript-facing materials
- `archive/legacy-manuscript-materials/`: old drafts, duplicated exports, and exploratory assets

## Data Handling

- do not commit large raw datasets
- keep manifests, schemas, and example slices in Git
- record source, version, retrieval date, and preprocessing notes

## Scientific Claims

- every performance claim must link to a reproducible analysis artifact
- every dataset claim must link to a source or manifest
- every API claim must match the implemented contract

## Naming

- use lowercase kebab-case file names for Markdown and config files
- avoid temporary names such as `copy`, `final_final`, or autosave variants in canonical paths
