# Leakage-Safe Model Comparison Shell

## Purpose

This note records the current multi-model comparison shell for the leakage-safe benchmark package. It now also marks the point where the shell became a completed two-model comparison rather than a progress-only tracker.

## Canonical shell artifacts

- `models/evaluation/leakage_safe_regimes/multi_model_regime_comparison.tsv`
- `models/evaluation/leakage_safe_regimes/multi_model_regime_status.json`

## Current state

The aggregated comparison shell now contains completed staged sweeps for both `ridge` and `ols`. The generated status JSON marks `ridge` and `ols` as complete, with `legacy_rf` still pending.

Current shell summary:

- completed models:
  - `ridge`
  - `ols`
- pending models:
  - `legacy_rf`

The completed `ols` sweep is effectively indistinguishable from the completed `ridge` sweep across all four saved regimes. The two-model comparison therefore strengthens the current leakage-sensitive benchmark story rather than changing it.

## Manuscript-use rule

This shell can now support manuscript-safe two-model leakage-safe benchmarking across `ridge` and `ols`. The remaining boundary is narrower:

1. cite `multi_model_regime_comparison.tsv`, Figure 12, and the multi-model supplementary table for ridge-versus-OLS leakage-safe claims
2. continue to use `multi_model_regime_status.json` to document which comparator families are complete versus pending
3. keep `legacy_rf` out of the manuscript evidence package until completed `regime_summary.tsv` outputs exist

## Next step

Completed next steps:

- reran `python3 scripts/evaluate/build_leakage_safe_model_comparison.py`
- regenerated the benchmark figure set
- activated the multi-model leakage-safe figure after both `ridge` and `ols` completed all four saved regimes

Remaining next step:

- decide whether the `legacy_rf` comparator is worth revisiting or whether the current completed ridge-versus-OLS comparison is sufficient for the manuscript scope
