# Verified Legacy Service Import Target

This directory records the verified legacy pIC50 prediction service as a future import target for refactoring.

## Source of truth

Verified sources:
- local legacy workspace under `/home/umut/projects/pharmacoprofiler_legacy/CLRB_MODELLING/pharmacoprofiler_docker/pharmacoprofiler/huggingface_profile`
- public Hugging Face Space `ozcanumut/pic50-prediction-server`

This directory is a preserved legacy snapshot, not the current deployment source of truth. The maintained baseline now lives in `services/prediction-api/`, and the repo-side Hugging Face sync templates live alongside it.

## Included here

- service entrypoint copied from the verified legacy Hugging Face profile
- deployment-oriented `requirements.txt`
- a legacy Dockerfile variant from the archived local workspace

## Not included here

The large model artifacts are intentionally not copied into the repository root service directory yet:
- `GDSC_extracted_988_cell_lines_L1000_common_genes_3747_feature_vector_v1_selected_common_3_platform_v2.txt`
- `GDSC_988_cell_line_name_main_fix_RRID_v1.txt`
- `GDSC_CCLE_cross_domain_mode_7_v4.joblib`

Those should be managed as versioned runtime assets or external storage objects rather than committed blindly.

## Import policy

Treat this directory as a preservation layer. Refactor into the main `services/prediction-api/` package only after:
- interface compatibility is documented
- asset loading is made explicit
- tests are added

## Deployment note

Do not assume all deployment files in legacy sources are identical.

The public Hugging Face Space and the archived local Docker setup are functionally related but show some runtime-packing differences. Use the public service contract as the compatibility baseline and treat Docker/runtime specifics as legacy variants until reconciled.
