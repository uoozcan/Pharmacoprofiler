# Leakage-Safe Benchmark Execution Plan

## Purpose

This note defines the practical execution order for the leakage-safe benchmark runner. The goal is to separate manageable comparator runs from the substantially heavier Random Forest sweeps.

## Stage 1: ridge sweep across all saved regimes

Run first:

```bash
/home/umut/projects/pharmacoprofiler/.venv-benchmark/bin/python \
  scripts/evaluate/run_legacy_leakage_safe_benchmarks.py \
  --models ridge
```

Purpose:

- validate end-to-end use of the saved split registry
- generate the first full regime comparison table
- provide a low-cost baseline comparator before the Random Forest sweeps

Required outputs:

- `models/evaluation/leakage_safe_regimes/fold_metrics.tsv`
- `models/evaluation/leakage_safe_regimes/regime_summary.tsv`
- `models/evaluation/leakage_safe_regimes/regime_predictions.tsv`
- `models/evaluation/leakage_safe_regimes/regime_benchmark_summary.json`

Operational note:

- the first full ridge sweep was launched on `2026-04-03` in the benchmark venv
- leakage-safe regime execution is materially heavier than the earlier CCLE transfer benchmark
- the maintained runner now writes outputs after each completed regime, so reruns are easier to monitor than the initial launch
- the maintained ridge path now uses chunked feature assembly and chunked fitting so staged `ridge` runs do not require the full design matrix in memory
- current recommended execution style is staged by regime:
  1. `pair_random`
  2. `compound_holdout`
  3. `cell_line_holdout`
  4. `double_cold_start`
- use a regime-specific output directory for staged reruns whenever a prior regime has already completed, for example:
  - `models/evaluation/leakage_safe_regimes/ridge_compound_holdout/`
  - `models/evaluation/leakage_safe_regimes/ridge_cell_line_holdout/`
  - `models/evaluation/leakage_safe_regimes/ridge_double_cold_start/`
- first completed staged result:
  - regime: `pair_random`
  - model: `ridge`
  - folds: `5`
  - total test rows: `337761`
  - mean MAE: `0.4056`
  - mean RMSE: `0.5428`
  - mean Pearson `r`: `0.8818`
  - mean Spearman `r`: `0.8564`
  - mean R²: `0.7775`

## Stage 2: targeted legacy Random Forest validation

Run next:

```bash
/home/umut/projects/pharmacoprofiler/.venv-benchmark/bin/python \
  scripts/evaluate/run_legacy_leakage_safe_benchmarks.py \
  --models legacy_rf \
  --regimes pair_random,compound_holdout
```

Purpose:

- validate the legacy model under the lightest and most interpretable regimes first
- establish whether RF retains an advantage over ridge when compounds are held out

## Stage 3: remaining high-rigor RF regimes

Run after Stage 2 is complete:

```bash
/home/umut/projects/pharmacoprofiler/.venv-benchmark/bin/python \
  scripts/evaluate/run_legacy_leakage_safe_benchmarks.py \
  --models legacy_rf \
  --regimes cell_line_holdout,double_cold_start
```

Purpose:

- measure the strongest within-dataset leakage-safe regimes
- provide the manuscript-facing high-rigor RF results

## Interpretation order

Results should be interpreted in this order:

1. `pair_random`
   - permissive comparator only
2. `compound_holdout`
   - unseen-drug generalization
3. `cell_line_holdout`
   - unseen-cell-line generalization
4. `double_cold_start`
   - strongest current within-dataset generalization test

## Reporting rule

No stronger generalization claim should be made until:

1. the current completed ridge sweep is cited as a comparator-only leakage-sensitive result
2. at least one additional model comparator completes under the same saved split registry
3. regime-level summaries for any additional comparator are linked back into manuscript and reviewer-response docs

The attempted legacy RF `pair_random` run produced no result files and is not part of the current manuscript evidence package.
