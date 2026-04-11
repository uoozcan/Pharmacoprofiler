# Leakage-Safe Benchmark Results

## Purpose

This note records the first completed leakage-safe benchmark comparison generated from the staged `ridge` runs. It should be used as the canonical manuscript-support source for the leakage-sensitive generalization story until additional comparator models are run under the same saved split registry.

## Canonical comparison file

- `models/evaluation/leakage_safe_regimes/ridge_regime_comparison.tsv`

Per-regime output directories:

- `models/evaluation/leakage_safe_regimes/`
- `models/evaluation/leakage_safe_regimes/ridge_compound_holdout/`
- `models/evaluation/leakage_safe_regimes/ridge_cell_line_holdout/`
- `models/evaluation/leakage_safe_regimes/ridge_double_cold_start/`

## Summary of the completed ridge sweep

| Regime | Meaning | Test rows | MAE | RMSE | Pearson r | Spearman r | R^2 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `pair_random` | permissive row-random comparator | 337,761 | 0.4056 | 0.5428 | 0.8818 | 0.8564 | 0.7775 |
| `compound_holdout` | unseen-drug generalization | 337,761 | 0.9037 | 1.1523 | 0.4115 | 0.3778 | -0.0353 |
| `cell_line_holdout` | unseen-cell-line generalization | 337,761 | 0.4767 | 0.6267 | 0.8402 | 0.8022 | 0.7033 |
| `double_cold_start` | unseen drug and unseen cell line in same fold | 67,675 | 0.9363 | 1.1923 | 0.3682 | 0.3319 | -0.1093 |

## Manuscript-safe interpretation

The completed ridge sweep shows that the preserved GDSC table contains strong leakage-sensitive performance differences across split regimes. The row-random comparator remains strong, but performance drops sharply when compounds are held out and drops further under the double-cold-start setting. In contrast, unseen-cell-line generalization remains materially better than unseen-compound generalization.

This pattern supports a conservative benchmark narrative:

1. `pair_random` is useful only as a permissive comparator.
2. `cell_line_holdout` shows that the feature representation still transfers reasonably across unseen cell lines within GDSC.
3. `compound_holdout` shows that generalization to unseen drugs is much weaker.
4. `double_cold_start` should be treated as the strongest current within-dataset generalization test and the most conservative ridge result.

The key manuscript claim supported by these outputs is that the main leakage-sensitive weakness of the current baseline is drug novelty rather than cell-line novelty. This should be stated directly instead of relying only on the easier row-random benchmark.

## Wording for the Results section

Suggested manuscript-safe wording:

> Leakage-sensitive benchmarking showed a large regime-dependent performance gap. While the staged ridge baseline remained strong under permissive pair-random splits (MAE 0.4056, R^2 0.7775), performance declined substantially when compounds were held out (MAE 0.9037, R^2 -0.0353). By contrast, unseen-cell-line performance was materially stronger (MAE 0.4767, R^2 0.7033), indicating that drug novelty is a harder generalization axis than cell-line novelty in the preserved GDSC setting. The strictest double-cold-start regime produced the weakest result (MAE 0.9363, R^2 -0.1093), supporting its use as the most conservative current within-dataset benchmark.

## Reviewer-facing value

This result addresses the main benchmarking criticism more directly than the earlier reconstructed CCLE baseline alone because it makes the split policy explicit and shows how much performance changes once leakage-sensitive regimes are enforced.

## Companion artifacts

- Figure panel: `docs/research/figures/legacy_benchmark_leakage_safe_regimes.(png|svg)`
- Supplementary table: `docs/research/supplementary/leakage-safe-ridge-regime-table.md`

## Remaining next steps

1. keep the legacy RF comparator marked pending because the attempted `rf_pair_random` run produced no result files
2. extend the leakage-safe comparison from ridge-only into a multi-model figure and table
3. rerun an additional comparator only after the current publication package is stable and the compute budget/runtime strategy is chosen
