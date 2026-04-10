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
5. `evaluate/analyze_legacy_benchmark_uncertainty.py`
   - computes first-pass uncertainty and applicability proxies from the preserved Random Forest baseline
   - expected input: benchmark config, verified artifacts, prepared or reconstructed CCLE response table
   - expected outputs:
     - `ccle_predictions_with_uncertainty.tsv`
     - `uncertainty_bin_metrics.tsv`
     - `applicability_bin_metrics.tsv`
     - `cell_line_applicability_metrics.tsv`
     - `uncertainty_applicability_summary.json`
6. `evaluate/generate_legacy_benchmark_figures.py`
   - generates the manuscript-quality benchmark and positioning figure set from canonical outputs
   - expected input: `models/evaluation/legacy_pic50_baseline/` plus `docs/research/figures/platform_positioning_matrix.tsv`
   - expected outputs:
     - `legacy_benchmark_overview.(png|svg)`
     - `legacy_benchmark_drug_mae.(png|svg)`
     - `legacy_benchmark_confidence_intervals.(png|svg)`
     - `legacy_benchmark_top_errors.(png|svg)`
     - `legacy_benchmark_calibration.(png|svg)`
     - `legacy_benchmark_subgroup_variability.(png|svg)`
     - `platform_positioning_comparison.(png|svg)`
7. `evaluate/generate_legacy_uncertainty_figures.py`
   - generates the manuscript-quality uncertainty and applicability figure set
   - expected input: uncertainty-analysis outputs under `models/evaluation/legacy_pic50_baseline/`
   - expected outputs:
     - `legacy_benchmark_uncertainty.(png|svg)`
     - `legacy_benchmark_applicability.(png|svg)`
     - `uncertainty_figure_set_note.md`
8. `evaluate/design_legacy_benchmark_splits.py`
   - generates deterministic split registries for stronger leakage-safe benchmark regimes
   - expected input: `configs/models/legacy-pic50-leakage-safe-benchmark-design.json` plus the preserved GDSC response table
   - expected outputs:
     - `models/evaluation/benchmark_design/gdsc_split_registry.tsv`
     - `models/evaluation/benchmark_design/benchmark_split_design_summary.json`
     - `models/evaluation/benchmark_design/benchmark_split_regime_counts.tsv`
9. `evaluate/run_legacy_leakage_safe_benchmarks.py`
   - trains and evaluates the saved split regimes using the legacy Random Forest baseline and configured comparator models
   - expected input:
     - `configs/models/legacy-pic50-leakage-safe-runner.json`
     - `models/evaluation/benchmark_design/gdsc_split_registry.tsv`
     - preserved GDSC response and omics tables
   - expected outputs:
     - `models/evaluation/leakage_safe_regimes/fold_metrics.tsv`
     - `models/evaluation/leakage_safe_regimes/regime_summary.tsv`
     - `models/evaluation/leakage_safe_regimes/regime_predictions.tsv`
     - `models/evaluation/leakage_safe_regimes/regime_benchmark_summary.json`

## Recommended Run Order

Use the scripts in this order:

1. `python3 scripts/evaluate/benchmark_reproducibility_check.py`
2. `python3 scripts/evaluate/prepare_ccle_cross_domain_response.py`
3. `python3 scripts/evaluate/run_legacy_benchmark_baseline.py`
4. `python3 scripts/evaluate/analyze_legacy_benchmark_subgroups.py`
5. `python3 scripts/evaluate/analyze_legacy_benchmark_uncertainty.py`
6. `python3 scripts/evaluate/generate_legacy_benchmark_figures.py`
7. `python3 scripts/evaluate/generate_legacy_uncertainty_figures.py`
8. `python3 scripts/evaluate/design_legacy_benchmark_splits.py`
9. `python3 scripts/evaluate/run_legacy_leakage_safe_benchmarks.py`

Optional overrides supported by the maintained evaluation scripts:

- `--config /path/to/config.json`
- `--output-dir /path/to/output-dir`
- `PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR=/path/to/output-dir`

## Environment Assumptions

- Python environment should include the maintained service/benchmark dependencies.
- The legacy runtime artifacts must remain available at the paths described in `configs/models/legacy-pic50-artifacts.json`.
- The evaluation layer is designed to emit stable machine-readable outputs and short run summaries only; exploratory notebook-style printing should not be added back into these scripts.
- The uncertainty/applicability layer is still a first-pass analysis. Its outputs are manuscript-support artifacts and should not yet be treated as calibrated public prediction intervals.
- The split-design layer creates saved benchmark regimes and reporting artifacts. The staged `ridge` execution has completed across all saved regimes; full multi-model execution remains pending.
- Full leakage-safe regime execution is substantially heavier than the baseline benchmark and should be run from the benchmark virtual environment, using `--models` and `--regimes` to validate subsets before launching larger model matrices.

## Directory Maturity

- `evaluate/`: maintained and manuscript-linked
- `setup/`: scaffolding only
- `ingest/`: scaffolding only
- `train/`: scaffolding only
- `release/`: scaffolding only

The scaffold directories exist for future work and should not be treated as production-ready pipelines yet.
