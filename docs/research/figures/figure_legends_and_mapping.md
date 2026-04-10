# Figure Legends and Mapping

This document provides manuscript-ready legends for the current canonical figure set and maps each figure to the most relevant manuscript paragraph targets and reviewer concerns.

## Figure 1. Legacy benchmark overview

Files:
- `legacy_benchmark_overview.png`
- `legacy_benchmark_overview.svg`

### Legend

**Figure 1. Overview of the verified legacy GDSC-to-CCLE benchmark baseline.**  
Panel A shows predicted versus observed pIC50 values for the reconstructed CCLE evaluation set (`n = 6513`) with a one-to-one reference line. The current baseline achieved Pearson `r = 0.756`, RMSE `0.836`, and `R² = 0.263`. Panel B summarizes absolute error across observed pIC50 bins and shows increasing error at higher observed response values; labels indicate mean signed error within each bin. Panel C shows normalized tissue-group mean absolute error for the highest-error tissue groups among those with at least 50 observations. Panel D shows the signed error distribution, highlighting systematic underprediction with mean signed error `-0.494` and underprediction in `85.0%` of benchmark rows.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Section `4.1 Verified Claims`
  - first quantitative results paragraph introducing the cross-domain benchmark
  - follow-up paragraph on calibration weakness and subgroup heterogeneity
- `normalization-and-benchmark-evidence.md`
  - `Verified benchmark status`
  - `Calibration and limitation summary`

### Reviewer mapping

- Reviewer 1
  - technical rigor
  - reproducibility
  - benchmarking context
- Reviewer 3
  - presentation quality
  - platform evidence clarity

## Figure 2. Drug-level benchmark variability

Files:
- `legacy_benchmark_drug_mae.png`
- `legacy_benchmark_drug_mae.svg`

### Legend

**Figure 2. Drug-level error variability in the preserved cross-domain overlap set.**  
Mean absolute error is shown for each overlapping compound evaluated in the reconstructed CCLE benchmark. The figure highlights that error varies substantially across compounds, with relatively low-error cases such as saracatinib and panobinostat contrasted against high-error cases such as irinotecan, plx4720, and paclitaxel. This panel supports the interpretation that aggregate benchmark metrics mask substantial compound-specific performance heterogeneity.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Section `4.1 Verified Claims`
  - paragraph after the core benchmark numbers introducing compound-level heterogeneity
- `normalization-and-benchmark-evidence.md`
  - `Calibration and limitation summary`

### Reviewer mapping

- Reviewer 1
  - need for stronger benchmarking context
- Reviewer 2
  - need for more biologically meaningful interpretation of result heterogeneity

## Figure 3. Bootstrap confidence intervals

Files:
- `legacy_benchmark_confidence_intervals.png`
- `legacy_benchmark_confidence_intervals.svg`

### Legend

**Figure 3. Bootstrap 95% confidence intervals for the core benchmark metrics.**  
Bootstrap mean estimates and 95% confidence intervals are shown for Pearson correlation, Spearman correlation, MAE, RMSE, and `R²` over the reconstructed CCLE evaluation set. These intervals provide quantitative uncertainty bounds for the current code-backed baseline and should be cited alongside the point estimates in the manuscript rather than relying on single metrics alone.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Section `4.1 Verified Claims`
  - sentence immediately following the core metric paragraph
- `normalization-and-benchmark-evidence.md`
  - `Verified benchmark status`

### Reviewer mapping

- Reviewer 1
  - missing rigor around quantitative reporting
  - insufficient statistical framing of model performance

## Figure 4. Largest benchmark failure cases

Files:
- `legacy_benchmark_top_errors.png`
- `legacy_benchmark_top_errors.svg`

### Legend

**Figure 4. Largest absolute errors in the reconstructed CCLE benchmark.**  
The 12 largest signed prediction errors are shown as cell line–drug pairs, annotated by tissue context. The largest failures are dominated by severe underprediction of high-response examples in haematopoietic and lymphoid tissue, bone marrow, pleural effusion, and pancreas-associated contexts. This panel makes the failure pattern explicit and supports the claim that the current model’s main limitation is compressed dynamic range in stronger-response regions rather than uniformly random error.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Section `4.1 Verified Claims`
  - paragraph introducing representative failure cases and limitations
