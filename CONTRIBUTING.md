# Contributing

## Scope

This repository combines scientific software documentation, manuscript support material, and future application code. Contributions must preserve both software engineering quality and scientific traceability.

## Workflow

1. Create branches from `develop`.
2. Use one concern per branch.
3. Open pull requests against `develop` unless preparing a release.
4. Keep code, documentation, and scientific claims aligned in the same change.

## Pull Request Requirements

Every pull request must state:
- scientific or product rationale
- user-facing impact
- tests or verification performed
- data, model, or manuscript claims affected
- documentation updated or explicitly not needed

## Scientific Documentation Rules

- Do not add unsupported performance claims.
- Do not describe implementation details that cannot be traced to code, config, or reproducible analysis.
- Record dataset source, version, retrieval date, and preprocessing assumptions.
- Keep manuscript-facing language conservative unless supported by evidence.

## Code and Documentation Standards

- Use clear file names and avoid ad hoc draft names in tracked canonical paths.
- Keep raw data, processed data, and derived figures separate.
- Prefer Markdown for versioned docs and scripts for reproducible figure/stat generation.
- Store large data and trained models outside Git unless they are lightweight examples.

## Review Focus

Reviewers should prioritize:
- correctness
- reproducibility
- data provenance
- API and workflow clarity
- maintainability

## Commit Conventions

Recommended prefixes:
- `docs:`
- `feat:`
- `fix:`
- `data:`
- `model:`
- `ops:`
