# Leakage-Safe Model Comparison Shell

## Purpose

This note records the current multi-model comparison shell for the leakage-safe benchmark package. It exists so the project can track completed and pending model-regime outputs without promoting incomplete comparator runs into the manuscript evidence package.

## Canonical shell artifacts

- `models/evaluation/leakage_safe_regimes/multi_model_regime_comparison.tsv`
- `models/evaluation/leakage_safe_regimes/multi_model_regime_status.json`

## Current state

The aggregated comparison shell currently contains the completed staged `ridge` rows only. The generated status JSON marks `ridge` as complete and both `ols` and `legacy_rf` as pending.

The first `ols` regime output has now landed for `pair_random`, and its summary is effectively identical to the completed ridge `pair_random` result (MAE `0.4056`, RMSE `0.5428`, Pearson `0.8818`, `R² = 0.7775`). That result is useful as a progress check, but it is not enough to promote `ols` into the manuscript evidence package because the stricter leakage-safe regimes are still incomplete.

Current shell summary:

- completed models:
  - `ridge`
- pending models:
  - `ols`
  - `legacy_rf`

## Manuscript-use rule

This shell should be treated as a coordination artifact, not as direct manuscript evidence, until at least one second comparator has finished cleanly across the full saved regime set. Until then:

1. cite `ridge_regime_comparison.tsv` and the ridge figure/table for manuscript claims
2. use `multi_model_regime_status.json` only to document benchmark progress
3. do not cite `ols` or `legacy_rf` leakage-safe results until completed `regime_summary.tsv` outputs exist

## Next step

When the first completed `ols` regime summary lands, rerun:

`python3 scripts/evaluate/build_leakage_safe_model_comparison.py`

Then regenerate the benchmark figure set. The optional multi-model leakage-safe figure will activate automatically only after the aggregated comparison TSV contains at least two models with all four saved regimes completed.