- `normalization-and-benchmark-evidence.md`
  - `Calibration and limitation summary`

### Reviewer mapping

- Reviewer 1
  - need to state limitations more explicitly
- Reviewer 2
  - need for biologically interpretable examples and stronger discussion of failure modes

## Figure 5. Calibration detail

Files:
- `legacy_benchmark_calibration.png`
- `legacy_benchmark_calibration.svg`

### Legend

**Figure 5. Calibration structure of the verified legacy cross-domain baseline.**  
Panel A shows predicted versus observed pIC50 values together with the one-to-one line, decile means, and the fitted calibration line (`slope = 0.740`, `intercept = 1.007`). Panel B shows mean signed error across observed-response deciles, demonstrating increasing negative bias in stronger-response regions. Together, these panels show that the current baseline retains rank signal while compressing dynamic range and systematically undercalling the highest responses.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Section `4.1 Verified Claims`
  - paragraph devoted to calibration caveats
- `normalization-and-benchmark-evidence.md`
  - `Calibration and limitation summary`

### Reviewer mapping

- Reviewer 1
  - benchmarking rigor
  - insufficient explanation of model weakness

## Figure 6. Tissue and drug subgroup variability

Files:
- `legacy_benchmark_subgroup_variability.png`
- `legacy_benchmark_subgroup_variability.svg`

### Legend

**Figure 6. Subgroup variability across tissue context and compound identity.**  
Panel A summarizes mean absolute error for the largest normalized tissue groups in the benchmark, showing that error varies meaningfully across disease-context groupings. Panel B shows mean signed error across compounds, demonstrating that most drugs are biased toward underprediction, with a small number of exceptions. This figure supports manuscript wording that the current baseline has usable global signal but non-uniform subgroup behavior that must be stated transparently.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Section `4.1 Verified Claims`
  - paragraph on subgroup variability after the main benchmark paragraph
- `normalization-and-benchmark-evidence.md`
  - `Normalized subgroup findings`
  - `Calibration and limitation summary`

### Reviewer mapping

- Reviewer 1
  - missing subgroup context
- Reviewer 2
  - need for more biologically contextualized result interpretation

## Figure 7. Competitive positioning comparison

Files:
- `platform_positioning_comparison.png`
- `platform_positioning_comparison.svg`

### Legend

**Figure 7. Competitive positioning of Pharmacoprofiler relative to representative pharmacogenomics resources.**  
The matrix summarizes the project’s current verified strengths and gaps relative to PharmacoDB 2.0, CellMinerCDB, DrugComb, PharmacoGx, and modern deep-learning model papers. Pharmacoprofiler’s strongest present differentiators are cross-resource harmonization, public inference serving, metadata-rich outputs, and benchmark transparency, while the clearest current gaps remain model-method innovation, uncertainty estimation, and combination-focused analysis.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Introduction or Discussion paragraph positioning PharmacoProfiler against existing tools
- `competitive-positioning.md`
  - `Current positioning claim`
  - `Innovation opportunities`

### Reviewer mapping

- Reviewer 2
  - weak comparative positioning
- Reviewer 3
  - need for clearer articulation of platform contribution and scope

## Figure 8. Uncertainty behavior of the legacy baseline

Files:
- `legacy_benchmark_uncertainty.png`
- `legacy_benchmark_uncertainty.svg`

### Legend

**Figure 8. First-pass uncertainty behavior of the verified legacy Random Forest baseline.**  
Panel A shows the relationship between per-sample tree prediction standard deviation and absolute benchmark error, demonstrating that higher ensemble spread is associated with larger error. Panel B summarizes benchmark performance across uncertainty quintiles and overlays empirical coverage of the nominal tree-based 90% interval. Together, the panels show that the preserved model exposes a useful internal uncertainty signal, but that the raw tree interval under-covers the benchmark set and should therefore be treated as an uncalibrated heuristic rather than as a final predictive interval.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Discussion paragraph on future uncertainty-aware serving
  - Results follow-up sentence if uncertainty is introduced as a supplementary analysis
- `uncertainty-applicability-analysis.md`
  - `Current findings`
  - `Manuscript-safe wording`

