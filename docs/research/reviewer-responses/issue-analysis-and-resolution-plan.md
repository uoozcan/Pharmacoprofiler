# Issue Analysis and Resolution Plan

## Critical

### Repository structure absent
- problem: no application repository existed, only a manuscript workspace
- implemented in this restructure:
  - monorepo-ready root layout
  - governance files
  - CI placeholders
  - canonical docs and archive separation

### Manuscript contains generic and duplicated text
- problem: placeholder frameworks, duplicate web-tool description, non-implementation-grounded prose
- implemented in this restructure:
  - manuscript status doc
  - methods rewrite spec
  - reviewer response matrix
- remaining work:
  - replace draft text after code import and evidence verification

### Reproducibility incomplete
- problem: missing technical specification for ingestion, harmonization, model training, and serving
- implemented in this restructure:
  - architecture docs
  - API docs
  - dataset docs
  - technical specification placeholder

### Performance claims under-supported
- problem: reported correlations lacked metric context, baselines, and confidence intervals
- implemented in this restructure:
  - benchmarking plan
  - supplementary comparison plan
- remaining work:
  - produce actual benchmark outputs from code and data

## High

### Harmonization writeup weak
- implemented:
  - harmonization documentation framework
- remaining:
  - fill with exact mapping logic and audit statistics

### Comparative positioning weak
- implemented:
  - platform comparison plan
- remaining:
  - create manuscript-ready comparison table

### Platform documentation weak
- implemented:
  - user-guide, architecture, API, and operations docs skeleton
- remaining:
  - replace placeholders with screenshots and real workflows

## Medium

### Sustainability and release process missing
- implemented:
  - operations and release doc

### Testing strategy missing
- implemented:
  - tests tree and CI placeholders

### Asset sprawl
- implemented:
  - legacy workspace moved under `archive/legacy-manuscript-materials/`
  - curated research set promoted under `docs/research/`
