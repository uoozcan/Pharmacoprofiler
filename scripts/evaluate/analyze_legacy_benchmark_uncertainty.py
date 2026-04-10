from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    import joblib
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    joblib = None

try:
    from scipy.stats import pearsonr
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    pearsonr = None

try:
    from ._common import (
        DEFAULT_CONFIG_PATH,
        BenchmarkPaths,
        load_json,
        require_existing,
        resolve_benchmark_paths,
        resolve_manifest_artifacts,
    )
    from .run_legacy_benchmark_baseline import build_test_matrix, load_or_reconstruct_ccle_response
except ImportError:
    from _common import (
        DEFAULT_CONFIG_PATH,
        BenchmarkPaths,
        load_json,
        require_existing,
        resolve_benchmark_paths,
        resolve_manifest_artifacts,
    )
    from run_legacy_benchmark_baseline import build_test_matrix, load_or_reconstruct_ccle_response


def require_runtime_dependencies() -> None:
    missing: list[str] = []
    if joblib is None:
        missing.append("joblib")
    if pearsonr is None:
        missing.append("scipy")
    if missing:
        raise SystemExit(
            "Missing runtime dependencies for uncertainty analysis: "
            + ", ".join(missing)
            + ". Install the benchmark dependencies and rerun."
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze uncertainty and applicability proxies for the canonical legacy pIC50 benchmark."
    )
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


def resolve_output_dir(args: argparse.Namespace, paths: BenchmarkPaths) -> Path:
    override = args.output_dir.resolve() if args.output_dir else None
    env_override = os.environ.get("PHARMACOPROFILER_BENCHMARK_OUTPUT_DIR")
    if override is not None:
        override.mkdir(parents=True, exist_ok=True)
        return override
    if env_override:
        output_dir = Path(env_override).expanduser().resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir
    paths.output_dir.mkdir(parents=True, exist_ok=True)
    return paths.output_dir


