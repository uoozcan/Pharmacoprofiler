# Benchmark Reproducibility Baseline

## Purpose

This document fixes the immediate reproducibility gap around the legacy pIC50 benchmark by naming the verified training logic, runtime artifacts, and the minimum checks required before reporting any metric.

## Verified baseline

### Core training script
- `pharmacoprofiler_legacy/CLRB_MODELLING/GDSC_CCLE_cross_domain_mode_7.py`

Verified behavior from code:
- load GDSC response table with precomputed fingerprints
- load CCLE response table for external testing
- load GDSC and CCLE 3,747-feature omics matrices
- concatenate omics vectors with 1,024-bit fingerprints
- train `RandomForestRegressor(max_depth=81, n_estimators=100, random_state=2)`
- report MAE, MSE, RMSE, Spearman, Pearson, and R-squared on CCLE

### Verified deployed artifact set

Artifact metadata is recorded in `configs/models/legacy-pic50-artifacts.json`.

The verified asset hashes are:
- omics matrix: `fe40965ae3d66fc7f706c7e38eb0a82b3bf42578f5b0edafeeb450289e353a97`
- cell line metadata: `87adf390014b5a9e16aa8d2ce1c3269c595417977212f13ff8d98f665bebf4b4`
- model file: `4058dfd341dd3b713da0885a9fe4e3f1b25ace0518fa900705cb8f48ef49bcf5`

## Immediate reproducibility fixes

1. Do not cite manuscript placeholder metrics as final benchmark results.
2. Treat `GDSC_CCLE_cross_domain_mode_7.py` as the current code-grounded benchmark baseline.
3. Verify artifact hashes before rerunning or reporting results.
4. Record split policy explicitly as:
   - train domain: GDSC
   - external test domain: CCLE
   - model family: Random Forest
   - feature schema: 3,747 omics + 1,024 ECFP4
5. Re-run metrics into a versioned report before using them in figures or manuscript text.

## Reproducibility command

Use:

```bash
python3 scripts/evaluate/benchmark_reproducibility_check.py
```

This verifies that the expected legacy runtime artifacts still match the documented hashes and sizes, even when the preserved model file lives under the legacy Hugging Face packaging subtree.

## Known benchmark limitations

- the current benchmark script is dataset-transfer based, not a modern leakage-safe benchmark suite
- no confidence intervals are generated in the current legacy code
- no baseline-model comparison is currently packaged in the repo
- metric output files referenced in the training script are not yet promoted into canonical current-repo reports
- the original prepared CCLE cross-domain response file is absent from the preserved legacy workspace and must currently be reconstructed from raw CCLE response records plus GDSC fingerprint mappings

## Next required benchmark step

Run the packaged evaluation workflow:

```bash
python3 scripts/evaluate/run_legacy_benchmark_baseline.py
```

Then generate subgroup diagnostics from the same benchmark outputs:

```bash
python3 scripts/evaluate/analyze_legacy_benchmark_subgroups.py
```

This command writes canonical outputs to `models/evaluation/legacy_pic50_baseline/`. In restricted environments where that path is not writable, the scripts fall back to `/tmp/pharmacoprofiler_outputs/legacy_pic50_baseline/`.

The first packaged version preserves the current legacy baseline while adding:
- explicit saved splits
- versioned metric outputs
- a machine-readable benchmark summary
- reconstructed CCLE benchmark input provenance when the original prepared file is absent

Confidence intervals and baseline comparisons remain phase-two benchmark tasks after the baseline rerun is stabilized.

See [benchmark-input-reconstruction.md](benchmark-input-reconstruction.md) for the current overlap counts and reconstructed input summary.

## Current generated baseline outputs

The current repository now has generated baseline benchmark outputs in:

- `models/evaluation/legacy_pic50_baseline/benchmark_summary.json`
- `models/evaluation/legacy_pic50_baseline/metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_predictions.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_response_reconstruction_summary.json`
- `models/evaluation/legacy_pic50_baseline/subgroup_analysis_summary.json`
- `models/evaluation/legacy_pic50_baseline/drug_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics_raw.tsv`
- `models/evaluation/legacy_pic50_baseline/tissue_metrics_normalized.tsv`
- `models/evaluation/legacy_pic50_baseline/potency_bin_metrics.tsv`
- `models/evaluation/legacy_pic50_baseline/top_error_examples.tsv`

The current packaged run produced:

- Pearson `0.7556`
- Spearman `0.6273`
- MAE `0.6548`
- RMSE `0.8361`
- R² `0.2633`

See [benchmark-baseline-interpretation.md](benchmark-baseline-interpretation.md) for the narrative interpretation and compatibility caveats.
See [benchmark-subgroup-analysis.md](benchmark-subgroup-analysis.md) for subgroup-level error and calibration diagnostics.
See [benchmark-reporting-standard.md](benchmark-reporting-standard.md) for the required reporting bundle and stage definitions.
