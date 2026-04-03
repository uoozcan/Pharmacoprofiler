from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr

try:
    import joblib
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    joblib = None

try:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    mean_absolute_error = None
    mean_squared_error = None
    r2_score = None

try:
    from ._common import (
        DEFAULT_CONFIG_PATH,
        REPO_ROOT,
        BenchmarkPaths,
        fingerprint_map_from_gdsc,
        load_json,
        require_existing,
        resolve_benchmark_paths,
        resolve_manifest_artifacts,
    )
except ImportError:
    from _common import (
        DEFAULT_CONFIG_PATH,
        REPO_ROOT,
        BenchmarkPaths,
        fingerprint_map_from_gdsc,
        load_json,
        require_existing,
        resolve_benchmark_paths,
        resolve_manifest_artifacts,
    )


def require_runtime_dependencies() -> None:
    missing: list[str] = []
    if joblib is None:
        missing.append("joblib")
    if mean_absolute_error is None or mean_squared_error is None or r2_score is None:
        missing.append("scikit-learn")
    if missing:
        raise SystemExit(
            "Missing runtime dependencies for benchmark execution: "
            + ", ".join(missing)
            + ". Install the service/benchmark Python dependencies and rerun."
        )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the canonical legacy pIC50 baseline benchmark.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Benchmark config JSON describing legacy inputs and output locations.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory override.",
    )
    return parser.parse_args()


