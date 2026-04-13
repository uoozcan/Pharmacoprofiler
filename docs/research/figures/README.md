# Figures

This directory holds canonical figure notes and small, tracked figure assets that are still relevant to the manuscript revision effort.

Use `archive/legacy-manuscript-materials/` for exploratory, duplicated, or non-canonical visual material.

## Current Canonical Figure Set

- `legacy_benchmark_overview.(png|svg)`: four-panel benchmark summary generated from the canonical legacy baseline outputs
- `legacy_benchmark_drug_mae.(png|svg)`: compound-level MAE ranking for the preserved cross-domain overlap set
- `legacy_benchmark_confidence_intervals.(png|svg)`: bootstrap confidence-interval summary for the core benchmark metrics
- `legacy_benchmark_top_errors.(png|svg)`: largest benchmark failure cases, annotated by tissue context
- `legacy_benchmark_calibration.(png|svg)`: detailed calibration figure with decile residual structure
- `legacy_benchmark_subgroup_variability.(png|svg)`: combined tissue/drug subgroup variability view
- `legacy_benchmark_leakage_safe_regimes.(png|svg)`: staged ridge comparison across leakage-sensitive split regimes
- `legacy_benchmark_uncertainty.(png|svg)`: ensemble-spread uncertainty and interval-behavior summary
- `legacy_benchmark_applicability.(png|svg)`: cell-line similarity applicability proxy versus benchmark error
- `legacy_benchmark_uncertainty_calibration.(png|svg)`: nominal-versus-empirical interval coverage and descriptive post hoc inflation summary
- `legacy_benchmark_mechanism_overview.(png|svg)`: mechanism-class and target-breadth context for the benchmark-overlap drugs
- `platform_positioning_comparison.(png|svg)`: competitive positioning heatmap derived from verified repo analysis
- `benchmark_figure_set_note.md`: manuscript-safe messages linked to the generated benchmark figures
- `supplementary-benchmark-captions.md`: compact manuscript-ready captions for supplementary benchmark figures, including Figures 2, 3, 4, and 10
- `uncertainty_figure_set_note.md`: manuscript-safe messages linked to the uncertainty and applicability figures
- `supplementary-uncertainty-captions.md`: compact manuscript-ready captions for Figures 8, 9, and Supplementary Figure S1
- `supplementary-leakage-safe-captions.md`: compact manuscript-ready captions for Figures 11, 12, and the leakage-safe regime tables
- `mechanism_figure_set_note.md`: manuscript-safe messages linked to the mechanism-aware figure
- `figure_legends_and_mapping.md`: manuscript-ready legends and mapping from each figure to manuscript targets and reviewer concerns
- `platform_positioning_matrix.tsv`: tracked source matrix for the strategic positioning figure

Generate or refresh these figures with:

```bash
python3 scripts/evaluate/generate_legacy_benchmark_figures.py
```

Generate or refresh the uncertainty/applicability figures with:

```bash
python3 scripts/evaluate/analyze_legacy_benchmark_uncertainty.py
python3 scripts/evaluate/generate_legacy_uncertainty_figures.py
```

Generate or refresh the mechanism-aware outputs and figure with:

```bash
python3 scripts/evaluate/analyze_legacy_benchmark_mechanisms.py
python3 scripts/evaluate/generate_legacy_mechanism_figures.py
```
