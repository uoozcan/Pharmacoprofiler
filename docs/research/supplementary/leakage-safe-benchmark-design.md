# Leakage-Safe Benchmark Design

## Purpose

This document defines the next benchmark-design layer required before stronger generalization claims are made for PharmacoProfiler. It translates the existing benchmark roadmap into concrete split regimes, saved split artifacts, and interpretation rules.

## Design principles

The current reconstructed GDSC-to-CCLE transfer baseline remains useful, but it is not sufficient for stronger generalization claims because it does not isolate leakage risk across compounds and cell lines within the GDSC training domain.

The new split-design layer therefore separates benchmark regimes by what is held out:

1. `pair_random`
   - conventional row-random split
   - retained only as a permissive comparator
   - not leakage-safe for compounds or cell lines
2. `compound_holdout`
   - entire compounds held out across folds
   - tests generalization to unseen compounds
3. `cell_line_holdout`
   - entire cell lines held out across folds
   - tests generalization to unseen cell lines
4. `double_cold_start`
   - test rows where both compound and cell line are held out for the same fold
   - strongest current leakage-safe design available from the preserved GDSC table

## Canonical outputs

Generated outputs are stored under `models/evaluation/benchmark_design/`:

- `gdsc_split_registry.tsv`
- `benchmark_split_design_summary.json`
- `benchmark_split_regime_counts.tsv`

These files should be treated as the saved split definitions required by Stage 3 of the benchmark reporting standard.

## Current design scope

The split-design generator operates on:

- `pharmacoprofiler_legacy/CLRB_MODELLING/GDSC_drug_response_drugs_w_smiles_988cl_404dr_337K_v4_w_fps.txt`

Using the verified columns:

- `DRUG_NAME_edited`
- `CELL_LINE_NAME_edited`
- `pIC50`
- `FINGERPRINT`

The current generator is deterministic and records its random seeds so later model-comparison runs can reuse the same split identities.

## Interpretation rules

### Pair-random

This regime is allowed only as a baseline comparator. It should never be used for strong novelty or generalization claims because drug and cell-line identities can appear in both train and test folds.

### Compound-holdout

This regime is the minimum benchmark for claims about generalization to unseen compounds.

### Cell-line-holdout

This regime is the minimum benchmark for claims about generalization to unseen cell lines.

### Double-cold-start

This regime is the strongest current within-dataset design and should be the default high-rigor benchmark for future model-comparison tables once runtime support is added.

## Next implementation step

The current repository now has both saved split definitions and a first execution runner:

- `scripts/evaluate/run_legacy_leakage_safe_benchmarks.py`
- `configs/models/legacy-pic50-leakage-safe-runner.json`

This runner supports targeted execution with `--models` and `--regimes`, which is useful because full regime execution is materially more expensive than the current baseline benchmark.

The first completed comparator under the saved regimes is now `ridge`, with canonical results recorded in:

- `models/evaluation/leakage_safe_regimes/ridge_regime_comparison.tsv`
- `docs/research/supplementary/leakage-safe-benchmark-results.md`

The next benchmark implementation pass should:

1. reuse `gdsc_split_registry.tsv` rather than generating new folds ad hoc
2. add at least one additional comparator beyond ridge under the same saved regimes
3. convert the current ridge regime comparison into a manuscript-quality figure
4. extend the reporting bundle with confidence intervals and, where sample sizes permit, subgroup analyses