def compute_tree_interval_predictions(model: Any, feature_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    estimator_predictions = np.vstack(
        [estimator.predict(feature_matrix).astype(np.float32) for estimator in model.estimators_]
    )
    return (
        estimator_predictions.std(axis=0, ddof=1),
        np.quantile(estimator_predictions, 0.05, axis=0),
        np.quantile(estimator_predictions, 0.95, axis=0),
    )


def nearest_train_cosine_similarity(
    gdsc_omics_df: pd.DataFrame,
    ccle_omics_df: pd.DataFrame,
) -> dict[str, float]:
    gdsc_matrix = gdsc_omics_df.set_index("CELL_LINE_NAME").astype(np.float32)
    ccle_matrix = ccle_omics_df.set_index("CELL_LINE_NAME").astype(np.float32)
    feature_columns = [column for column in gdsc_matrix.columns if column in ccle_matrix.columns]
    gdsc_values = gdsc_matrix[feature_columns].to_numpy(dtype=np.float32)
    ccle_values = ccle_matrix[feature_columns].to_numpy(dtype=np.float32)

    gdsc_norms = np.linalg.norm(gdsc_values, axis=1, keepdims=True)
    ccle_norms = np.linalg.norm(ccle_values, axis=1, keepdims=True)
    gdsc_norms[gdsc_norms == 0] = 1.0
    ccle_norms[ccle_norms == 0] = 1.0

    normalized_gdsc = gdsc_values / gdsc_norms
    normalized_ccle = ccle_values / ccle_norms
    similarity_matrix = normalized_ccle @ normalized_gdsc.T
    nearest_similarity = similarity_matrix.max(axis=1)

    return {
        str(cell_line): float(similarity)
        for cell_line, similarity in zip(ccle_matrix.index.tolist(), nearest_similarity.tolist())
    }


def add_quantile_bins(
    df: pd.DataFrame,
    source_column: str,
    output_column: str,
    labels: list[str],
) -> pd.DataFrame:
    binned = df.copy()
    binned[output_column] = pd.qcut(
        binned[source_column],
        q=len(labels),
        labels=labels,
        duplicates="drop",
    )
    return binned


def summarize_uncertainty_bins(df: pd.DataFrame) -> pd.DataFrame:
    plot_df = add_quantile_bins(
        df,
        source_column="prediction_std",
        output_column="uncertainty_bin",
        labels=["Q1 lowest", "Q2", "Q3", "Q4", "Q5 highest"],
    )
    summary = (
        plot_df.groupby("uncertainty_bin", observed=False)
        .agg(
            n=("CELL_LINE_NAME", "size"),
            mean_prediction_std=("prediction_std", "mean"),
            mae=("absolute_error", "mean"),
            rmse=("squared_error", lambda values: float(np.sqrt(np.mean(values)))),
            interval_coverage_90=("within_tree_interval_90", "mean"),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
    )
    return summary


def summarize_applicability_bins(df: pd.DataFrame) -> pd.DataFrame:
    plot_df = add_quantile_bins(
        df,
        source_column="nearest_train_cosine",
        output_column="applicability_bin",
        labels=["Q1 lowest", "Q2", "Q3", "Q4", "Q5 highest"],
    )
    summary = (
        plot_df.groupby("applicability_bin", observed=False)
        .agg(
            n=("CELL_LINE_NAME", "size"),
            mean_nearest_train_cosine=("nearest_train_cosine", "mean"),
            mae=("absolute_error", "mean"),
            mean_prediction_std=("prediction_std", "mean"),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
    )
    return summary


def summarize_cell_line_applicability(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("CELL_LINE_NAME")
        .agg(
            n=("DRUG_NAME", "size"),
            nearest_train_cosine=("nearest_train_cosine", "first"),
            mae=("absolute_error", "mean"),
            rmse=("squared_error", lambda values: float(np.sqrt(np.mean(values)))),
            mean_prediction_std=("prediction_std", "mean"),
            mean_signed_error=("signed_error", "mean"),
        )
        .reset_index()
        .sort_values(["nearest_train_cosine", "mae"], ascending=[True, False])
    )
    return summary


def correlation_or_none(x_values: pd.Series, y_values: pd.Series) -> float | None:
    if pearsonr is None:
        return None
    if x_values.nunique() <= 1 or y_values.nunique() <= 1:
        return None
    return float(pearsonr(x_values, y_values)[0])


def build_summary(
    uncertainty_df: pd.DataFrame,
    uncertainty_bins: pd.DataFrame,
    applicability_bins: pd.DataFrame,
    cell_line_summary: pd.DataFrame,
    response_metadata: dict[str, Any],
    artifact_paths: dict[str, Path],
) -> dict[str, Any]:
    return {
        "analysis_name": "legacy_pic50_uncertainty_and_applicability",
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "ccle_response_source": response_metadata,
        "artifacts": {key: str(path) for key, path in artifact_paths.items()},
        "global": {
            "rows": int(len(uncertainty_df)),
            "cell_lines": int(uncertainty_df["CELL_LINE_NAME"].nunique()),
            "drugs": int(uncertainty_df["DRUG_NAME"].nunique()),
            "mean_prediction_std": float(uncertainty_df["prediction_std"].mean()),
            "median_prediction_std": float(uncertainty_df["prediction_std"].median()),
            "tree_interval_90_coverage": float(uncertainty_df["within_tree_interval_90"].mean()),
            "uncertainty_vs_absolute_error_pearson": correlation_or_none(
                uncertainty_df["prediction_std"], uncertainty_df["absolute_error"]
            ),
            "cell_line_similarity_vs_mae_pearson": correlation_or_none(
                cell_line_summary["nearest_train_cosine"], cell_line_summary["mae"]
            ),
        },
        "highest_uncertainty_bin": uncertainty_bins.sort_values("mean_prediction_std", ascending=False)
        .head(1)
        .to_dict(orient="records")[0],
        "lowest_applicability_bin": applicability_bins.sort_values("mean_nearest_train_cosine", ascending=True)
        .head(1)
        .to_dict(orient="records")[0],
    }


def write_outputs(
    output_dir: Path,
    uncertainty_df: pd.DataFrame,
    uncertainty_bins: pd.DataFrame,
    applicability_bins: pd.DataFrame,
    cell_line_summary: pd.DataFrame,
    summary: dict[str, Any],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    uncertainty_df.to_csv(output_dir / "ccle_predictions_with_uncertainty.tsv", sep="\t", index=False)
    uncertainty_bins.to_csv(output_dir / "uncertainty_bin_metrics.tsv", sep="\t", index=False)
    applicability_bins.to_csv(output_dir / "applicability_bin_metrics.tsv", sep="\t", index=False)
    cell_line_summary.to_csv(output_dir / "cell_line_applicability_metrics.tsv", sep="\t", index=False)
    (output_dir / "uncertainty_applicability_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    require_runtime_dependencies()
    config = load_json(args.config.resolve())
    paths = resolve_benchmark_paths(config)
    output_dir = resolve_output_dir(args, paths)

    require_existing(paths.gdsc_response_path, "GDSC response file")
    require_existing(paths.ccle_vector_path, "CCLE omics matrix")
    require_existing(paths.artifact_manifest_path, "artifact manifest")

    artifact_paths = resolve_manifest_artifacts(paths.artifact_manifest_path)
    for label, path in artifact_paths.items():
        require_existing(path, f"artifact {label}")

    gdsc_response_df = pd.read_csv(paths.gdsc_response_path, sep="\t")
    ccle_vector_df = pd.read_csv(paths.ccle_vector_path, sep="\t")
    gdsc_omics_df = pd.read_csv(artifact_paths["omics_matrix"], sep="\t")
    ccle_response_df, response_metadata = load_or_reconstruct_ccle_response(
        paths,
        gdsc_response_df,
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
    prediction_std, lower_90, upper_90 = compute_tree_interval_predictions(model, feature_matrix)

    nearest_similarity = nearest_train_cosine_similarity(gdsc_omics_df, ccle_vector_df)
    uncertainty_df = merged_ccle_df[["CELL_LINE_NAME", "DRUG_NAME"]].copy()
    uncertainty_df["pIC50_True"] = labels
    uncertainty_df["pIC50_Pred"] = predictions
    uncertainty_df["prediction_std"] = prediction_std
    uncertainty_df["prediction_interval_low_90"] = lower_90
    uncertainty_df["prediction_interval_high_90"] = upper_90
    uncertainty_df["signed_error"] = uncertainty_df["pIC50_Pred"] - uncertainty_df["pIC50_True"]
    uncertainty_df["absolute_error"] = uncertainty_df["signed_error"].abs()
    uncertainty_df["squared_error"] = uncertainty_df["signed_error"] ** 2
    uncertainty_df["within_tree_interval_90"] = (
        (uncertainty_df["pIC50_True"] >= uncertainty_df["prediction_interval_low_90"])
        & (uncertainty_df["pIC50_True"] <= uncertainty_df["prediction_interval_high_90"])
    ).astype(float)
    uncertainty_df["nearest_train_cosine"] = uncertainty_df["CELL_LINE_NAME"].map(nearest_similarity)

    uncertainty_bins = summarize_uncertainty_bins(uncertainty_df)
    applicability_bins = summarize_applicability_bins(uncertainty_df)
    cell_line_summary = summarize_cell_line_applicability(uncertainty_df)
    summary = build_summary(
        uncertainty_df,
        uncertainty_bins,
        applicability_bins,
        cell_line_summary,
        response_metadata,
        artifact_paths,
    )
    write_outputs(output_dir, uncertainty_df, uncertainty_bins, applicability_bins, cell_line_summary, summary)

    print("summary:")
    print(f"output_dir: {output_dir}")
    print(f"rows: {len(uncertainty_df)}")
    print(f"mean_prediction_std: {summary['global']['mean_prediction_std']:.4f}")
    print(f"tree_interval_90_coverage: {summary['global']['tree_interval_90_coverage']:.4f}")
    print(
        "uncertainty_vs_absolute_error_pearson: "
        f"{summary['global']['uncertainty_vs_absolute_error_pearson']}"
    )


if __name__ == "__main__":
    main()
