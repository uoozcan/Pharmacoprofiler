# Uncertainty and Applicability Figure Set

## Included figures

- `legacy_benchmark_uncertainty.(png|svg)`: relationship between ensemble spread, error, and empirical interval behavior
- `legacy_benchmark_applicability.(png|svg)`: relationship between nearest-train cell-line similarity, benchmark error, and uncertainty

## Figure-safe messages

- The preserved Random Forest baseline already exposes a usable uncertainty proxy through per-tree prediction spread.
- Higher ensemble spread is associated with larger absolute benchmark error, with Pearson `r = 0.227`.
- The nominal 90% tree interval should be presented as an internal uncertainty heuristic rather than as a fully calibrated predictive interval.
- A simple applicability proxy based on nearest GDSC cell-line cosine similarity shows that CCLE cell lines farther from the GDSC training manifold tend to have worse benchmark error, with Pearson `r = -0.092`.

## Canonical artifact source

All values and plots in this figure set are generated directly from `models/evaluation/legacy_pic50_baseline/`.
