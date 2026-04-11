# Manuscript Status

## Canonical Objective

Convert the manuscript from a draft containing generic and duplicated prose into an implementation-grounded scientific document that is aligned with the actual software and validation evidence.

## Immediate Problems Identified

- duplicated web application description
- placeholder stack names such as `XXXX`
- generic ML textbook-style prose without implementation traceability
- incomplete benchmarking context
- unsupported or underspecified validation claims

## Current Canonical Sources

Use these as source material, not as final publishable text:
- `archive/legacy-manuscript-materials/a_CLRB_RESEARCH_ARTICLE/PharmacoProfile1.docx`
- `archive/legacy-manuscript-materials/a_CLRB_RESEARCH_ARTICLE/issues_v1.docx`
- reviewer markdown files preserved from the legacy workspace
- `canonical-manuscript-draft.md`, the implementation-grounded baseline assembled from verified repository evidence
- `author-working-draft.md`, the evidence-linked author version for revision work
- `submission-manuscript-draft.md`, the cleaner manuscript version for journal-facing editing

## Required Next Step

Continue polishing from the two-draft structure: use `author-working-draft.md` when internal evidence links and figure-placement notes are needed, and use `submission-manuscript-draft.md` for prose-level journal editing. Any new scientific claim should still be added first to the evidence-linked author draft and only then promoted into the submission-facing draft.

## Current Benchmark Boundary

The current manuscript evidence package is complete for the reconstructed CCLE baseline, the uncertainty/applicability and mechanism-aware support analyses, and the staged leakage-safe `ridge` comparison. The next benchmark expansion is a second lightweight comparator under the same saved split registry. That `ols` comparator path is now implemented, but it should not be cited in the manuscript until completed regime outputs have landed. The earlier legacy RF comparator attempt remains non-evidentiary because the attempted `rf_pair_random` run produced no result files.