### Reviewer mapping

- Reviewer 1
  - need for stronger rigor around predictive reliability
- Reviewer 2
  - need for more informative interpretation beyond point estimates

## Figure 9. Applicability proxy from cell-line similarity

Files:
- `legacy_benchmark_applicability.png`
- `legacy_benchmark_applicability.svg`

### Legend

**Figure 9. First-pass applicability analysis using CCLE-to-GDSC cell-line similarity.**  
Panel A relates each CCLE cell line’s mean absolute benchmark error to its nearest GDSC training-cell cosine similarity in the preserved omics feature space. Panel B summarizes benchmark error and mean prediction spread across applicability quintiles. This figure supports the interpretation that cell lines farther from the GDSC training manifold tend to show modestly worse performance, while also showing that the current similarity-based applicability proxy is weaker than the uncertainty signal and should be treated as an initial domain-shift analysis rather than a final applicability-domain method.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Discussion paragraph on domain shift and next-step methodology
- `uncertainty-applicability-analysis.md`
  - `Applicability proxy`
  - `Next recommended uncertainty work`

### Reviewer mapping

- Reviewer 1
  - need for stronger generalization framing
- Reviewer 2
  - need for biologically contextualized explanation of where the model is less reliable

## Figure 10. Mechanism-aware benchmark annotation

Files:
- `legacy_benchmark_mechanism_overview.png`
- `legacy_benchmark_mechanism_overview.svg`

### Legend

**Figure 10. Mechanism-aware annotation of the preserved benchmark-overlap drugs.**  
Panel A shows drug-level benchmark MAE colored by broad compound class from the verified merged compound-target table. Panel B relates annotated target breadth to benchmark MAE, providing polypharmacology context without asserting causality. Panel C summarizes mean MAE across the mapped mechanism classes. Together, these panels show that the current benchmark spans multiple mechanism classes and both narrow- and broad-target compounds, while also indicating that class-level performance differences should be interpreted descriptively because the overlap set is small.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Discussion paragraph on mechanism-aware interpretation and future biological validation
- `mechanism-aware-analysis.md`
  - `Current findings`
  - `Manuscript-safe wording`

### Reviewer mapping

- Reviewer 2
  - need for stronger biological interpretation and contextualization
- Reviewer 3
  - need for clearer articulation of what the platform adds beyond raw prediction scores

## Figure 11. Leakage-safe regime comparison

Files:
- `legacy_benchmark_leakage_safe_regimes.png`
- `legacy_benchmark_leakage_safe_regimes.svg`

### Legend

**Figure 11. Leakage-sensitive performance differences across the staged ridge benchmark regimes.**  
Panel A compares MAE and RMSE across the four saved GDSC split regimes. Panel B compares Pearson correlation and `R²` across the same regimes. The row-random comparator remains strong, cell-line holdout remains materially better than drug holdout, and the strictest double-cold-start regime is the weakest overall. This figure supports the manuscript-safe claim that the current baseline is far more robust to unseen cell lines than to unseen compounds and that row-random performance should not be interpreted as strong unseen-drug generalization.

### Manuscript mapping

- `canonical-manuscript-draft.md`
  - Section `4.2 Claims that still require rerun evidence`
  - leakage-safe benchmark paragraph introducing the staged ridge comparison
- `leakage-safe-benchmark-results.md`
  - `Summary of the completed ridge sweep`
  - `Manuscript-safe interpretation`

### Reviewer mapping

- Reviewer 1
  - need for explicit split-policy rigor
  - need to distinguish permissive from leakage-sensitive performance
- Reviewer 2
  - need for stronger comparative interpretation of what the model actually generalizes across

## Recommended manuscript insertion order

For the current revision cycle, the most effective primary figure order is:

1. Figure 1: benchmark overview
2. Figure 5: calibration detail
3. Figure 6: subgroup variability
4. Figure 11: leakage-safe regime comparison
5. Figure 7: competitive positioning comparison

Recommended supplemental figure order:

1. Figure 3: confidence intervals
2. Figure 2: drug-level variability
3. Figure 4: top-error examples
4. Figure 8: uncertainty behavior
5. Figure 9: applicability proxy
6. Figure 10: mechanism-aware benchmark annotation
