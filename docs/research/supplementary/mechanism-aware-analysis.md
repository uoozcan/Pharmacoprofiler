# Mechanism-Aware Analysis

## Purpose

This note records the first mechanism-aware extension of the canonical legacy benchmark. It links benchmark-drug performance to the verified merged compound-target annotation table from the legacy workspace.

## Analysis scope

The current mechanism layer uses:

- `models/evaluation/legacy_pic50_baseline/drug_metrics.tsv`
- `/home/umut/projects/pharmacoprofiler_legacy/Merged_all_platforms_compound_file_drug_target_update_v8.csv`

The merged compound table contributes:

- benchmark-drug to compound-name matching
- broad compound-class annotations
- target-list strings
- target-count context for each drug

This analysis is intended as an interpretation layer for the benchmark overlap set, not as proof that the model has learned or recovered true biological mechanisms.

## Canonical outputs

Generated outputs are stored under `models/evaluation/legacy_pic50_baseline/`:

- `mechanism_annotated_drug_metrics.tsv`
- `mechanism_class_metrics.tsv`
- `mechanism_analysis_summary.json`

Generated figure assets are stored under `docs/research/figures/`:

- `legacy_benchmark_mechanism_overview.(png|svg)`
- `mechanism_figure_set_note.md`

## Current findings

### Mapping coverage

The current mechanism-aware pass maps all `16` benchmark drugs to the verified merged compound-target table.

Compound-class distribution in the overlap set is:

- `10` kinase inhibitors
- `3` transporter inhibitors
- `1` ion channel inhibitor
- `1` cytosolic inhibitor
- `1` epigenetic regulator inhibitor

### Class-level benchmark behavior

Mean benchmark error varies across the current class labels:

- `Transporter inhibitors`: mean MAE `1.1563`
- `Ion channel inhibitors`: mean MAE `0.6603`
- `Cytosolic inhibitors`: mean MAE `0.6131`
- `Kinase inhibitors`: mean MAE `0.5738`
- `Epigenetic regulator inhibitors`: mean MAE `0.2971`

The mapped worst-MAE drug is `irinotecan` (`MAE = 1.6631`), which is labeled in the merged table as a transporter inhibitor. The broadest-target annotated drug is `sorafenib` with `535` listed targets and `MAE = 0.3830`.

### Polypharmacology context

The current overlap set contains both narrowly and broadly annotated compounds:

- `pd0325901`: `1` listed target
- `selumetinib`: `26` listed targets
- `sorafenib`: `535` listed targets
- `erlotinib`: `512` listed targets

This supports a manuscript-safe interpretation that the benchmark covers drugs with markedly different apparent target breadth. However, target breadth alone should not be presented as a causal explanation of model performance.

## Manuscript-safe wording

`A mechanism-aware annotation pass mapped all benchmark-overlap drugs to a verified merged compound-target table, showing that the current benchmark spans multiple broad mechanism classes and both narrow- and broad-target compounds, with transporter-labeled compounds showing higher mean error than kinase-labeled compounds in this preserved overlap set.`

`These annotations improve interpretability and reviewer-facing biological context, but they should be framed as a benchmark annotation layer rather than as proof that the model has learned mechanistic relationships.`

## Cautions

1. The broad compound classes come from a preserved merged annotation table and should be treated as legacy-derived labels, not as newly validated ontology assignments.
2. Individual target previews can be noisy for polypharmacologic compounds and should be used illustratively rather than as definitive single-target statements.
3. The overlap set contains only `16` benchmark drugs, so class-level conclusions should remain descriptive and conservative.