def load_or_reconstruct_ccle_response(
    paths: BenchmarkPaths,
    gdsc_df: pd.DataFrame,
    ccle_vector_df: pd.DataFrame,
    target_column: str,
    raw_target_column: str,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    if paths.prepared_ccle_response_path.exists():
        prepared_df = pd.read_csv(paths.prepared_ccle_response_path, sep="\t")
        return prepared_df, {
            "source_mode": "prepared_file",
            "source_path": str(paths.prepared_ccle_response_path),
            "reconstructed": False,
        }

    require_existing(paths.raw_ccle_response_path, "raw CCLE response file")
    raw_df = pd.read_csv(paths.raw_ccle_response_path, sep="\t")
    drug_to_fp = fingerprint_map_from_gdsc(gdsc_df)
    valid_cell_lines = set(ccle_vector_df["CELL_LINE_NAME"].astype(str).str.lower().tolist())

    reconstructed = raw_df.copy()
    reconstructed["CELL_LINE_NAME_edited"] = reconstructed["CELL_LINE_NAME_edited"].astype(str).str.lower()
    reconstructed["DRUG_NAME_edited"] = reconstructed["DRUG_NAME"].map(normalize_token)
    reconstructed["FINGERPRINT"] = reconstructed["DRUG_NAME_edited"].map(drug_to_fp)
    reconstructed[target_column] = reconstructed[raw_target_column]
    reconstructed = reconstructed[
        reconstructed["CELL_LINE_NAME_edited"].isin(valid_cell_lines) & reconstructed["FINGERPRINT"].notna()
    ].copy()
    reconstructed.sort_values(by=["CELL_LINE_NAME_edited", "DRUG_NAME_edited"], inplace=True)

    metadata = {
        "source_mode": "reconstructed_from_raw",
        "source_path": str(paths.raw_ccle_response_path),
        "reconstructed": True,
        "raw_rows": int(len(raw_df)),
        "reconstructed_rows": int(len(reconstructed)),
        "unique_drugs_after_mapping": int(reconstructed["DRUG_NAME_edited"].nunique()),
        "unique_cell_lines_after_mapping": int(reconstructed["CELL_LINE_NAME_edited"].nunique()),
    }
    return reconstructed, metadata


def split_fingerprints(response_df: pd.DataFrame, vector_df: pd.DataFrame, target_column: str) -> pd.DataFrame:
    fingerprint_rows = [list(str(bits)) for bits in response_df["FINGERPRINT"].tolist()]
    split_df = pd.DataFrame(fingerprint_rows)
    split_df.insert(0, "CELL_LINE_NAME", response_df["CELL_LINE_NAME_edited"].tolist())
    split_df["DRUG_NAME"] = response_df["DRUG_NAME_edited"].tolist()
    split_df[target_column] = response_df[target_column].tolist()

    renamed = {index: index + len(vector_df.columns.values) for index in range(1024)}
    split_df.rename(columns=renamed, inplace=True)
    return split_df


def build_test_matrix(
    ccle_vector_df: pd.DataFrame,
    ccle_response_df: pd.DataFrame,
    target_column: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    split_df = split_fingerprints(ccle_response_df, ccle_vector_df, target_column)
    merged = pd.merge(ccle_vector_df, split_df, on="CELL_LINE_NAME", how="inner")
    merged = merged.dropna(subset=["DRUG_NAME", target_column]).copy()
    features = merged.drop(["DRUG_NAME", "CELL_LINE_NAME", target_column], axis=1).astype(np.float32)
    labels = merged[[target_column]].astype(np.float32)
    return merged, pd.concat([features, labels], axis=1)


def compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": float(mean_squared_error(y_true, y_pred)),
        "rmse": float(mean_squared_error(y_true, y_pred, squared=False)),
        "spearman_r": float(spearmanr(y_true, y_pred)[0]),
        "pearson_r": float(pearsonr(y_true, y_pred)[0]),
        "r_squared": float(r2_score(y_true, y_pred)),
    }


def write_outputs(
    output_dir: Path,
    summary: dict[str, Any],
    metrics: dict[str, float],
    predictions_df: pd.DataFrame,
    reconstructed_ccle_df: pd.DataFrame | None,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "benchmark_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.DataFrame([metrics]).to_csv(output_dir / "metrics.tsv", sep="\t", index=False)
    predictions_df.to_csv(output_dir / "ccle_predictions.tsv", sep="\t", index=False)
    if reconstructed_ccle_df is not None:
        reconstructed_ccle_df.to_csv(output_dir / "ccle_response_reconstructed.tsv", sep="\t", index=False)


def main() -> None:
    args = parse_args()
    require_runtime_dependencies()
    config_path = args.config.resolve()
    config = load_json(config_path)
    output_override = str(args.output_dir.resolve()) if args.output_dir else os.environ.get(
        "PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR"
    )
    paths = resolve_benchmark_paths(config, output_dir_override=output_override)
    require_existing(paths.gdsc_response_path, "GDSC response file")
    require_existing(paths.ccle_vector_path, "CCLE omics matrix")
    require_existing(paths.artifact_manifest_path, "artifact manifest")

    artifact_paths = resolve_manifest_artifacts(paths.artifact_manifest_path)
    for label, path in artifact_paths.items():
        require_existing(path, f"artifact {label}")

    gdsc_df = pd.read_csv(paths.gdsc_response_path, sep="\t")
    ccle_vector_df = pd.read_csv(paths.ccle_vector_path, sep="\t")
    ccle_response_df, response_metadata = load_or_reconstruct_ccle_response(
        paths,
        gdsc_df,
        ccle_vector_df,
        target_column=config["target_column"],
        raw_target_column=config["raw_target_column"],
    )

    merged_ccle_df, benchmark_df = build_test_matrix(
        ccle_vector_df,
        ccle_response_df,
        target_column=config["target_column"],
    )

    feature_matrix = benchmark_df.drop([config["target_column"]], axis=1).to_numpy(dtype=np.float32)
    labels = benchmark_df[config["target_column"]].to_numpy(dtype=np.float32)
    model = joblib.load(artifact_paths["trained_model"])
    predictions = model.predict(feature_matrix)
    metrics = compute_metrics(labels, predictions)

    predictions_df = merged_ccle_df[["CELL_LINE_NAME", "DRUG_NAME"]].copy()
    predictions_df["pIC50_True"] = labels
    predictions_df["pIC50_Pred"] = predictions

    summary = {
        "benchmark_name": config["benchmark_name"],
        "description": config["description"],
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "lineage_note": config["lineage_note"],
        "artifacts": {key: str(value) for key, value in artifact_paths.items()},
        "inputs": {
            "gdsc_response_path": str(paths.gdsc_response_path),
            "ccle_vector_path": str(paths.ccle_vector_path),
            "ccle_response_source": response_metadata,
        },
        "split_policy": {
            "train_domain": "GDSC",
            "test_domain": "CCLE",
            "model_family": config["model_family"],
            "feature_schema_version": config["feature_schema_version"],
        },
        "dataset_summary": {
            "gdsc_rows": int(len(gdsc_df)),
            "ccle_vector_cell_lines": int(ccle_vector_df["CELL_LINE_NAME"].nunique()),
            "evaluated_ccle_rows": int(len(predictions_df)),
            "evaluated_ccle_drugs": int(predictions_df["DRUG_NAME"].nunique()),
            "evaluated_ccle_cell_lines": int(predictions_df["CELL_LINE_NAME"].nunique()),
        },
        "metrics": metrics,
    }

    reconstructed_df = ccle_response_df if response_metadata["reconstructed"] else None
    write_outputs(paths.output_dir, summary, metrics, predictions_df, reconstructed_df)

    print("summary:")
    print(f"config_path: {config_path}")
    print(f"preferred_output_dir: {(REPO_ROOT / config['output_dir']).resolve()}")
    print(f"output_dir: {paths.output_dir}")
    print(f"Wrote benchmark outputs to: {paths.output_dir}")
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
