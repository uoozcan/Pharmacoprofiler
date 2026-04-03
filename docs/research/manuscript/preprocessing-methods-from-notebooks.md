# Preprocessing Methods From Verified Notebooks

## Status

This note provides manuscript-ready preprocessing language grounded in sampled legacy notebooks and the verified cross-domain training script. It is limited to steps directly supported by notebook or script evidence.

For notebook provenance, see:

- `docs/research/notebooks/notebook-methods-evidence-matrix.md`
- `docs/research/notebooks/notebook-provenance.md`

## Source datasets and assay endpoints

The legacy notebook layer shows that PharmacoProfiler aggregated drug-response data from multiple public pharmacogenomic resources rather than from a single benchmark dataset. The sampled preprocessing notebooks cover GDSC1, GDSC2, CCLE, FIMM, NCI-60, and NCATS, each with source-specific assay formats and endpoint conventions.

The verified endpoint handling is heterogeneous:

- CCLE notebooks convert micromolar IC50 values to pIC50.
- FIMM notebooks fit dose-response curves to recover IC50 values and then convert them to pIC50.
- NCI-60 notebooks preserve the source endpoint as pGI50 and explicitly note the distinction between total assayed compounds and the subset passing quality control.
- NCATS notebooks reshape a source file named as IC50 activity data, but the notebook internally labels the response column as `pIC50` before setting `METRIC = IC50`; this inconsistency must be reported as a notebook-level caveat rather than silently harmonized.

## Response-value standardization

The verified response standardization steps are dataset-specific rather than globally scripted in a single pipeline.

For CCLE NP24, the notebook selects the source columns `Compound`, `Primary Cell Line Name`, and `IC50 (uM)`, renames them to canonical fields, and computes pIC50 as `-(log10(IC50 / 1000000))`. The same notebook also contains a GNF/NP26 reshaping path in which wide-format response values are converted to long format and transformed to pIC50 using the same micromolar-to-molar conversion logic.

For FIMM, the notebook fits a four-parameter dose-response curve using `scipy.optimize.curve_fit`, extracts IC50 from the fitted parameters, converts those values to pIC50, and then emits a standardized response table with canonical column names.

For NCI-60, the notebook does not convert to pIC50. Instead, it retains the source response framing as negative log10 GI50 and labels the final metric as `pGI50`.

## Dataset-specific reshaping and filtering

The sampled notebooks show that reshaping and filtering were handled per source dataset.

The CCLE and NCATS notebooks explicitly reshape source tables into long drug-cell-line form. In NCATS, this is implemented by concatenating repeated drug metadata, repeated cell-line names, and per-cell-line response columns into one long response table. In NCI-60, a wide table with colon-delimited column names is split so that cell-line names and tissue descriptors can be recovered from the source headers before long-format export.

For GDSC1 and GDSC2, the preprocessing emphasis in the sampled notebook cells is on drug metadata cleanup and response-table curation. Header names with leading spaces are normalized, drug metadata are filtered to the relevant dataset, duplicate compound names or synonyms are collapsed, and only drugs matched to curated response identifiers are retained in later output tables.

## Cell-line harmonization and Cellosaurus enrichment

The notebook evidence shows that cell-line harmonization relied heavily on dictionary-based enrichment from Cellosaurus-derived exports rather than on a single packaged mapping module. The sampled Cellosaurus notebook builds mappings from identifiers and synonyms to accession numbers, disease annotations, references, comments, and cross-references. Those dictionaries are then applied to dataset-specific cell-line tables.

The same notebook extracts tissue-like annotations from Cellosaurus comments by parsing `Derived from site ... UBERON` strings with regular expressions. This supports a methods statement that tissue labels were at least partly derived from Cellosaurus annotations or source metadata, depending on the workflow.

The notebook evidence also shows explicit manual alias correction. For example, the FIMM preprocessing notebook remaps `RPMI` to `RPMI-8226` and `RMG1` to `RMG-I` before downstream response processing. These corrections should be described as curated notebook-driven adjustments rather than as a fully formalized ontology pipeline.

## Compound normalization, SMILES, and fingerprints

The chemical preprocessing layer is distributed across SMILES/InChI mapping notebooks and fingerprint-generation notebooks. The verified fingerprint notebook loads a prepared compound-to-SMILES table, then computes Morgan/ECFP4 fingerprints with radius 2 and 1024 bits using RDKit. The resulting bit strings are written to a file for downstream prediction use.

This supports the manuscript claim that the predictor consumes 1024-bit Morgan/ECFP4 fingerprints derived from curated SMILES representations. It does not yet support a stronger claim that the entire compound-normalization workflow has been fully reconstructed into a single scripted pipeline in the current repository.

## Predictor input assembly

The predictor input assembly is supported jointly by notebook and script evidence. The prediction-pair preparation notebook loads preserved GDSC, CCLE, and NCI-60 cell-line matrices in a shared 3747-feature space, maps cell-line identifiers to canonical names, and attaches RRID metadata from Cellosaurus-derived lookups. It also loads curated compound lists and cross-platform drug-response tables to construct prediction-ready pairings.

The verified cross-domain training script then consumes prepared GDSC and CCLE response tables together with those 3747-feature omics matrices. It splits 1024-bit fingerprint strings into explicit columns, merges fingerprint columns with cell-line omics vectors, casts the resulting matrices to `float32`, and trains a `RandomForestRegressor` on GDSC before external testing on CCLE.

## Omics preprocessing boundary

The current evidence is sufficient to state that the predictor consumes preserved 3747-feature L1000-based matrices that were already aligned across platforms in a shared feature space. It is not yet sufficient to describe the full upstream omics normalization, feature selection, or imputation workflow in detail.

The correct methods framing is therefore:

- the 3747-feature matrices are verified predictor inputs
- cross-platform shared-feature use is verified
- upstream normalization and feature-selection logic remain only partially reconstructed from available notebook evidence

## Dataset-specific caveats

- NCATS notebook labeling is internally inconsistent because it uses a `pIC50` response column name but later writes `METRIC = IC50`.
- NCI-60 preprocessing uses a sentinel replacement (`na` -> `9999`) before splitting actual and missing response tables; this should be described as notebook-specific handling, not as a recommended final missing-data standard.
- Several harmonization steps rely on explicit dictionary mappings and manual alias fixes rather than on a fully scripted ontology resolution pipeline.
- The sampled notebooks support the use of preserved prepared omics matrices, but not a complete reconstruction of their upstream generation.

## Manuscript-safe summary

The notebook evidence supports a methods section in which response preprocessing is described as source-specific, harmonization is described as Cellosaurus-assisted and partially manual, chemical features are described as RDKit-generated 1024-bit ECFP4 fingerprints, and model inputs are described as concatenated omics-plus-fingerprint vectors. The same evidence also requires explicit caveats around NCATS metric labeling, NCI-60 endpoint differences, and the incomplete reconstruction of upstream omics preprocessing.
