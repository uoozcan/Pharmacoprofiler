# Project Notebook

## Purpose

This file is the running project notebook for repository restructuring, benchmark hardening, manuscript correction, and publishability work. It should be updated as substantive project changes are made so the current state does not depend on chat history.

## 2026-04-02

### Publishability and benchmark foundation

- preserved the verified legacy predictor as the current baseline
- added canonical benchmark outputs under `models/evaluation/legacy_pic50_baseline/`
- documented reconstructed CCLE benchmark lineage and baseline metrics
- added subgroup, calibration, potency-bin, and failure-case analyses

### Tissue normalization

- introduced a reporting-layer tissue vocabulary in `configs/datasets/tissue_vocabulary.tsv`
- normalized obvious reporting duplicates:
  - `Colon` -> `large_intestine`
  - `Soft Tissue` -> `soft_tissue`
- kept `pleura`, `pleural_effusion`, and `pericardial_effusion` distinct pending source-level review
- documented the policy in `docs/datasets/tissue-normalization.md`

### Manuscript evidence package

- added `docs/research/manuscript/normalization-and-benchmark-evidence.md`
- added `docs/research/supplementary/benchmark-reporting-standard.md`
- updated manuscript and reviewer-facing docs to cite normalized subgroup outputs and calibration caveats

### Notebook-grounded methods work

- reviewed decisive legacy notebooks for:
  - GDSC1 and GDSC2 response preparation
  - CCLE NP24 and GNF preprocessing
  - FIMM IC50 recovery and pIC50 conversion
  - NCI-60 pGI50 handling
  - NCATS wide-to-long reshaping
  - Cellosaurus-based harmonization
  - fingerprint generation and predictor input assembly
- added `docs/research/notebooks/notebook-methods-evidence-matrix.md`
- added `docs/research/manuscript/preprocessing-methods-from-notebooks.md`

### Current methods boundaries

- source-specific response preprocessing is now notebook-grounded
- cell-line and compound harmonization are notebook-grounded but still partly manual and dictionary-based
- predictor input assembly is notebook- and script-grounded
- upstream omics normalization and feature-selection steps remain only partially reconstructed and should continue to be described as preserved provenance rather than verified preprocessing

### Next recommended steps

1. turn the notebook-derived preprocessing note into final manuscript section text
2. generate manuscript-ready figures from the canonical benchmark outputs
3. add leakage-safe benchmark regimes and baseline-model comparisons
4. decide whether to expose normalized tissue fields in downstream service or export layers as additive metadata

### Script cleanup and utility hardening

- added a shared evaluation helper layer in `scripts/evaluate/_common.py` for config loading, output-dir resolution, token normalization, and artifact resolution
- aligned the maintained benchmark scripts around a clearer CLI pattern with explicit config and output-dir overrides where applicable
- tightened script boundaries:
  - artifact verification remains isolated in `benchmark_reproducibility_check.py`
  - CCLE reconstruction remains isolated in `prepare_ccle_cross_domain_response.py`
  - baseline execution remains isolated in `run_legacy_benchmark_baseline.py`
  - subgroup analysis remains isolated in `analyze_legacy_benchmark_subgroups.py`
- cleaned `services/prediction-api/app.py` so request parsing and response metadata are centralized at the HTTP layer
- cleaned `services/prediction-api/predictor.py` so asset loading, metadata construction, valid-compound filtering, and feature assembly are more explicit
- expanded API contract coverage for degraded info, `smiles_list`, single-SMILES prediction, max-request enforcement, and invalid-SMILES reporting
- added lightweight unit coverage for the shared benchmark helper module

### Current script maturity

- canonical maintained scripts:
  - `scripts/evaluate/*`
  - `services/prediction-api/app.py`
  - `services/prediction-api/predictor.py`
  - `tests/api/test_prediction_api_contract.py`
- preserved legacy reference:
  - `services/prediction-api/legacy_verified/`
- scaffolding only:
  - `scripts/setup/`
  - `scripts/ingest/`
  - `scripts/train/`
  - `scripts/release/`

### Hugging Face alignment

- reviewed the live Space page and public app endpoints on `2026-04-02`
- confirmed the live public service is healthy and returns `988` predictions for a valid single-SMILES request
- confirmed the live Space metadata is inaccurate:
  - `sdk: gradio` even though the deployment is Flask + Docker
  - request-limit docs drift from the actual `MAX_SMILES_PER_REQUEST=10` runtime assumption
- confirmed live public JSON can expose missing tissue metadata as raw `NaN`
- updated the maintained predictor to sanitize missing tissue metadata to empty string at the canonical service layer
- added repo-side Hugging Face sync templates:
  - `services/prediction-api/HF_SPACE_README.md`
  - `services/prediction-api/HF_SPACE_Dockerfile`
