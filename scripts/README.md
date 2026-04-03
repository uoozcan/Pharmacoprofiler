# Scripts

This directory contains command-line entry points grouped by purpose. At the current project stage, the maintained and manuscript-linked scripts are concentrated in `evaluate/`.

## Canonical Scripts

The following scripts are the maintained baseline for benchmark reproducibility and reporting:

1. `evaluate/benchmark_reproducibility_check.py`
   - verifies the preserved legacy artifacts against the versioned manifest
   - expected input: `configs/models/legacy-pic50-artifacts.json`
   - expected output: stdout pass/fail summary only
2. `evaluate/prepare_ccle_cross_domain_response.py`
   - reconstructs the preserved CCLE benchmark input when the original prepared table is absent
   - expected input: `configs/models/legacy-pic50-benchmark-config.json` plus preserved legacy response/vector files
   - expected outputs:
     - `ccle_response_reconstructed.tsv`
     - `ccle_response_reconstruction_summary.json`
3. `evaluate/run_legacy_benchmark_baseline.py`
   - runs the canonical GDSC-to-CCLE Random Forest baseline
   - expected input: benchmark config, verified artifacts, prepared or reconstructed CCLE response table
   - expected outputs:
     - `benchmark_summary.json`
     - `metrics.tsv`
     - `ccle_predictions.tsv`
     - `ccle_response_reconstructed.tsv` when reconstruction is used
4. `evaluate/analyze_legacy_benchmark_subgroups.py`
   - computes secondary benchmark analyses for manuscript/reporting use
   - expected input: generated benchmark outputs plus the tissue vocabulary
   - expected outputs:
     - `subgroup_analysis_summary.json`
     - `drug_metrics.tsv`
     - `potency_bin_metrics.tsv`
     - `top_error_examples.tsv`
     - `tissue_metrics_raw.tsv`
     - `tissue_metrics.tsv`
     - `tissue_metrics_normalized.tsv`

## Recommended Run Order

Use the scripts in this order:

1. `python3 scripts/evaluate/benchmark_reproducibility_check.py`
2. `python3 scripts/evaluate/prepare_ccle_cross_domain_response.py`
3. `python3 scripts/evaluate/run_legacy_benchmark_baseline.py`
4. `python3 scripts/evaluate/analyze_legacy_benchmark_subgroups.py`

Optional overrides supported by the maintained evaluation scripts:

- `--config /path/to/config.json`
- `--output-dir /path/to/output-dir`
- `PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR=/path/to/output-dir`

## Environment Assumptions

- Python environment should include the maintained service/benchmark dependencies.
- The legacy runtime artifacts must remain available at the paths described in `configs/models/legacy-pic50-artifacts.json`.
- The evaluation layer is designed to emit stable machine-readable outputs and short run summaries only; exploratory notebook-style printing should not be added back into these scripts.

## Directory Maturity

- `evaluate/`: maintained and manuscript-linked
- `setup/`: scaffolding only
- `ingest/`: scaffolding only
- `train/`: scaffolding only
- `release/`: scaffolding only

The scaffold directories exist for future work and should not be treated as production-ready pipelines yet.
