# Harmonization Pipeline Boundary

## Purpose

This note defines the current manuscript-safe boundary for PharmacoProfiler's broader pharmacogenomic harmonization work. It separates three things that are easy to blur in prose:

1. harmonization behavior that is directly supported by preserved notebooks and tables
2. manual curation steps that are visible but not fully scripted
3. broader end-to-end pipeline claims that are still not package-backed in the current repository

## Verified harmonization scope

The preserved legacy workspace contains dataset-specific harmonization notebooks and associated tables for:

- GDSC
- CCLE
- FIMM
- NCI-60
- NCATS
- PRISM
- CTRP
- CellMiner-linked mapping workflows

Those notebooks support the verified claim that PharmacoProfiler performed cross-resource harmonization of:

- drug-response tables
- cell-line identifiers
- compound identifiers
- tissue or lineage-like annotations
- compound SMILES and InChI-linked integration layers

## Notebook-grounded harmonization behavior

The currently recovered notebook evidence supports the following methods-safe statements:

- GDSC workflows clean source-specific drug metadata, separate GDSC1 and GDSC2 handling, and connect drug-response rows to curated compound metadata
- CCLE workflows reshape NP24 and GNF response tables into canonical long-format outputs and convert IC50-like inputs to pIC50
- FIMM workflows include explicit cell-line alias correction and IC50 recovery from dose-response fitting before pIC50 conversion
- NCI-60 workflows preserve pGI50 framing and reshape wide response tables into long-form outputs
- NCATS workflows reshape wide cell-line response matrices into long-form tables and attach tissue-like labels
- Cellosaurus-linked notebooks use accessions, synonyms, disease labels, and comment fields to build cell-line mapping dictionaries and RRID-aware metadata joins
- chemical notebooks normalize SMILES and InChI-linked identifiers and generate RDKit Morgan/ECFP4 fingerprints for downstream prediction

## Manual and semi-manual curation boundary

The preserved notebooks also show that part of the harmonization layer is manual or semi-manual rather than fully scripted. The currently visible examples include:

- dictionary-based cell-line alias corrections
- explicit manual remapping of selected cell-line names
- notebook-level synonym cleanup for compounds
- source-specific tissue-label interpretation from Cellosaurus comments or local metadata tables

These actions are part of the historical implementation and should be described as curated harmonization rather than as purely automatic pipeline behavior.

## Current repository boundary

The current repository preserves this harmonization scope through:

- notebook provenance summaries
- notebook-to-methods evidence matrices
- merged metadata tables
- manuscript-support notes

It does **not** yet package the broader harmonization work as one reproducible end-to-end script or library that rebuilds the full cross-resource integrated dataset from raw source files.

That means the current manuscript can safely claim:

- demonstrable multi-dataset harmonization provenance
- curated identifier normalization across public pharmacogenomic resources
- direct linkage from harmonized metadata into the prediction service and benchmark package

It should **not** yet claim:

- a fully rebuilt end-to-end harmonization pipeline from raw inputs
- a completely automated mapping workflow without manual intervention
- exhaustive source-wide audit statistics unless those are regenerated and versioned in the current repository

## Manuscript-safe wording

Recommended wording:

> PharmacoProfiler's broader data layer is supported by notebook-grounded harmonization workflows spanning major public pharmacogenomic resources, including GDSC, CCLE, FIMM, NCI-60, NCATS, PRISM, CTRP, and CellMiner-linked mapping tables. The preserved evidence shows that response tables, cell-line identifiers, compound identifiers, and metadata fields were curated into common analysis-ready representations, with part of this process implemented through explicit dictionary-based and notebook-level manual corrections. The current repository preserves this harmonization provenance and its downstream integration into the predictor and benchmark package, but it does not yet package the full cross-resource harmonization process as a single end-to-end reproducible pipeline.

## Implication for project scope

This boundary keeps the project scientifically honest. PharmacoProfiler can make a stronger claim about historical harmonization depth than a model-only project, but it should still present the current repository as preserving and exposing harmonization provenance rather than as already shipping a complete rebuildable harmonization framework.