- added `docs/research/supplementary/huggingface-space-parity.md` as the operational parity note

## 2026-04-03

### Benchmark figure package

- added `scripts/evaluate/generate_legacy_benchmark_figures.py` as the canonical figure generator for the current benchmark baseline
- generated manuscript-quality benchmark figures under `docs/research/figures/` in both PNG and SVG formats
- added figure support files:
  - `docs/research/figures/benchmark_figure_set_note.md`
  - `docs/research/figures/figure_legends_and_mapping.md`
  - `docs/research/figures/platform_positioning_matrix.tsv`

### Figure-linked manuscript revision

- updated `docs/research/manuscript/canonical-manuscript-draft.md` so the Results baseline now cites the generated figure set directly
- added figure-placement guidance for primary and supplemental figure order
- updated `docs/research/manuscript/methods-verified-baseline.md` with figure-linked reporting guidance so benchmark numbers and limitations are tied to canonical figure outputs rather than floating prose

### Current figure priorities

- primary manuscript figures:
  - Figure 1: legacy benchmark overview
  - Figure 5: calibration detail
  - Figure 6: subgroup variability
  - Figure 7: competitive positioning comparison
- supplemental benchmark support:
  - Figure 3: bootstrap confidence intervals
  - Figure 2: drug-level variability
  - Figure 4: top-error examples

### Next recommended steps

1. insert figure callouts into the manuscript text section-by-section during the full revision pass
2. convert the figure set into final journal-style legends and caption formatting if target-journal guidance is chosen
3. use the canonical benchmark outputs and figure set to design the next scientific figure round for leakage-safe benchmarking, uncertainty, or mechanism-aware analysis

### Uncertainty and applicability analysis

- added `scripts/evaluate/analyze_legacy_benchmark_uncertainty.py` for the first uncertainty/applicability analysis pass on the canonical benchmark
- added `scripts/evaluate/generate_legacy_uncertainty_figures.py` for manuscript-quality uncertainty and applicability figures
- generated canonical outputs:
  - `models/evaluation/legacy_pic50_baseline/ccle_predictions_with_uncertainty.tsv`
  - `models/evaluation/legacy_pic50_baseline/uncertainty_bin_metrics.tsv`
  - `models/evaluation/legacy_pic50_baseline/applicability_bin_metrics.tsv`
  - `models/evaluation/legacy_pic50_baseline/cell_line_applicability_metrics.tsv`
  - `models/evaluation/legacy_pic50_baseline/uncertainty_applicability_summary.json`
- generated figure assets:
  - `docs/research/figures/legacy_benchmark_uncertainty.(png|svg)`
  - `docs/research/figures/legacy_benchmark_applicability.(png|svg)`
  - `docs/research/figures/uncertainty_figure_set_note.md`
- recorded manuscript-facing interpretation in `docs/research/supplementary/uncertainty-applicability-analysis.md`

### Current uncertainty findings

- per-sample tree prediction spread is informative but only moderately correlated with absolute error:
  - mean prediction SD `0.6032`
  - Pearson correlation with absolute error `0.2273`
- nominal tree-based 90% intervals under-cover the benchmark set:
  - empirical coverage `0.7371`
- nearest-train cell-line cosine similarity is directionally informative but weaker:
  - Pearson correlation with cell-line MAE `-0.0916`

### Mechanism-aware analysis

- added `scripts/evaluate/analyze_legacy_benchmark_mechanisms.py` to annotate the benchmark-overlap drugs with verified legacy compound-target metadata
- added `scripts/evaluate/generate_legacy_mechanism_figures.py` for the manuscript-quality mechanism overview figure
- generated canonical outputs:
  - `models/evaluation/legacy_pic50_baseline/mechanism_annotated_drug_metrics.tsv`
  - `models/evaluation/legacy_pic50_baseline/mechanism_class_metrics.tsv`
  - `models/evaluation/legacy_pic50_baseline/mechanism_analysis_summary.json`
- generated figure assets:
  - `docs/research/figures/legacy_benchmark_mechanism_overview.(png|svg)`
  - `docs/research/figures/mechanism_figure_set_note.md`
- recorded manuscript-facing interpretation in `docs/research/supplementary/mechanism-aware-analysis.md`

### Current mechanism findings

- all `16` benchmark-overlap drugs now map to the verified merged compound-target table
- the overlap is dominated by kinase inhibitors (`10` of `16`) but also includes transporter, ion-channel, cytosolic, and epigenetic regulator classes
- transporter-labeled compounds show the highest mean MAE in the preserved overlap set (`1.1563`)
- the mechanism layer is useful for biological interpretation and prioritization, but not yet for causal claims about what the model has learned

