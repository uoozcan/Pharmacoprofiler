# Methods Rewrite Specification

The Methods section must be rewritten from verified implementation details only.

## Required Sections

### Data sources and versions
- exact source release names
- retrieval date
- assay and endpoint notes

### Cell line harmonization
- exact matching
- fuzzy matching
- Cellosaurus lookup
- manual resolution and audit outputs

### Compound, target, and indication integration
- identifier precedence
- registry usage
- conflict resolution rules

### Data preprocessing and QC
- unit conversions to pIC50 or equivalent
- exclusion criteria
- missing-data handling
- source-specific caveats

### Model training and evaluation
- feature inputs actually used
- train/validation/test split policy
- hyperparameter search strategy
- baseline models
- performance metrics and confidence intervals
- exact script or package entrypoint used to generate reported metrics
- artifact checksum or version references for the runtime asset set

### Web and service implementation
- actual frontend framework
- actual backend framework
- visualization library
- service boundaries
- prediction API contract

## Explicitly Prohibited

- placeholder framework names
- generic textbook paragraphs that are not tied to implementation
- claims of clinical translation beyond available evidence
- invented preprocessing details that are not yet verified from code
- placeholder benchmark values in manuscript-ready sections
