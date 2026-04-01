# Reviewer Response Matrix

## Consolidated High-Priority Actions

| Area | Problem | Evidence | Planned repository artifact |
| --- | --- | --- | --- |
| Repository foundation | No software repository structure | Legacy root contained manuscript assets only | Root scaffold, governance files, CI placeholders |
| Methods rigor | Technical details insufficient for reproducibility | `issues_v1.docx`, reviewer comments | `docs/research/manuscript/methods-rewrite-spec.md` |
| Benchmarking | Claims lack context and metrics | Reviewer 1, issue log | `models/evaluation/legacy_pic50_baseline/metrics.tsv`, `models/evaluation/legacy_pic50_baseline/benchmark_summary.json`, `docs/research/supplementary/benchmark-baseline-interpretation.md` |
| Data harmonization | Mapping strategy poorly documented | `issues_v1.docx`, Reviewer 1 and 2 | `docs/datasets/harmonization.md` |
| Comparative positioning | Weak distinction from existing tools | Issue log, Reviewer 2 | `docs/research/supplementary/platform-comparison-plan.md` |
| Platform documentation | Architecture and workflows undocumented | Reviewer 3 | `docs/architecture/overview.md`, `docs/user-guide/` |
| Sustainability | No release or maintenance process | Reviewer 3 | `docs/operations/release-and-sustainability.md` |

## Issue Log Mapping

### Critical manuscript issues from `issues_v1.docx`

1. Clarify GDSC1 and GDSC2 separately and position them properly in the introduction.
2. Correct NCI-60 wording to distinguish total compounds from quality-controlled subset.
3. Replace weak comparative discussion with a structured review of existing tools and then introduce PharmacoProfiler novelty.
4. Rewrite cell line harmonization and drug information sections using actual methodology rather than generic prose.
5. Remove duplicated and awkward text around web application and prediction service implementation.
6. Reframe results around implemented use cases, including the website prediction flow and top-10 reporting instead of top-20.

### Reviewer themes

- Reviewer 1: technical rigor, reproducibility, benchmarking
- Reviewer 2: biological validation, translational framing, comparative analysis
- Reviewer 3: architecture clarity, usability evidence, sustainability, presentation quality