### Leakage-safe benchmark design

- added `configs/models/legacy-pic50-leakage-safe-benchmark-design.json`
- added `scripts/evaluate/design_legacy_benchmark_splits.py` to generate deterministic saved split registries from the preserved GDSC response table
- generated canonical Stage 3 design outputs:
  - `models/evaluation/benchmark_design/gdsc_split_registry.tsv`
  - `models/evaluation/benchmark_design/benchmark_split_design_summary.json`
  - `models/evaluation/benchmark_design/benchmark_split_regime_counts.tsv`
- added manuscript/support note `docs/research/supplementary/leakage-safe-benchmark-design.md`

### Current split-design findings

- preserved GDSC training table size for split design:
  - `337761` rows
  - `403` drugs
  - `986` cell lines
- deterministic saved regimes now exist for:
  - pair-random comparison
  - compound holdout
  - cell-line holdout
  - double-cold-start
- double-cold-start currently yields `67675` eligible test rows across the five folds, with per-fold test sizes between `13302` and `13924`

### Leakage-safe regime runner

- added `configs/models/legacy-pic50-leakage-safe-runner.json`
- added `scripts/evaluate/run_legacy_leakage_safe_benchmarks.py`
- added unit coverage in `tests/unit/test_leakage_safe_runner.py`
- the runner now supports targeted execution with:
  - `--models`
  - `--regimes`
- full regime execution is substantially heavier than the baseline benchmark and should be treated as a separate compute step, not a quick manuscript-support script
- the first full `ridge` sweep across all saved regimes was launched from `/home/umut/projects/pharmacoprofiler/.venv-benchmark/bin/python`
- the maintained runner now writes fold metrics, regime summaries, predictions, and benchmark JSON after each completed regime so future long runs are inspectable before final completion
- the `ridge` path was refactored to avoid materializing the full `337k x 4771` design matrix in memory
- current staged execution uses chunked feature assembly and chunked ridge fitting, and the isolated `pair_random` rerun is now progressing with low memory use rather than the earlier near-OOM behavior
- the first staged `ridge` regime (`pair_random`) completed and wrote:
  - `models/evaluation/leakage_safe_regimes/fold_metrics.tsv`
  - `models/evaluation/leakage_safe_regimes/regime_predictions.tsv`
  - `models/evaluation/leakage_safe_regimes/regime_summary.tsv`
  - `models/evaluation/leakage_safe_regimes/regime_benchmark_summary.json`
- current `pair_random` ridge summary:
  - folds: `5`
  - total test rows: `337761`
  - mean MAE: `0.4056`
  - mean RMSE: `0.5428`
  - mean Pearson `r`: `0.8818`
  - mean Spearman `r`: `0.8564`
  - mean R²: `0.7775`
- the next staged `ridge` regime (`compound_holdout`) was launched with a regime-specific output directory:
  - `models/evaluation/leakage_safe_regimes/ridge_compound_holdout/`
- the full staged `ridge` sweep is now complete across:
  - `pair_random`
  - `compound_holdout`
  - `cell_line_holdout`
  - `double_cold_start`
- canonical aggregated comparison:
  - `models/evaluation/leakage_safe_regimes/ridge_regime_comparison.tsv`
- current leakage-sensitive interpretation:
  - unseen-cell-line generalization remains materially stronger than unseen-compound generalization
  - `compound_holdout` and `double_cold_start` are the main conservative benchmark regimes for manuscript limitation framing

### Manuscript-support packaging

- added `docs/research/supplementary/benchmark-results-index.md` as the single entry point for the benchmark evidence package
- added `docs/research/figures/primary-figure-captions.md` as the compact caption set for the current recommended main-text figures
- updated manuscript and research index docs so the leakage-safe ridge comparison sits inside the same evidence chain as the earlier baseline, calibration, subgroup, uncertainty, and mechanism notes

### Current unresolved limitations

- the legacy RF leakage-safe comparator remains pending; the attempted `rf_pair_random` run produced no result files and should not be cited
- the current leakage-safe benchmark evidence is ridge-only, so a multi-model regime comparison remains future work
- uncertainty/applicability outputs are exploratory and should not be described as calibrated predictive intervals
- upstream omics normalization and feature-selection provenance is still only partially reconstructed from notebooks
- broader multi-dataset harmonization is preserved as notebook provenance, not yet a packaged end-to-end pipeline
- direct verification of the `pharmacoprofiler.com` frontend/runtime remains incomplete from this environment
- `pharmacoprofiler_presentation.html` is treated as a local-only export artifact and is now ignored unless intentionally promoted into the repository later
