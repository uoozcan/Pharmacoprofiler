# Benchmark Input Reconstruction

## Purpose

The original legacy training script expects a prepared file named `CCLE_drug_response_df_for_cross_domain_v3.txt`, but that exact file is not currently present in the preserved legacy workspace. This document defines the current-repo reconstruction path used to recover the missing benchmark input from verified source files.

## Current reconstruction workflow

Use:

```bash
python3 scripts/evaluate/prepare_ccle_cross_domain_response.py
```

This script:
- loads the preserved GDSC response table with 1,024-bit fingerprints
- loads the preserved raw CCLE response table from `Cellminer/CCLE/CCLE_actual_drug_response_v1.txt`
- normalizes drug names conservatively using lowercase alphanumeric matching
- maps overlapping CCLE drugs onto GDSC fingerprint strings
- filters to CCLE cell lines present in the preserved 3,747-feature omics matrix
- writes a reconstructed cross-domain response table into `models/evaluation/legacy_pic50_baseline/`

## Output files

- `models/evaluation/legacy_pic50_baseline/ccle_response_reconstructed.tsv`
- `models/evaluation/legacy_pic50_baseline/ccle_response_reconstruction_summary.json`

In restricted environments where the canonical repo output path is not writable, the scripts fall back to:

- `/tmp/pharmacoprofiler_outputs/legacy_pic50_baseline/`

## Current verified reconstruction summary

Using the preserved files currently available in `/home/umut/projects/pharmacoprofiler_legacy`, the reconstruction step yields:

- 11,273 raw CCLE response rows
- 6,513 reconstructed cross-domain rows after fingerprint and omics overlap filtering
- 24 raw CCLE drugs reduced to 16 overlapping drugs with available GDSC fingerprints
- 492 raw CCLE cell lines reduced to 434 overlapping cell lines present in the preserved CCLE omics matrix

The currently mapped drug set is:

- `crizotinib`
- `erlotinib`
- `irinotecan`
- `lapatinib`
- `nilotinib`
- `paclitaxel`
- `palbociclib`
- `panobinostat`
- `pd0325901`
- `pha665752`
- `plx4720`
- `saracatinib`
- `selumetinib`
- `sorafenib`
- `tanespimycin`
- `topotecan`

## Interpretation

This reconstruction is intended to make the benchmark baseline executable from preserved files. It should be treated as a reproducible current-repo preparation step, not as proof that the exact original prepared legacy file has been recovered byte-for-byte.
