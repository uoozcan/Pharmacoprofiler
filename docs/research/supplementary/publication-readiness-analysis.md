# Publication Readiness Analysis

## Purpose

This note translates the current benchmark and service evidence into manuscript-safe claims, known publication risks, and concrete next analyses needed for a stronger paper.

## What is publishable now

The current repository can support these claims without overreach:

- PharmacoProfiler implements a verified SMILES-to-cell-line pIC50 prediction service backed by a preserved deployed model artifact.
- The current predictor uses a Random Forest trained on GDSC-style examples with a cross-domain CCLE evaluation baseline.
- The repository now contains reproducible benchmark outputs, artifact verification, subgroup analyses, and service-validation notes.
- Prediction outputs are enriched with canonical cell line names, RRIDs, and tissue labels.

This positions the project as a harmonization-plus-serving platform with a reproducible predictive baseline, not yet as a methodologically novel modeling paper.

## What the current evidence does not support

The following should remain explicitly out of scope for final claims:

- state-of-the-art predictive performance claims
- confidence in individual predictions without uncertainty estimation
- leakage-safe generalization claims across compounds, cell lines, and datasets
- strong biological-mechanistic interpretation from the current model alone
- verified implementation claims about the live `pharmacoprofiler.com` stack

## Benchmark interpretation for manuscript wording

The current baseline is scientifically useful but needs careful framing:

- overall transfer correlation is strong enough to justify continued development
- explanatory power remains modest (`R² = 0.2633`)
- error is directionally biased toward underprediction (`85.0%` of rows)
- output variance is compressed relative to observed response values
- high-sensitivity cases are the weakest region of the current model

Recommended wording:

`The current repository baseline demonstrates reproducible cross-domain ranking signal on a reconstructed CCLE evaluation set, while also revealing systematic underprediction and reduced dynamic range in higher-pIC50 regions.`

## Reviewer-relevant risk points

### 1. High-sensitivity undercalling

The fixed-bin potency analysis shows the largest error in the `>7.5` pIC50 group:

- count: `524`
- MAE: `1.1134`
- mean signed error: `-1.1131`

This means the model most strongly underestimates the strongest responses, which is a direct manuscript limitation and a practical ranking risk.

### 2. Drug-specific instability

Several drugs show weak transfer behavior or large systematic offsets:

- `irinotecan`: MAE `1.6631`, mean signed error `-1.6631`
- `plx4720`: MAE `1.1725`, mean signed error `-1.1725`
- `paclitaxel`: Pearson `0.1176`, slope near zero in follow-up calibration analysis
- `crizotinib`: Pearson `0.1062`, mean signed error `-0.6240`

This argues against presenting a single undifferentiated “model performs well” claim.

### 3. Residual tissue ontology debt

The current repository now fixes obvious reporting duplication through a canonical tissue-normalization layer:

- `soft_tissue` and `Soft Tissue` are merged for benchmark reporting
- `large_intestine` and `Colon` are merged for benchmark reporting

The remaining issue is broader ontology design, not simple label hygiene. In particular, labels such as `pleura`, `pleural_effusion`, and `pericardial_effusion` should stay distinct until a source-level review justifies collapsing them.

## Most useful next figure/table package

The next manuscript-ready figure set should be built from current repo outputs:

1. Overall predicted-vs-observed scatter with regression line and identity line.
2. Drug-level bar plot of Pearson and MAE from `drug_metrics.tsv`.
3. Tissue-level bar plot of Pearson and MAE from `tissue_metrics.tsv`.
4. Potency-bin error plot from `potency_bin_metrics.tsv`.
5. A compact table of the top 10 worst prediction failures from `top_error_examples.tsv`.

These figures would strengthen the Results and Limitations sections without requiring a new model.

## Best next analyses for publication strength

1. Add uncertainty or applicability-domain scoring to prediction outputs.
2. Add a calibration comparison table before and after post-hoc correction.
3. Add simple baseline comparators such as ridge or elastic net before introducing deep models.
4. Extend the current reporting-layer tissue normalization into a broader cross-resource ontology only after source review.
5. Add leakage-safe split regimes for compound holdout, cell-line holdout, and source-transfer evaluation.

## Bottom line

The project is now publishable as a reproducible platform-and-baseline paper only if the manuscript is explicit about current limitations. For a stronger methods paper, the next threshold is not a more complex model first; it is calibration, uncertainty, cleaner subgroup reporting, and stronger benchmark design.
