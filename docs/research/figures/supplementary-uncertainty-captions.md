# Supplementary Uncertainty Figure Captions

## Purpose

This file provides compact supplementary-caption text for the uncertainty-focused figure set. It is intended for manuscript assembly when the shorter caption form is more useful than the full legend-and-mapping document.

## Figure 8

**Figure 8. First-pass uncertainty behavior of the verified legacy Random Forest baseline.** Per-sample tree prediction standard deviation is related to absolute benchmark error, and uncertainty quintiles are summarized together with empirical coverage of the nominal tree-based 90% interval. The preserved model exposes a real internal uncertainty signal, but the raw tree interval under-covers the benchmark set and should therefore be treated as an uncalibrated heuristic rather than as a finalized predictive interval.

## Figure 9

**Figure 9. First-pass applicability analysis using CCLE-to-GDSC cell-line similarity.** Cell-line-level benchmark error is compared with nearest GDSC training-cell cosine similarity in the preserved shared omics space, and applicability quintiles are summarized together with mean prediction spread. The resulting pattern suggests that CCLE cell lines farther from the GDSC training manifold tend to have modestly worse performance, but the current similarity-based applicability proxy remains weaker than the uncertainty signal and should be interpreted as an initial domain-shift analysis rather than as a final applicability-domain method.

## Supplementary Figure S1

**Supplementary Figure S1. Interval calibration behavior of the verified legacy Random Forest baseline.** Nominal central tree-quantile coverage is compared with empirical benchmark coverage across interval levels from 50% to 95%, and coverage gaps are summarized together with the descriptive post hoc width-inflation factor needed to recover nominal 90% coverage on the same benchmark set. These panels show that interval under-coverage is systematic rather than confined to one nominal level, reinforcing the manuscript-safe conclusion that the current uncertainty layer is informative but not yet calibrated for deployment-facing predictive-interval claims.
