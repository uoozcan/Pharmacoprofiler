# Current Open Issues

## Purpose

This note is the single current tracker for unresolved project issues that still matter scientifically or operationally. It should be used to distinguish:

- issues that are now resolved and only need maintenance
- issues that remain open but are already bounded by manuscript-safe notes
- issues that still require new computation, new code, or external verification

## Resolved enough for current manuscript scope

These areas are no longer open blockers for the current platform-and-baseline manuscript position:

- benchmark reproducibility for the reconstructed CCLE baseline
- service baseline hardening and Hugging Face deployment parity
- notebook-grounded preprocessing documentation
- tissue normalization for benchmark reporting
- figure-linked manuscript drafting
- explicit boundary notes for omics provenance, harmonization scope, and uncertainty/applicability claims

## Still open

### 1. Whether to pursue a third leakage-safe comparator

Current state:

- staged `ridge` leakage-safe sweep is complete and citable
- staged `ols` leakage-safe sweep is complete and citable
- the completed `ridge` and `ols` sweeps are effectively indistinguishable across all four saved regimes
- legacy RF comparator remains unresolved because the attempted `rf_pair_random` run produced no result files

Why it still matters:

- the manuscript can now make a completed two-model leakage-sensitive benchmarking claim from the `ridge` versus `ols` comparison
- the remaining question is whether revisiting the heavier legacy RF comparator would add enough value to justify the extra compute cost

### 2. Calibrated uncertainty and applicability

Current state:

- first-pass uncertainty and applicability outputs exist
- the uncertainty signal is informative
- the current tree-based intervals are under-calibrated
- the similarity-based applicability proxy is modest in effect size

Why it still matters:

- the current layer is useful for manuscript limitation framing
- it is not yet strong enough for public reliability claims or default API outputs

### 3. End-to-end harmonization packaging

Current state:

- notebook-grounded harmonization provenance is strong
- curated cell-line, compound, and metadata integration is clearly evidenced
- the current repository still does not rebuild the full cross-resource harmonization layer from raw inputs as a single scripted pipeline

Why it still matters:

- the project can claim broad harmonization provenance
- it still cannot claim a fully packaged reusable harmonization framework

### 4. Upstream omics preprocessing reconstruction

Current state:

- the cross-platform `3747`-feature matrix lineage is now better bounded
- the exact upstream normalization, feature-selection, and possible imputation steps are still unrecovered

Why it still matters:

- current methods wording is now safe
- a stronger methods paper would still benefit from fuller provenance reconstruction

### 5. External web-stack verification

Current state:

- Hugging Face Space is verified and aligned with the maintained repo
- `pharmacoprofiler.com` remains only partially verifiable from this environment

Why it still matters:

- public product claims should stay tied to the verified Hugging Face service and maintained repo
- the live external frontend stack should still not be overclaimed in manuscript or software descriptions

## Recommended order

1. decide whether calibrated uncertainty is the next scientific work item or whether the completed manuscript package should be pushed first
2. decide whether the legacy RF comparator is worth revisiting beyond the completed `ridge` versus `ols` benchmark
3. treat harmonization repackaging and fuller omics provenance recovery as medium-term follow-up work
